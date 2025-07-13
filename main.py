# main.py
import json
import uuid
from datetime import datetime
from typing import List
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks, status, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import ApiTrackingLog
from background_processor import process_invoice_task
from validators import FileValidator
from config import settings
from datetime import datetime

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para extracción automática de datos de facturas usando Google Gemini AI"
)

# Configurar CORS para permitir el acceso desde el cliente .NET
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar templates para la interfaz web
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos si se necesitan
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # Directorio static no existe aún

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Endpoint para iniciar la extracción (múltiples archivos)
@app.post("/api/v1/invoices/extract", status_code=status.HTTP_202_ACCEPTED)
async def extract_invoice_data(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    user_identifier: str = Form(default="default_user"),
    session: Session = Depends(get_session)
):
    """
    Procesa uno o múltiples archivos de facturas y devuelve una lista de task_ids.
    
    - **files**: Lista de archivos (PDF, JPG, PNG) a procesar
    - **user_identifier**: Identificador del usuario que hace la solicitud
    
    Returns:
        - **task_ids**: Lista de identificadores de tareas para seguimiento
        - **message**: Mensaje de confirmación
    """
    # Validar archivos
    validated_files = await FileValidator.validate_files(files)
    
    task_ids = []
    
    for filename, content in validated_files:
        # Crear la entrada de registro inicial en la BD
        log_entry = ApiTrackingLog(
            user_identifier=user_identifier,
            status="PENDING",
            filename=filename
        )
        session.add(log_entry)
        session.commit()
        session.refresh(log_entry)
        
        # Añadir la tarea de procesamiento al fondo
        background_tasks.add_task(
            process_invoice_task,
            log_entry.task_id,
            content,
            user_identifier,
            filename
        )
        
        task_ids.append(log_entry.task_id)
    
    # Devolver los task_ids para que el cliente pueda consultar el estado
    return {
        "task_ids": task_ids,
        "message": f"Lote de {len(validated_files)} facturas enviado a procesar.",
        "total_files": len(validated_files)
    }

# Endpoint para consultar el estado de la tarea
@app.get("/api/v1/invoices/status/{task_id}")
async def get_task_status(task_id: uuid.UUID, session: Session = Depends(get_session)):
    """
    Consulta el estado de una tarea específica.
    
    - **task_id**: UUID de la tarea a consultar
    
    Returns:
        - **task_id**: ID de la tarea
        - **status**: Estado actual de la tarea
        - **data**: Datos extraídos (solo si está completada)
        - **error**: Mensaje de error (solo si falló)
    """
    # Buscar por task_id en lugar de id
    statement = select(ApiTrackingLog).where(ApiTrackingLog.task_id == task_id)
    log_entry = session.exec(statement).first()
    
    if not log_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    response = {
        "task_id": log_entry.task_id,
        "status": log_entry.status,
        "filename": log_entry.filename,
        "user_identifier": log_entry.user_identifier,
        "created_at": log_entry.request_utc_timestamp.isoformat(),
        "completed_at": log_entry.completion_utc_timestamp.isoformat() if log_entry.completion_utc_timestamp else None
    }
    
    if log_entry.status == "COMPLETED" and log_entry.final_json_response:
        try:
            response["data"] = json.loads(log_entry.final_json_response)
        except json.JSONDecodeError:
            response["data"] = log_entry.final_json_response
        
        # Agregar información de tokens si está disponible
        if log_entry.total_tokens:
            response["tokens_used"] = log_entry.total_tokens
            
    elif log_entry.status == "FAILED":
        response["error"] = log_entry.error_message
        
    return response

# Endpoint para consultar el estado de múltiples tareas
@app.get("/api/v1/invoices/batch-status")
async def get_batch_status(
    task_ids: str,  # Lista de task_ids separados por comas
    session: Session = Depends(get_session)
):
    """
    Consulta el estado de múltiples tareas usando una lista de task_ids separados por comas.
    """
    try:
        task_id_list = [uuid.UUID(task_id.strip()) for task_id in task_ids.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de task_id inválido"
        )
    
    results = []
    for task_id in task_id_list:
        # Usar select con where en lugar de session.get()
        statement = select(ApiTrackingLog).where(ApiTrackingLog.task_id == task_id)
        log_entry = session.exec(statement).first()
        
        if not log_entry:
            results.append({
                "task_id": task_id,
                "status": "NOT_FOUND",
                "error": "Task not found"
            })
        else:
            result = {
                "task_id": log_entry.task_id,
                "status": log_entry.status,
                "filename": log_entry.filename
            }
            
            if log_entry.status == "COMPLETED" and log_entry.final_json_response:
                try:
                    result["data"] = json.loads(log_entry.final_json_response)
                except json.JSONDecodeError:
                    result["data"] = log_entry.final_json_response
            elif log_entry.status == "FAILED":
                result["error"] = log_entry.error_message
                
            results.append(result)
    
    return {"results": results}

# Interfaz web de administración
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session: Session = Depends(get_session)):
    """
    Interfaz web para monitorear el estado de todas las facturas.
    """
    # Obtener todas las entradas de seguimiento
    statement = select(ApiTrackingLog).order_by(ApiTrackingLog.request_utc_timestamp.desc())
    logs = session.exec(statement).all()
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "logs": logs,
        "title": "Dashboard de Administración - Extracción de Facturas"
    })

# API para la interfaz web (obtener datos en JSON)
@app.get("/api/v1/admin/logs")
async def get_admin_logs(
    status_filter: str = None,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    API para obtener los logs de procesamiento con filtros opcionales.
    """
    statement = select(ApiTrackingLog)
    
    if status_filter:
        statement = statement.where(ApiTrackingLog.status == status_filter)
    
    statement = statement.order_by(ApiTrackingLog.request_utc_timestamp.desc()).limit(limit)
    
    logs = session.exec(statement).all()
    
    return {
        "logs": [
            {
                "task_id": str(log.task_id),
                "filename": log.filename,
                "user_identifier": log.user_identifier,
                "status": log.status,
                "request_timestamp": log.request_utc_timestamp.isoformat(),
                "completion_timestamp": log.completion_utc_timestamp.isoformat() if log.completion_utc_timestamp else None,
                "total_tokens": log.total_tokens,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }

# Endpoint para obtener estadísticas
@app.get("/api/v1/admin/stats")
async def get_admin_stats(session: Session = Depends(get_session)):
    """
    Obtiene estadísticas de uso del sistema.
    """
    from sqlmodel import func
    
    # Contar por estado
    pending_count = session.exec(select(func.count(ApiTrackingLog.id)).where(ApiTrackingLog.status == "PENDING")).first()
    processing_count = session.exec(select(func.count(ApiTrackingLog.id)).where(ApiTrackingLog.status == "PROCESSING")).first()
    completed_count = session.exec(select(func.count(ApiTrackingLog.id)).where(ApiTrackingLog.status == "COMPLETED")).first()
    failed_count = session.exec(select(func.count(ApiTrackingLog.id)).where(ApiTrackingLog.status == "FAILED")).first()
    
    # Total de tokens utilizados
    total_tokens = session.exec(select(func.sum(ApiTrackingLog.total_tokens))).first() or 0
    
    return {
        "pending": pending_count or 0,
        "processing": processing_count or 0,
        "completed": completed_count or 0,
        "failed": failed_count or 0,
        "total_tokens_used": total_tokens
    }

# Endpoint para obtener información del sistema
@app.get("/api/v1/system/info")
async def get_system_info():
    """
    Obtiene información del sistema y configuración.
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "max_file_size_mb": settings.max_file_size_mb,
        "allowed_extensions": settings.allowed_extensions,
        "gemini_configured": bool(settings.gemini_api_key),
        "database_url": settings.database_url.replace("sqlite:///", "").replace("./", ""),
        "status": "operational"
    }

# Endpoint para validar configuración
@app.get("/api/v1/system/health")
async def health_check(session: Session = Depends(get_session)):
    """
    Endpoint de health check para verificar el estado del sistema.
    """
    try:
        # Verificar base de datos
        session.exec(select(ApiTrackingLog).limit(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "gemini_api": "configured" if settings.gemini_api_key else "not configured",
        "timestamp": datetime.utcnow().isoformat()
    }

# Endpoint raíz con información básica
@app.get("/")
async def root():
    """
    Endpoint raíz con información básica de la API.
    """
    return {
        "message": "API de Extracción de Facturas con IA",
        "version": settings.app_version,
        "documentation": "/docs",
        "admin_panel": "/admin",
        "health_check": "/api/v1/system/health"
    }
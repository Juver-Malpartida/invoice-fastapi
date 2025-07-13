# background_processor.py
import json
import uuid
from datetime import datetime
from sqlmodel import Session, select
from models import ApiTrackingLog
from database import engine
from convert_toimage import convert_pdf_to_images
from gedata import get_invoice_data_from_gemini 


async def process_invoice_task(task_id: uuid.UUID, file_bytes: bytes, user_identifier: str, filename: str):
    """
    Procesa una factura individual en segundo plano.
    """
    print(f"Iniciando procesamiento de tarea {task_id} para archivo {filename}")
    
    # 1. Actualizar estado a PROCESSING en la BD
    with Session(engine) as session:
        statement = select(ApiTrackingLog).where(ApiTrackingLog.task_id == task_id)
        log_entry = session.exec(statement).first()
        if not log_entry:
            print(f"ERROR: Tarea {task_id} no encontrada en la base de datos")
            return
        log_entry.status = "PROCESSING"
        session.add(log_entry)
        session.commit()

    try:
        # 2. Pre-procesar archivo a imágenes
        if filename.lower().endswith('.pdf'):
            images = convert_pdf_to_images(file_bytes)
        else:
            # Para imágenes JPG/PNG, usar directamente
            images = [file_bytes]
        
        if not images:
            raise Exception("Error converting file to image format")

        # 3. Llamar a Gemini
        with open("promp.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        
        gemini_result = await get_invoice_data_from_gemini(prompt, images)

        # 4. Actualizar la BD con el resultado final
        with Session(engine) as session:
            statement = select(ApiTrackingLog).where(ApiTrackingLog.task_id == task_id)
            log_entry = session.exec(statement).first()
            if not log_entry:
                print(f"ERROR: Tarea {task_id} no encontrada para actualizar resultado")
                return
                
            if "error" in gemini_result:
                log_entry.status = "FAILED"
                log_entry.error_message = str(gemini_result["error"])
            else:
                log_entry.status = "COMPLETED"
                log_entry.final_json_response = gemini_result["json_text"]
                log_entry.prompt_tokens = gemini_result["usage"]["prompt_tokens"]
                log_entry.completion_tokens = gemini_result["usage"]["completion_tokens"]
                log_entry.total_tokens = gemini_result["usage"]["total_tokens"]
                
            log_entry.completion_utc_timestamp = datetime.utcnow()
            session.add(log_entry)
            session.commit()
            
        print(f"Tarea {task_id} completada exitosamente")
        
    except Exception as e:
        print(f"ERROR procesando tarea {task_id}: {str(e)}")
        # Marcar como fallida en caso de error
        with Session(engine) as session:
            statement = select(ApiTrackingLog).where(ApiTrackingLog.task_id == task_id)
            log_entry = session.exec(statement).first()
            if log_entry:
                log_entry.status = "FAILED"
                log_entry.error_message = str(e)
                log_entry.completion_utc_timestamp = datetime.utcnow()
                session.add(log_entry)
                session.commit()
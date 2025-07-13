# validators.py
import mimetypes
from typing import List
from fastapi import UploadFile, HTTPException, status
from config import settings

class FileValidator:
    """
    Validador de archivos para la API
    """
    
    ALLOWED_MIME_TYPES = {
        "application/pdf": ["pdf"],
        "image/jpeg": ["jpg", "jpeg"],
        "image/png": ["png"],
        "image/jpg": ["jpg"]  # Some browsers send this
    }
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Valida un archivo individual
        """
        # Verificar tipo MIME
        if file.content_type not in FileValidator.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido: {file.content_type}. "
                       f"Tipos permitidos: {list(FileValidator.ALLOWED_MIME_TYPES.keys())}"
            )
        
        # Verificar extensión del archivo
        if file.filename:
            extension = file.filename.split('.')[-1].lower()
            allowed_extensions = FileValidator.ALLOWED_MIME_TYPES.get(file.content_type, [])
            
            if extension not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Extensión de archivo no válida: .{extension}. "
                           f"Extensiones permitidas para {file.content_type}: {allowed_extensions}"
                )
    
    @staticmethod
    async def validate_file_size(file: UploadFile) -> bytes:
        """
        Valida el tamaño del archivo y devuelve los bytes
        """
        content = await file.read()
        max_size = settings.max_file_size_mb * 1024 * 1024
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo {file.filename} excede el tamaño máximo de {settings.max_file_size_mb}MB"
            )
        
        return content
    
    @staticmethod
    async def validate_files(files: List[UploadFile]) -> List[tuple]:
        """
        Valida múltiples archivos y devuelve una lista de (filename, content)
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron archivos"
            )
        
        if len(files) > 10:  # Límite de archivos por lote
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 10 archivos por lote"
            )
        
        validated_files = []
        
        for file in files:
            FileValidator.validate_file(file)
            content = await FileValidator.validate_file_size(file)
            validated_files.append((file.filename or "unknown", content))
        
        return validated_files

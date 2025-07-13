# config.py
import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic BaseSettings
    """
    # API Configuration
    app_name: str = "Invoice Extraction API"
    app_version: str = "1.0.0"
    
    # Gemini API
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    
    # Database
    database_url: str = Field(default="sqlite:///./invoices.db", alias="DATABASE_URL")
    
    # Server
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # File Processing
    max_file_size_mb: int = Field(default=10, alias="MAX_FILE_SIZE_MB")
    
    # Processing
    max_concurrent_tasks: int = Field(default=5, alias="MAX_CONCURRENT_TASKS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Obtiene las extensiones permitidas desde variable de entorno o valor por defecto"""
        env_extensions = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png")
        return [ext.strip() for ext in env_extensions.split(',') if ext.strip()]

# Instancia global de configuración
settings = Settings()

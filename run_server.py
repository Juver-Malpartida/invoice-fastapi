#!/usr/bin/env python3
"""
Script para ejecutar el servidor de desarrollo de FastAPI
"""

import sys
import uvicorn
from config import settings

def main():
    """Función principal para ejecutar el servidor"""
    
    print(f"🚀 Iniciando servidor de extracción de facturas...")
    print(f"📍 URL: http://{settings.host}:{settings.port}")
    print(f"📊 Panel de administración: http://{settings.host}:{settings.port}/admin")
    print(f"📚 Documentación API: http://{settings.host}:{settings.port}/docs")
    
    # Verificar que la API key esté configurada
    if not settings.gemini_api_key:
        print("⚠️  ADVERTENCIA: GEMINI_API_KEY no está configurada")
        print("   Por favor, configura tu API key en el archivo .env")
        print("   El procesamiento de facturas fallará sin la API key")
        print()
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=True,
            reload_dirs=["./"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

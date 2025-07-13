#!/usr/bin/env python3
"""
Script de prueba para la API de extracción de facturas
"""

import requests
import json
import time
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")  # Directorio con archivos de prueba

def test_system_health():
    """Probar el health check del sistema"""
    print("🔍 Probando health check del sistema...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/system/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📊 Respuesta: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_system_info():
    """Probar información del sistema"""
    print("\n🔍 Probando información del sistema...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/system/info")
        print(f"✅ Info del sistema: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo info del sistema: {e}")
        return False

def test_file_upload():
    """Probar subida de archivos"""
    print("\n🔍 Probando subida de archivos...")
    
    # Crear un archivo de prueba simple si no existe
    if not TEST_FILES_DIR.exists():
        TEST_FILES_DIR.mkdir()
    
    # Crear archivo de prueba
    test_file = TEST_FILES_DIR / "test_invoice.txt"
    test_file.write_text("Esta es una factura de prueba\nTotal: 100.50€\nFecha: 2024-01-15")
    
    try:
        # Intentar subir archivo (esto debería fallar por el tipo de archivo)
        with open(test_file, 'rb') as f:
            files = {'files': ('test_invoice.txt', f, 'text/plain')}
            data = {'user_identifier': 'test_user'}
            response = requests.post(f"{API_BASE_URL}/api/v1/invoices/extract", files=files, data=data)
        
        print(f"📊 Respuesta: {response.status_code}")
        print(f"📊 Contenido: {response.text}")
        
        if response.status_code == 400:
            print("✅ Validación de archivos funciona correctamente (rechazó archivo de texto)")
            return True
        else:
            print("⚠️  Validación de archivos no funcionó como esperado")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en subida de archivos: {e}")
        return False

def test_task_status():
    """Probar consulta de estado de tarea inexistente"""
    print("\n🔍 Probando consulta de estado de tarea...")
    try:
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{API_BASE_URL}/api/v1/invoices/status/{fake_task_id}")
        print(f"📊 Respuesta: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Manejo de tareas inexistentes funciona correctamente")
            return True
        else:
            print(f"⚠️  Respuesta inesperada: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error consultando estado de tarea: {e}")
        return False

def test_admin_stats():
    """Probar estadísticas de administración"""
    print("\n🔍 Probando estadísticas de administración...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/admin/stats")
        print(f"✅ Estadísticas: {response.status_code}")
        print(f"📊 Respuesta: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de la API de extracción de facturas")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"✅ Servidor disponible en {API_BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ Servidor no disponible en {API_BASE_URL}")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python run_server.py")
        return
    
    # Ejecutar pruebas
    tests = [
        test_system_health,
        test_system_info,
        test_file_upload,
        test_task_status,
        test_admin_stats
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🧪 Resumen de pruebas:")
    print(f"✅ Pasadas: {passed}")
    print(f"❌ Fallidas: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print(f"⚠️  {failed} pruebas fallaron")
    
    # Limpiar archivos de prueba
    if TEST_FILES_DIR.exists():
        for file in TEST_FILES_DIR.iterdir():
            file.unlink()
        TEST_FILES_DIR.rmdir()

if __name__ == "__main__":
    main()

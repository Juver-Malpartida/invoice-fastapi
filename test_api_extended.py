#!/usr/bin/env python3
"""
Script de prueba completo para la API de extracción de facturas
Incluye pruebas con un PDF de ejemplo
"""

import requests
import json
import time
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")

def create_test_invoice_image():
    """Crear una imagen de factura de prueba"""
    # Crear imagen de 800x600 píxeles
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente del sistema
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        # Usar fuente por defecto si no se encuentra Arial
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Dibujar contenido de la factura
    draw.text((50, 50), "FACTURA", fill='black', font=font_large)
    draw.text((50, 100), "Número: FAC-2024-001", fill='black', font=font_medium)
    draw.text((50, 130), "Fecha: 15/01/2024", fill='black', font=font_medium)
    draw.text((50, 160), "Vencimiento: 15/02/2024", fill='black', font=font_medium)
    
    draw.text((50, 200), "Emisor:", fill='black', font=font_medium)
    draw.text((50, 230), "TechCorp Solutions S.L.", fill='black', font=font_small)
    draw.text((50, 250), "NIF: B12345678", fill='black', font=font_small)
    draw.text((50, 270), "Calle Ejemplo, 123", fill='black', font=font_small)
    draw.text((50, 290), "28001 Madrid", fill='black', font=font_small)
    
    draw.text((50, 330), "Cliente:", fill='black', font=font_medium)
    draw.text((50, 360), "Cliente Test S.A.", fill='black', font=font_small)
    draw.text((50, 380), "NIF: A87654321", fill='black', font=font_small)
    
    draw.text((50, 420), "Descripción:", fill='black', font=font_medium)
    draw.text((50, 450), "Servicios de consultoría tecnológica", fill='black', font=font_small)
    draw.text((50, 470), "Desarrollo de software personalizado", fill='black', font=font_small)
    
    draw.text((50, 510), "Subtotal: 1.000,00 €", fill='black', font=font_medium)
    draw.text((50, 530), "IVA (21%): 210,00 €", fill='black', font=font_medium)
    draw.text((50, 550), "TOTAL: 1.210,00 €", fill='black', font=font_large)
    
    # Guardar imagen
    return img

def test_full_invoice_processing():
    """Probar el procesamiento completo de una factura"""
    print("\n🔍 Probando procesamiento completo de factura...")
    
    # Crear directorio de pruebas
    if not TEST_FILES_DIR.exists():
        TEST_FILES_DIR.mkdir()
    
    try:
        # Crear imagen de factura de prueba
        test_image = create_test_invoice_image()
        test_file = TEST_FILES_DIR / "factura_test.jpg"
        test_image.save(test_file, format='JPEG')
        
        print(f"✅ Imagen de prueba creada: {test_file}")
        
        # Subir archivo
        with open(test_file, 'rb') as f:
            files = {'files': ('factura_test.jpg', f, 'image/jpeg')}
            data = {'user_identifier': 'test_user'}
            response = requests.post(f"{API_BASE_URL}/api/v1/invoices/extract", 
                                    files=files, data=data)
        
        if response.status_code == 202:
            result = response.json()
            task_id = result['task_ids'][0]
            print(f"✅ Factura enviada. Task ID: {task_id}")
            
            # Monitorear estado
            max_wait = 60  # Máximo 60 segundos
            wait_time = 0
            
            while wait_time < max_wait:
                status_response = requests.get(f"{API_BASE_URL}/api/v1/invoices/status/{task_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Estado: {status_data['status']}")
                    
                    if status_data['status'] == 'COMPLETED':
                        print("✅ Procesamiento completado exitosamente")
                        if 'data' in status_data:
                            print(f"📋 Datos extraídos: {json.dumps(status_data['data'], indent=2)}")
                        if 'tokens_used' in status_data:
                            print(f"🔢 Tokens utilizados: {status_data['tokens_used']}")
                        return True
                    elif status_data['status'] == 'FAILED':
                        print(f"❌ Procesamiento falló: {status_data.get('error', 'Error desconocido')}")
                        return False
                    elif status_data['status'] in ['PENDING', 'PROCESSING']:
                        print(f"⏳ Esperando... ({status_data['status']})")
                        time.sleep(3)
                        wait_time += 3
                    else:
                        print(f"⚠️  Estado desconocido: {status_data['status']}")
                        return False
                else:
                    print(f"❌ Error consultando estado: {status_response.status_code}")
                    return False
            
            print("⏰ Timeout: El procesamiento tardó más de 60 segundos")
            return False
            
        else:
            print(f"❌ Error enviando factura: {response.status_code}")
            print(f"📊 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba completa: {e}")
        return False
    
    finally:
        # Limpiar archivos de prueba
        if TEST_FILES_DIR.exists():
            for file in TEST_FILES_DIR.iterdir():
                file.unlink()
            TEST_FILES_DIR.rmdir()

def test_batch_processing():
    """Probar procesamiento por lotes"""
    print("\n🔍 Probando procesamiento por lotes...")
    
    if not TEST_FILES_DIR.exists():
        TEST_FILES_DIR.mkdir()
    
    try:
        # Crear múltiples imágenes de prueba
        files_to_upload = []
        
        for i in range(3):
            test_image = create_test_invoice_image()
            test_file = TEST_FILES_DIR / f"factura_test_{i+1}.jpg"
            test_image.save(test_file, format='JPEG')
            files_to_upload.append(('files', (f'factura_test_{i+1}.jpg', open(test_file, 'rb'), 'image/jpeg')))
        
        # Subir archivos en lote
        data = {'user_identifier': 'batch_test_user'}
        response = requests.post(f"{API_BASE_URL}/api/v1/invoices/extract", 
                                files=files_to_upload, data=data)
        
        # Cerrar archivos
        for _, (_, file_obj, _) in files_to_upload:
            file_obj.close()
        
        if response.status_code == 202:
            result = response.json()
            task_ids = result['task_ids']
            print(f"✅ Lote enviado. {len(task_ids)} tareas creadas")
            
            # Consultar estado de todas las tareas
            task_ids_str = ','.join(str(tid) for tid in task_ids)
            batch_response = requests.get(f"{API_BASE_URL}/api/v1/invoices/batch-status?task_ids={task_ids_str}")
            
            if batch_response.status_code == 200:
                batch_data = batch_response.json()
                print(f"✅ Consulta por lotes exitosa")
                for result in batch_data['results']:
                    print(f"  - Task {str(result['task_id'])[:8]}...: {result['status']}")
                return True
            else:
                print(f"❌ Error en consulta por lotes: {batch_response.status_code}")
                return False
        else:
            print(f"❌ Error enviando lote: {response.status_code}")
            print(f"📊 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de lote: {e}")
        return False
    
    finally:
        # Limpiar archivos de prueba
        if TEST_FILES_DIR.exists():
            for file in TEST_FILES_DIR.iterdir():
                try:
                    file.unlink()
                except:
                    pass
            try:
                TEST_FILES_DIR.rmdir()
            except:
                pass

def test_admin_panel():
    """Probar el panel de administración"""
    print("\n🔍 Probando panel de administración...")
    
    try:
        # Probar estadísticas
        stats_response = requests.get(f"{API_BASE_URL}/api/v1/admin/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Estadísticas obtenidas:")
            print(f"  - Pendientes: {stats['pending']}")
            print(f"  - Procesando: {stats['processing']}")
            print(f"  - Completadas: {stats['completed']}")
            print(f"  - Fallidas: {stats['failed']}")
            print(f"  - Tokens totales: {stats['total_tokens_used']}")
            
            # Probar logs
            logs_response = requests.get(f"{API_BASE_URL}/api/v1/admin/logs?limit=5")
            if logs_response.status_code == 200:
                logs = logs_response.json()
                print(f"✅ Logs obtenidos: {len(logs['logs'])} entradas")
                return True
            else:
                print(f"❌ Error obteniendo logs: {logs_response.status_code}")
                return False
        else:
            print(f"❌ Error obteniendo estadísticas: {stats_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de admin: {e}")
        return False

def main():
    """Función principal de pruebas extendidas"""
    print("🧪 Iniciando pruebas extendidas de la API de extracción de facturas")
    print("=" * 80)
    
    # Verificar que el servidor esté disponible
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
        ("🔋 Prueba básica de sistema", lambda: requests.get(f"{API_BASE_URL}/api/v1/system/health").status_code == 200),
        ("🖼️ Procesamiento de imagen", test_full_invoice_processing),
        ("📦 Procesamiento por lotes", test_batch_processing),
        ("📊 Panel de administración", test_admin_panel),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 50)
        try:
            if test_func():
                print(f"✅ {test_name}: PASÓ")
                passed += 1
            else:
                print(f"❌ {test_name}: FALLÓ")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"🧪 Resumen de pruebas extendidas:")
    print(f"✅ Pasadas: {passed}")
    print(f"❌ Fallidas: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ¡Todas las pruebas extendidas pasaron exitosamente!")
        print("🚀 La API está lista para uso en producción")
    else:
        print(f"⚠️  {failed} pruebas fallaron")
        print("💡 Revisa los logs del servidor para más detalles")

if __name__ == "__main__":
    main()

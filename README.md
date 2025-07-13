# API de Extracción de Facturas con IA

Una API REST desarrollada con FastAPI para extraer datos de facturas en formato PDF, JPG y PNG.

## 🚀 Características

- ✅ **Procesamiento por lotes**: Sube múltiples facturas a la vez
- ✅ **Procesamiento asíncrono**: Las tareas se procesan en segundo plano
- ✅ **Múltiples formatos**: Soporte para PDF, JPG y PNG
- ✅ **Interfaz de administración**: Panel web para monitorear el procesamiento
- ✅ **Base de datos**: Seguimiento completo de todas las operaciones
- ✅ **API RESTful**: Endpoints bien documentados

## 🛠️ Instalación

### Prerrequisitos

- Python 3.9 o superior
- API Key de Google Gemini

### Pasos de instalación

1. **Clonar el repositorio o descargar los archivos**

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:

```bash
# En Windows PowerShell
$env:GOOGLE_API_KEY="tu_api_key_aquí"

# O crear archivo .env
echo "GOOGLE_API_KEY=tu_api_key_aquí" > .env
```

**Obtener API Key:**

- Visita https://makersuite.google.com/app/apikey
- Genera una nueva API key de Google AI Studio

4. **Ejecutar el servidor**:

```bash
python run_server.py
```

## 📚 Uso de la API

### Endpoints Principales

#### 1. Extraer datos de facturas (Procesamiento por lotes)

```http
POST /api/v1/invoices/extract
Content-Type: multipart/form-data

files: [archivo1.pdf, archivo2.jpg, archivo3.png]
user_identifier: "usuario_ejemplo"
```

**Respuesta:**

```json
{
  "task_ids": ["uuid1", "uuid2", "uuid3"],
  "message": "Lote de 3 facturas enviado a procesar."
}
```

#### 2. Consultar estado de una tarea

```http
GET /api/v1/invoices/status/{task_id}
```

**Respuesta:**

```json
{
  "task_id": "uuid",
  "status": "COMPLETED",
  "data": {
    "invoice_id": "FAC-2024-001",
    "issuer_name": "Empresa Ejemplo S.L.",
    "total_amount": 1250.5,
    "issue_date": "2024-01-15",
    "due_date": "2024-02-15",
    "tax_id": "B12345678"
  }
}
```

#### 3. Consultar estado de múltiples tareas

```http
GET /api/v1/invoices/batch-status?task_ids=uuid1,uuid2,uuid3
```

### Estados de las tareas

- **PENDING**: La tarea está en cola esperando procesamiento
- **PROCESSING**: La tarea se está procesando actualmente
- **COMPLETED**: La tarea se completó exitosamente
- **FAILED**: La tarea falló durante el procesamiento

## 🎛️ Panel de Administración

Accede al panel de administración web en: `http://localhost:8000/admin`

### Características del panel:

- 📊 **Estadísticas en tiempo real**: Contador de tareas por estado
- 📋 **Lista de todas las tareas**: Con filtros y búsqueda
- 🔄 **Auto-refresh**: Actualización automática cada 30 segundos
- 📥 **Exportación**: Descarga los datos en formato CSV
- 🎨 **Interfaz moderna**: Diseño responsive y fácil de usar

## 🔧 Configuración

### Variables de entorno (.env)

```env
# API Key de Google Gemini (OBLIGATORIO)
GEMINI_API_KEY=tu_api_key_aqui

# Configuración de la base de datos
DATABASE_URL=sqlite:///./invoices.db

# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración de archivos
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png
```

### Personalización del prompt

El prompt que se envía a Gemini se encuentra en el archivo `promp.txt`. Puedes modificarlo para ajustar el comportamiento de la extracción según tus necesidades.

## 📁 Estructura del proyecto

```
invoice-fastapi/
├── main.py                    # Aplicación principal FastAPI
├── models.py                  # Modelos de base de datos
├── database.py                # Configuración de base de datos
├── background_processor.py    # Procesamiento asíncrono
├── gedata.py                  # Integración con Gemini
├── convert_toimage.py         # Conversión PDF a imagen
├── config.py                  # Configuración centralizada
├── validators.py              # Validación de archivos
├── promp.txt                  # Prompt para Gemini
├── requirements.txt           # Dependencias Python
├── run_server.py              # Script para ejecutar el servidor
├── test_api.py                # Pruebas básicas de la API
├── test_api_extended.py       # Pruebas extendidas con procesamiento
├── .env.example              # Ejemplo de variables de entorno
├── .env                      # Variables de entorno (no incluir en git)
├── .gitignore                # Archivos a ignorar en git
├── Dockerfile                # Configuración para Docker
├── docker-compose.yml        # Orquestación Docker
├── templates/                # Templates HTML
│   └── admin_dashboard.html  # Panel de administración
└── invoices.db              # Base de datos SQLite (se crea automáticamente)
```

## 🧪 Pruebas

### Pruebas automáticas

```bash
# Pruebas básicas de la API
python test_api.py

# Pruebas extendidas con procesamiento de imágenes
python test_api_extended.py
```

### Usando cURL

```bash
# Enviar una factura
curl -X POST "http://localhost:8000/api/v1/invoices/extract" \
  -F "files=@factura1.pdf" \
  -F "files=@factura2.jpg" \
  -F "user_identifier=test_user"

# Consultar estado individual
curl "http://localhost:8000/api/v1/invoices/status/TASK_ID"

# Consultar estado de múltiples tareas
curl "http://localhost:8000/api/v1/invoices/batch-status?task_ids=uuid1,uuid2,uuid3"
```

### Usando Python

```python
import requests

# Enviar facturas
files = [
    ('files', open('factura1.pdf', 'rb')),
    ('files', open('factura2.jpg', 'rb'))
]
data = {'user_identifier': 'test_user'}

response = requests.post('http://localhost:8000/api/v1/invoices/extract',
                        files=files, data=data)
print(response.json())

# Consultar estado individual
task_id = response.json()['task_ids'][0]
status = requests.get(f'http://localhost:8000/api/v1/invoices/status/{task_id}')
print(status.json())

# Consultar estado de múltiples tareas
task_ids_str = ','.join(response.json()['task_ids'])
batch_status = requests.get(f'http://localhost:8000/api/v1/invoices/batch-status?task_ids={task_ids_str}')
print(batch_status.json())
```

## 📖 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a la documentación interactiva:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔒 Seguridad

- ✅ La API key de Gemini se almacena de forma segura en variables de entorno
- ✅ Validación de tipos de archivo permitidos
- ✅ Límites de tamaño de archivo
- ✅ Manejo de errores robusto

## 🚨 Consideraciones de Producción

Esta implementación es adecuada para una **Prueba de Concepto (PoC)**. Para producción, considera:

- 🔐 **Autenticación**: Implementar OAuth 2.0 o JWT
- 💾 **Base de datos**: Migrar a PostgreSQL o SQL Server
- 🌐 **Escalabilidad**: Usar Redis + Celery para colas de tareas
- 📊 **Monitoreo**: Agregar métricas y logging avanzado
- 🔒 **Seguridad**: HTTPS, rate limiting, validación de entrada

## 🐛 Solución de Problemas

### Error: "GEMINI_API_KEY no está configurada"

- Verifica que el archivo `.env` existe y contiene la API key
- Asegúrate de que la API key es válida

### Error: "Error converting PDF to image"

- Verifica que el archivo PDF no esté corrupto
- Comprueba que PyMuPDF está instalado correctamente

### Error: "Task not found"

- Verifica que el task_id es correcto
- Comprueba que la base de datos está funcionando

## 📞 Soporte

Para problemas o preguntas, revisa:

1. Los logs del servidor
2. El panel de administración para ver el estado de las tareas
3. La documentación de la API en `/docs`

## 🏗️ Desarrollo

### Ejecutar en modo desarrollo

```bash
python run_server.py
```

El servidor se ejecutará con recarga automática habilitada.

### Estructura de datos extraídos

La API extrae los siguientes campos de las facturas:

```json
{
  "invoice_id": "Número de factura",
  "issuer_name": "Nombre del emisor",
  "issuer_tax_id": "NIF/CIF del emisor",
  "recipient_name": "Nombre del cliente/receptor",
  "recipient_tax_id": "NIF/CIF del cliente",
  "issue_date": "Fecha de emisión",
  "due_date": "Fecha de vencimiento",
  "total_amount": "Importe total",
  "tax_amount": "Importe de impuestos",
  "currency": "Moneda",
  "line_items": [
    {
      "description": "Descripción del producto/servicio",
      "quantity": "Cantidad",
      "unit_price": "Precio unitario",
      "total_price": "Precio total"
    }
  ]
}
```

### Ejemplo de respuesta real

Basado en las pruebas exitosas, aquí tienes un ejemplo de datos extraídos:

```json
{
  "invoice_id": "FAC-2024-001",
  "issuer_name": "TechCorp Solutions S.L.",
  "issuer_tax_id": "B12345678",
  "recipient_name": "Cliente Test S.A.",
  "recipient_tax_id": "A87654321",
  "issue_date": "2024-01-15",
  "due_date": "2024-02-15",
  "total_amount": 1210.0,
  "tax_amount": 210.0,
  "currency": "EUR",
  "line_items": [
    {
      "description": "Servicios de consultoría tecnológica",
      "quantity": null,
      "unit_price": null,
      "total_price": null
    },
    {
      "description": "Desarrollo de software personalizado",
      "quantity": null,
      "unit_price": null,
      "total_price": null
    }
  ]
}
```

## 🐳 Despliegue con Docker

### Construcción y ejecución

```bash
# Construir la imagen
docker build -t invoice-api .

# Ejecutar con variable de entorno
docker run -e GOOGLE_API_KEY="tu_api_key_aquí" -p 8000:8000 invoice-api
```

### Docker Compose

```yaml
version: "3.8"
services:
  invoice-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=tu_api_key_aquí
```

## 🔧 Configuración Avanzada

### Variables de entorno disponibles

```bash
GOOGLE_API_KEY=tu_api_key_aquí      # Requerido
DATABASE_URL=sqlite:///./tasks.db    # Opcional
ALLOWED_EXTENSIONS=pdf,jpg,png       # Opcional
MAX_FILE_SIZE=10485760              # Opcional (10MB)
```

## 📊 Monitoreo y Logs

### Endpoints de diagnóstico

```bash
# Estado de la aplicación
curl http://localhost:8000/health

# Información del sistema
curl http://localhost:8000/info

# Estadísticas de procesamiento
curl http://localhost:8000/admin
```

### Logs del sistema

Los logs se muestran en la consola del servidor e incluyen:

- Procesamiento de archivos
- Errores de la API de Gemini
- Estadísticas de tokens utilizados
- Tiempo de procesamiento

## 🧪 Pruebas y Validación

### Pruebas automatizadas

```bash
# Pruebas básicas
python test_api.py

# Pruebas extendidas con imágenes sintéticas
python test_api_extended.py
```

### Métricas de rendimiento

Basado en las pruebas exitosas:

- **Tiempo de procesamiento**: ~3-5 segundos por factura
- **Uso de tokens**: ~1,113 tokens por imagen
- **Tasa de éxito**: 100% en pruebas automatizadas
- **Formatos soportados**: PDF, JPG, PNG

## 🔍 Solución de Problemas

### Errores comunes

**Error: Google API Key no configurada**

```bash
# Verificar configuración
echo $env:GOOGLE_API_KEY  # PowerShell
echo $GOOGLE_API_KEY      # Linux/Mac
```

**Error: Dependencias no instaladas**

```bash
pip install -r requirements.txt
```

**Error: Puerto 8000 en uso**

```bash
# Cambiar puerto
python run_server.py --port 8001
```

## 🏗️ Arquitectura del Proyecto

```
invoice-fastapi/
├── main.py                 # Aplicación FastAPI principal
├── models.py              # Modelos de base de datos
├── config.py              # Configuración y settings
├── background_processor.py # Procesamiento asíncrono
├── validators.py          # Validación de archivos
├── run_server.py          # Punto de entrada
├── requirements.txt       # Dependencias
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación Docker
├── test_api.py           # Pruebas básicas
├── test_api_extended.py  # Pruebas avanzadas
├── tasks.db              # Base de datos SQLite
└── templates/
    └── admin_dashboard.html  # Panel de administración
```

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) por el excelente framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) por la API de IA
- [SQLModel](https://sqlmodel.tiangolo.com/) por el ORM type-safe

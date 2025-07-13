# Documento de Requisitos de Producto (PRD)
## Extracción Inteligente de Datos de Facturas con IA

**Versión:** 1.2 (Versión Consolidada)
**Fecha:** 2025-07-12
**Autor:** Gemini Architect
**Estado:** Final para PoC

---

### **Nota Importante sobre la Estrategia Técnica**
Este documento se basa en la premisa original de utilizar la **API de Google Gemini** como motor de extracción de datos. La historia de usuario **HU01** del documento `UserStories.docx` proponía una estrategia técnica alternativa (Tesseract OCR + LayoutLM) que representa un desarrollo a medida y entra en conflicto directo con el uso de un LLM como servicio. Para esta versión del PRD, **se mantiene el enfoque de Gemini** por ser más rápido de implementar para una PoC y alinearse con la solicitud inicial.

---

## 1. Visión General y Objetivos

### 1.1. Problema
Los operadores del ERP actualmente invierten una cantidad significativa de tiempo y esfuerzo manual en la transcripción de datos desde facturas en formato PDF, JPG o PNG hacia los campos correspondientes en el sistema. Este proceso es repetitivo, propenso a errores humanos y genera un cuello de botella en el departamento de cuentas por pagar.

### 1.2. Solución Propuesta
Desarrollaremos una solución que integra el poder del LLM de Google, Gemini, para automatizar la extracción de datos de facturas. La solución consistirá en una nueva funcionalidad en el cliente ERP de escritorio (.NET) que permitirá a los usuarios cargar **una o varias facturas (en lote)**. Estos archivos serán procesados por una API intermedia (Python/FastAPI) que orquestará la comunicación con Gemini. El proceso será asíncrono. Adicionalmente, se propone una **interfaz web de administración** para el monitoreo y gestión del proceso.

### 1.3. Objetivos del Proyecto (PoC)
* **Validar la Viabilidad:** Demostrar que Gemini puede extraer datos clave de facturas con alta precisión y devolverlos en un formato JSON estructurado y predecible.
* **Reducir el Tiempo de Procesamiento:** Disminuir drásticamente el tiempo que un usuario dedica a la entrada de datos, especialmente al procesar facturas en lote.
* **Mejorar la Experiencia de Usuario:** Transformar una tarea manual en un proceso de carga simple y una revisión rápida.
* **Establecer una Arquitectura Escalable:** Crear una base técnica que sea segura, mantenible y que pueda evolucionar hacia una solución de producción completa.

## 2. Personas de Usuario

* **Clara "La Contable" (Operadora de Cuentas por Pagar):**
    * **Rol:** Responsable de recibir e ingresar facturas de proveedores en el ERP.
    * **Metas:** Procesar las facturas de manera rápida y precisa.
    * **Frustraciones:** La entrada de datos manual, los errores tipográficos y el tiempo perdido.
* **Andrés "El Administrador" (Supervisor/Admin TI):**
    * **Rol:** Responsable de supervisar la operación, asegurar que los procesos se completen y solucionar problemas.
    * **Metas:** Tener visibilidad del estado de todas las facturas procesadas, generar reportes y configurar el sistema.
    * **Frustraciones:** Falta de visibilidad sobre procesos automatizados, dificultad para rastrear errores.

## 3. Requisitos y User Stories

### 3.1. Frontend: Cliente de Escritorio .NET (ERP)

| User Story | Criterios de Aceptación |
| :--- | :--- |
| **F-1: Como Clara, quiero poder seleccionar y cargar una o varias facturas (en lote) desde mi ordenador para que el sistema pueda extraer sus datos.** | 1. La interfaz del ERP debe mostrar un nuevo botón "Cargar Factura(s) con IA".<br>2. Al hacer clic, se debe abrir el explorador de archivos, permitiendo la **selección múltiple** de archivos.<br>3. El explorador debe estar filtrado para aceptar formatos `.pdf`, `.jpg`, y `.png`.<br>4. Tras la selección, la aplicación debe iniciar la carga de los archivos a la API de backend sin bloquear la UI. |
| **F-2: Como Clara, quiero ver una indicación visual de que las facturas se están procesando.** | 1. Debe aparecer una notificación no bloqueante: "Lote de [N] facturas enviado a procesar."<br>2. En la lista de facturas, las nuevas entradas deben mostrar un estado visual claro como "Procesando...". |
| **F-3: Como Clara, quiero recibir una notificación cuando los datos de una factura estén listos.** | 1. La aplicación debe mostrar una notificación: "Los datos de la factura [Nombre del Archivo] están listos para su revisión."<br>2. El estado de la factura en la lista debe cambiar a "Listo para Revisión". |
| **F-4: Como Clara, quiero ver los datos extraídos para poder verificarlos y validarlos.** | 1. Al seleccionar una factura "Lista para Revisión", la UI debe mostrar los datos extraídos en campos editables junto a una vista previa de la factura.<br>2. Debe haber un botón de "Confirmar y Guardar" y otro de "Rechazar". |
| **F-5: Como Clara, si la extracción falla, quiero ver un mensaje de error claro.** | 1. La notificación debe indicar el error: "Error al procesar la factura [Nombre del Archivo]."<br>2. El estado de la factura en la lista debe cambiar a "Error".<br>3. Al seleccionar la factura, se debe mostrar el mensaje de error devuelto por la API. |

### 3.2. Backend: API Intermedia (Python/FastAPI)

| User Story | Criterios de Aceptación |
| :--- | :--- |
| **B-1: Como sistema, necesito un endpoint para recibir una o múltiples facturas (PDF, JPG, PNG) y un identificador de usuario, para iniciar el proceso de extracción.** | 1. Debe existir un endpoint `POST /api/v1/invoices/extract`.<br>2. El endpoint debe aceptar `multipart/form-data` con **una lista de archivos**.<br>3. Debe validar que los archivos sean de tipo `application/pdf`, `image/jpeg`, o `image/png`.<br>4. Debe validar un tamaño máximo por archivo (ej. 10MB). |
| **B-2: Como sistema, al recibir una solicitud, necesito crear entradas de seguimiento y lanzar las tareas en segundo plano.** | 1. Por cada archivo en el lote, se debe generar un `task_id` único.<br>2. Por cada archivo, se debe crear una fila en `ApiTrackingLog` con estado `PENDING`.<br>3. La lógica de procesamiento para cada archivo debe ser añadida a una cola de tareas en segundo plano (`BackgroundTasks`).<br>4. El endpoint debe responder `HTTP 202 Accepted` con una lista de los `task_id` generados. |
| **B-3: Como sistema, necesito un endpoint para que el cliente pueda consultar el estado de una tarea.** | 1. Debe existir un endpoint `GET /api/v1/invoices/status/{task_id}`.<br>2. Si el `task_id` no existe, debe devolver `HTTP 404 Not Found`.<br>3. La respuesta debe contener el estado (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`) y el resultado o mensaje de error si aplica. |
| **B-4: Como sistema, en la tarea en segundo plano, necesito realizar la llamada a la API de Gemini para obtener los datos estructurados.** | 1. La tarea debe enviar la imagen (convertida desde el PDF si es necesario) y un prompt robusto a la API de Gemini.<br>2. La llamada a la API debe especificar `response_mime_type="application/json"` para forzar una salida JSON. |
| **B-5: Como sistema, necesito registrar el resultado y los datos de uso de tokens en la base de datos.** | 1. Tras recibir la respuesta de Gemini, la fila en `ApiTrackingLog` debe ser actualizada.<br>2. Si fue exitosa, el estado cambia a `COMPLETED` y se guardan `final_json_response`, `total_tokens`, etc.<br>3. Si falló, el estado cambia a `FAILED` y se guarda el `error_message`. |

### 3.3. Interfaz Web de Administración (Sugerencia para PoC)

| User Story | Criterios de Aceptación |
| :--- | :--- |
| **B-6: Como Andrés, necesito una interfaz web para monitorear el estado de todas las facturas que se están procesando, para tener control total sobre la operación.** | 1. La interfaz web debe mostrar una tabla con todas las facturas procesadas.<br>2. Las columnas deben incluir: `Task ID`, `Nombre de Archivo`, `Usuario`, `Fecha de Carga`, `Estado` (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`), y `Fecha de Finalización`.<br>3. La página debe tener una opción para refrescar los datos (o refrescarse automáticamente cada 30 segundos).<br>4. Debe haber filtros para buscar por `Estado` y por `Fecha`.<br>5. (Opcional para PoC) Un botón para exportar la vista actual a un archivo Excel/CSV. |

## 4. Consideraciones Técnicas (PoC)

* **Arquitectura General:** Patrón de 3 niveles (Cliente .NET -> API Python -> Gemini) con comunicación asíncrona mediante el patrón "Submit & Poll".
* **Cliente .NET:**
  * **Lenguaje:** C#
  * **Frameworks:** .NET Framework / .NET Core (según la versión del ERP existente), WinForms/WPF.
  * **Librerías Clave:** `HttpClient` para comunicación HTTP, `System.Text.Json` o `Newtonsoft.Json` para manejar el JSON.
* **Backend API:**
  * **Lenguaje:** Python 3.9+
  * **Framework:** FastAPI
  * **Servidor:** Uvicorn
  * **Librerías Clave:**
    * `google-generativeai`: SDK oficial para la API de Gemini.
    * `PyMuPDF` y `Pillow`: Para la conversión y manejo de PDF e imágenes.
    * `SQLModel` o `SQLAlchemy`: Para la definición del modelo de base de datos y la interacción con ella.
    * `python-dotenv`: Para la gestión de la API Key.
* **Interfaz Web de Administración (PoC):**
  * **Tecnología:** FastAPI sirviendo plantillas HTML con el motor **Jinja2**. Esto evita añadir un framework frontend complejo para la PoC.
* **Base de Datos (PoC):**
  * **Motor:** SQLite. Es una base de datos basada en archivos, simple y perfecta para una PoC, sin necesidad de un servidor dedicado.
* **Seguridad:**
  * La clave de la API de Gemini **DEBE** residir únicamente en el servidor de la API de backend y nunca debe ser expuesta al cliente .NET. Se cargará desde una variable de entorno.

## 5. Métricas de Éxito (KPIs)

* **Precisión de Extracción:** > 95% de precisión en los campos clave (Total, Fecha de Emisión, ID de Factura, NIF del Emisor) en un conjunto de 50 facturas de prueba de diferentes proveedores.
* **Tiempo de Procesamiento End-to-End:** El tiempo promedio desde que el usuario carga un PDF hasta que recibe la notificación de "Listo para Revisión" debe ser inferior a 25 segundos.
* **Tasa de Éxito del Proceso:** > 98% de las solicitudes deben finalizar con estado `COMPLETED`.
* **Reducción del Tiempo de Usuario:** El tiempo total que un usuario dedica a una factura (Carga + Revisión) debe ser al menos un 70% menor que el tiempo de entrada manual.

## 6. Fuera del Alcance (Para la v1.0 / PoC)

* **Notificaciones en Tiempo Real:** La comunicación se basará en sondeo (polling) por parte del cliente. No se implementarán WebSockets o SignalR en esta fase.
* **Ingesta Automática de Datos:** La solución presentará los datos para su revisión y aprobación manual. No se implementará la escritura automática de los datos en las tablas finales del ERP.
* **Sistema de Autenticación Robusto:** La API utilizará un identificador de usuario simple. No se implementará un flujo completo de OAuth 2.0.
* **Infraestructura de Producción:** No se configurarán colas de tareas robustas (Celery/Redis) ni bases de datos de producción (PostgreSQL/SQL Server). La PoC se ejecutará en un entorno de desarrollo.
* **Entrenamiento o Ajuste Fino del Modelo (Fine-Tuning):** Se utilizará el modelo base de Gemini (`gemini-1.5-flash`) sin ninguna personalización.
* **Modificación de Datos Post-Procesamiento:** La HU-08 que solicita un endpoint `PUT` para modificar datos ya extraídos queda fuera del alcance de esta PoC. La corrección se hará manualmente en el cliente .NET antes de guardar en el ERP.
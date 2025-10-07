# Explicación del Código del Backend - SembrandoBits

Este documento proporciona una explicación detallada del código del backend de la aplicación SembrandoBits, que es una API REST construida con Flask y MongoDB Atlas para gestionar sensores y medidas en un sistema de monitoreo agrícola.

## Estructura General del Backend

El backend está organizado en varios módulos Python que manejan diferentes aspectos de la aplicación:

- `database.py`: Manejo de la conexión a MongoDB Atlas
- `servidor.py`: Configuración principal del servidor Flask
- `sensores.py`: Endpoints para gestión de sensores
- `medidas.py`: Endpoints para gestión de medidas
- `requirements.txt`: Dependencias del proyecto

## 1. database.py - Conexión a la Base de Datos

Este módulo se encarga de establecer y gestionar la conexión con MongoDB Atlas, incluyendo reintentos y manejo de errores.

### Variables Globales y Configuración

```python
RETRY_ATTEMPTS = int(os.getenv("DB_RETRY_ATTEMPTS", "5"))  # Número de reintentos
RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "5"))        # Segundos entre reintentos
ALLOW_START_WITHOUT_DB = os.getenv("ALLOW_START_WITHOUT_DB", "1") == "1"  # Permitir inicio sin BD
```

Se cargan variables de entorno desde un archivo `.env` usando `python-dotenv`.

### Función `_intento_conectar(uri: str)`

Esta función privada intenta conectar a MongoDB de dos formas:
1. **Conexión TLS estándar**: Usa `mongodb+srv://` con TLS habilitado
2. **Conexión alternativa sin SSL**: Si la primera falla, intenta una conexión sin SSL modificando la URI

Parámetros de conexión:
- `server_api=ServerApi('1')`: Usa la API estable de MongoDB
- `tls=True` y `tlsAllowInvalidCertificates=True`: Manejo de certificados TLS
- Timeouts configurados en 30 segundos

### Función `inicializar_base_datos()`

Función principal que:
- Intenta conectar con reintentos (configurable)
- Si falla después de todos los reintentos, permite continuar en modo degradado si está habilitado
- Registra el progreso en la consola

### Funciones Getter

- `get_sensores_collection()`: Retorna la colección de sensores
- `get_medidas_collection()`: Retorna la colección de medidas
- `get_db()`: Retorna la base de datos
- `get_client()`: Retorna el cliente MongoDB

Todas retornan `None` si no hay conexión.

### Función `log_error(e, contexto="")`

Helper para logging de errores con formato consistente.

## 2. servidor.py - Servidor Principal Flask

Este es el archivo principal que configura y ejecuta el servidor Flask.

### Imports y Configuración Inicial

```python
from flask import Flask, jsonify, json
from flask_cors import CORS
from bson import ObjectId
```

- `Flask`: Framework web
- `CORS`: Para permitir peticiones cross-origin
- `ObjectId`: Para manejar IDs de MongoDB

### Configuración de la App

```python
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
```

Habilita CORS para todas las rutas y orígenes.

### Helpers

#### `convert_objectids(obj)`

Función recursiva que convierte todos los `ObjectId` en un objeto/dict/lista a strings para serialización JSON. Esto es necesario porque `ObjectId` no es serializable directamente a JSON.

#### Middleware `after_request(response)`

Se ejecuta después de cada petición. Convierte automáticamente `ObjectId` en respuestas JSON a strings.

### Configuración de Base de Datos

#### `configurar_base_datos()`

Crea índices en las colecciones para optimizar consultas:

**Índices en `sensores`:**
- `nombre` (único): Para búsquedas por nombre
- `activo + tipo_sensor`: Para filtrar sensores activos por tipo
- `campos.nombre_campo`: Para búsquedas en campos anidados

**Índices en `medidas`:**
- `sensor_id + campo_id + timestamp`: Para consultas de medidas específicas
- `timestamp`: Para ordenamiento por tiempo
- `sensor_id + timestamp`: Para medidas de un sensor ordenadas por tiempo

### Registro de Blueprints

```python
app.register_blueprint(sensores_bp)
app.register_blueprint(medidas_bp)
```

Registra los blueprints de sensores y medidas bajo el prefijo por defecto.

### Endpoints del Servidor

#### `GET /`

Endpoint raíz que confirma que el API está funcionando.

#### `GET /test-db`

Prueba la conexión a la base de datos:
- Ejecuta `client.admin.command('serverStatus')`
- Retorna versión de MongoDB si conecta
- Maneja errores de conexión

### Inicio del Servidor

El bloque `if __name__ == "__main__":` configura y inicia el servidor:

- **Variables de entorno:**
  - `BIND_HOST`: Host donde bindear (default: 0.0.0.0)
  - `PORT`: Puerto (default: 8860)
  - `FLASK_DEBUG`: Modo debug (default: 0)
  - `ALLOW_START_WITHOUT_DB`: Permitir inicio sin BD

- **Configuración UTF-8:** Para evitar errores de encoding al correr como servicio

- **Modo degradado:** Si no hay conexión a BD y está permitido, inicia pero endpoints devolverán 503

## 3. sensores.py - Gestión de Sensores

Blueprint que maneja todas las operaciones CRUD relacionadas con sensores.

### Función `convertir_sensor_a_json(sensor)`

Convierte un documento de sensor de MongoDB a un diccionario JSON serializable:
- Convierte `_id` a string
- Maneja campos anidados
- Convierte fechas `datetime` a strings ISO

### Endpoints

#### `POST /agregar_sensor`

Agrega un nuevo sensor o actualiza uno existente.

**Proceso:**
1. Valida datos requeridos (`sensor`, `tipo_sensor`)
2. Busca sensor existente por nombre
3. Si existe: actualiza tipo, activo y campos
4. Si no existe: crea nuevo sensor con campos
5. Maneja campos: actualiza existentes o agrega nuevos

**Campos del sensor:**
- `nombre`: Nombre único del sensor
- `tipo`: Tipo del sensor
- `activo`: Estado del sensor
- `campos`: Array de campos con nombre, tipo y estado

#### `PUT /editar_sensor/<sensor_id>`

Edita un sensor existente.

**Funcionalidades:**
- Activar/desactivar sensor (si solo se envía `activo`)
- Actualizar nombre, tipo, estado y campos
- Agregar nuevos campos o editar existentes

#### `DELETE /eliminar_sensor_definitivo/<sensor_id>`

Elimina un sensor y todas sus medidas asociadas.

**Proceso:**
1. Elimina todas las medidas del sensor
2. Elimina el sensor
3. Retorna confirmación

#### `GET /listar_sensores_campos`

Lista todos los sensores con sus campos.

**Proceso:**
1. Obtiene todos los sensores
2. Convierte cada sensor a formato JSON usando `convertir_sensor_a_json`
3. Retorna array de sensores

## 4. medidas.py - Gestión de Medidas

Blueprint que maneja las operaciones relacionadas con las medidas de los sensores.

### Endpoints

#### `POST /guardar`

Guarda medidas de múltiples sensores.

**Formato esperado:**
```json
{
  "measures": {
    "Sensor1": [
      {"detail": "Temperatura", "value": 25.5},
      {"detail": "Humedad", "value": 60.0}
    ]
  }
}
```

**Proceso:**
1. Obtiene sensores activos con sus campos
2. Crea un mapa de sensores para búsqueda rápida
3. Para cada medida:
   - Verifica que el sensor existe y está activo
   - Verifica que el campo existe y está activo
   - Crea documento de medida con `sensor_id`, `campo_id`, `valor`, `timestamp`
4. Inserta todas las medidas en batch

#### `GET /medidas`

Obtiene medidas con filtros opcionales.

**Parámetros de query:**
- `limite`: Número máximo de resultados (default: 100)
- `sensor_id`: Filtrar por sensor específico
- `campo_id`: Filtrar por campo específico
- `desde`: Fecha desde (ISO format)
- `hasta`: Fecha hasta (ISO format)

**Pipeline de agregación:**
1. `$match`: Aplica filtros
2. `$sort`: Ordena por timestamp descendente
3. `$limit`: Limita resultados
4. `$lookup`: Une con colección sensores
5. `$unwind`: Descompone arrays
6. `$match`: Filtra por campo_id
7. `$project`: Proyecta campos finales, convirtiendo ObjectId a string

#### `GET /estado`

Retorna el estado general del sistema.

**Información retornada:**
- Estado de conexión
- Total de sensores
- Total de medidas
- Timestamp de la última medida

## 5. requirements.txt - Dependencias

```
Flask              # Framework web
Flask-Cors         # Manejo de CORS
pymongo[srv]       # Driver MongoDB con soporte SRV
python-dotenv      # Carga de variables de entorno
certifi            # Certificados SSL
```

## Manejo de Errores Común

Todos los endpoints siguen un patrón similar de manejo de errores:

1. Verifican conexión a BD (retornan 503 si no hay)
2. Usan try/except para capturar excepciones
3. Usan `log_error()` para logging
4. Retornan JSON con mensaje de error y código HTTP apropiado

## Consideraciones de Diseño

### Separación de Concerns
- `database.py`: Solo conexión y configuración de BD
- `servidor.py`: Configuración del servidor y rutas generales
- `sensores.py` y `medidas.py`: Lógica de negocio específica

### Evitación de Imports Circulares
Los blueprints importan desde `database.py` en lugar de `servidor.py` para evitar dependencias circulares.

### Modo Degradado
El sistema puede funcionar sin conexión a BD, permitiendo despliegues donde la BD puede no estar disponible inicialmente.

### Serialización JSON
Manejo automático de `ObjectId` y `datetime` para compatibilidad con JSON.

### Índices de Base de Datos
Optimización de consultas comunes para mejor rendimiento.

Este backend proporciona una API robusta y escalable para el sistema de monitoreo agrícola SembrandoBits.

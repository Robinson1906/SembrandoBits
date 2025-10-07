# Backend API - SembrandoBits

Este backend es una API REST construida con Flask y MongoDB Atlas para gestionar sensores y medidas en un sistema de monitoreo agrícola.

## Tecnologías Utilizadas

- **Flask**: Framework web para Python
- **MongoDB Atlas**: Base de datos NoSQL en la nube
- **Flask-CORS**: Para manejo de CORS
- **Python-dotenv**: Para variables de entorno

## Estructura del Proyecto

```
Backend/
├── database.py      # Conexión y configuración de MongoDB
├── servidor.py      # Configuración principal del servidor Flask
├── sensores.py      # Endpoints para gestión de sensores
├── medidas.py       # Endpoints para gestión de medidas
├── requirements.txt # Dependencias Python
└── README.md        # Esta documentación
```

## Configuración

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con:

```
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/iotdb
DB_RETRY_ATTEMPTS=5
DB_RETRY_DELAY=5
ALLOW_START_WITHOUT_DB=1
BIND_HOST=0.0.0.0
PORT=8860
FLASK_DEBUG=0
```

## Base de Datos

### Esquema de Colecciones

#### Colección `sensores`

```json
{
  "_id": "ObjectId",
  "nombre": "string (único)",
  "tipo": "string",
  "activo": "boolean",
  "campos": [
    {
      "_id": "ObjectId",
      "nombre_campo": "string",
      "tipo_campo": "string",
      "activo": "boolean"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Colección `medidas`

```json
{
  "_id": "ObjectId",
  "sensor_id": "ObjectId (referencia a sensores._id)",
  "campo_id": "ObjectId (referencia a sensores.campos._id)",
  "valor": "mixed (número o string)",
  "timestamp": "datetime"
}
```

### Índices

- `sensores`: nombre (único), activo + tipo_sensor, campos.nombre_campo
- `medidas`: sensor_id + campo_id + timestamp, timestamp, sensor_id + timestamp

## API Endpoints

### Sensores

#### POST /sensores/agregar_sensor
Agrega o actualiza un sensor.

**Request Body:**
```json
{
  "sensor": "Nombre del sensor",
  "tipo_sensor": "Tipo del sensor",
  "activo": true,
  "campos": [
    {
      "nombre_campo": "Temperatura",
      "tipo_campo": "float"
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "mensaje": "Sensor agregado correctamente",
  "sensor_id": "string"
}
```

#### PUT /sensores/editar_sensor/{sensor_id}
Edita un sensor existente.

#### DELETE /sensores/eliminar_sensor_definitivo/{sensor_id}
Elimina un sensor y todas sus medidas.

#### GET /sensores/listar_sensores_campos
Lista todos los sensores con sus campos.

### Medidas

#### POST /medidas/guardar
Guarda medidas de sensores.

**Request Body:**
```json
{
  "measures": {
    "Sensor1": [
      {
        "detail": "Temperatura",
        "value": 25.5
      }
    ]
  }
}
```

#### GET /medidas/medidas
Obtiene medidas filtradas.

**Parámetros Query:**
- `limite`: Número máximo de resultados (default: 100)
- `sensor_id`: Filtrar por sensor
- `campo_id`: Filtrar por campo
- `desde`: Fecha desde (ISO format)
- `hasta`: Fecha hasta (ISO format)

#### GET /medidas/estado
Retorna el estado del sistema.

### Utilidades

#### GET /
Endpoint raíz de confirmación.

#### GET /test-db
Prueba la conexión a la base de datos.

## Inicio del Servidor

```bash
cd Backend
python servidor.py
```

El servidor iniciará en `http://localhost:8860` por defecto.

## Modo Degradado

Si no hay conexión a MongoDB, el servidor puede iniciarse en modo degradado (configurable), devolviendo errores 503 en endpoints que requieren base de datos.

## Manejo de Errores

- **400**: Datos inválidos
- **404**: Recurso no encontrado
- **500**: Error interno del servidor
- **503**: Servicio no disponible (sin conexión a BD)

## Logs

Los errores se registran en la consola con formato:
```
❌ ERROR contexto: mensaje

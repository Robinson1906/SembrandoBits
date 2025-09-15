# SembrandoBits

Sistema de monitoreo agrícola inteligente para cultivos y tierras utilizando sensores IoT. Permite gestionar sensores, registrar medidas en tiempo real y visualizar datos históricos a través de una interfaz web moderna.

## 🚀 Características Principales

- **Gestión Completa de Sensores**: Agregar, editar, activar/desactivar y eliminar sensores con campos personalizables
- **Monitoreo en Tiempo Real**: Registro automático de medidas con actualización cada 5 segundos
- **Visualización de Datos**: Tablas interactivas con historial de medidas
- **API RESTful**: Endpoints documentados para integración con dispositivos IoT
- **Interfaz Web Responsiva**: SPA moderna construida con React y TailwindCSS
- **Base de Datos Escalables**: MongoDB Atlas con índices optimizados
- **Despliegue Unificado**: Backend Flask sirve el frontend compilado desde una sola URL

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.10+**
- **Flask** - Framework web ligero
- **MongoDB Atlas** - Base de datos NoSQL en la nube
- **PyMongo** - Driver oficial de MongoDB para Python
- **Flask-CORS** - Manejo de CORS para API
- **python-dotenv** - Gestión de variables de entorno

### Frontend
- **React 19** - Biblioteca para interfaces de usuario
- **Vite** - Herramienta de construcción rápida
- **TailwindCSS 4** - Framework CSS utilitario
- **React Router DOM** - Enrutamiento del lado cliente
- **Recharts** - Biblioteca de gráficos (disponible para futuras expansiones)

## 📋 Prerrequisitos

- Python 3.10 o superior
- Node.js 18+ y npm
- Cuenta en MongoDB Atlas
- Conexión a internet (para MongoDB Atlas)

## 🔧 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/SembrandoBits.git
cd SembrandoBits
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
```

Editar `.env` con tu configuración:
```env
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
PORT=8860
BIND_HOST=0.0.0.0
FLASK_DEBUG=0
ALLOW_START_WITHOUT_DB=1
DB_RETRY_ATTEMPTS=5
DB_RETRY_DELAY=5
```

### 3. Instalar Dependencias del Backend
```bash
cd Backend
pip install -r requirements.txt
```

### 4. Instalar Dependencias del Frontend
```bash
cd ../frontend
npm install
```

## 🚀 Uso

### Modo Desarrollo
```bash
# Terminal 1: Backend
cd Backend
python servidor.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

El backend estará disponible en `http://localhost:8860` y el frontend en desarrollo en `http://localhost:7681`.

### Modo Producción
```bash
# Construir frontend
cd frontend
npm run build

# Iniciar backend (sirve el frontend compilado)
cd ../Backend
python servidor.py
```

Acceder desde cualquier dispositivo en la red a `http://IP_DEL_SERVIDOR:8860`.

## 📡 API RESTful

### Endpoints de Sensores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/agregar_sensor` | Agregar nuevo sensor |
| `PUT` | `/editar_sensor/<sensor_id>` | Editar sensor existente |
| `DELETE` | `/eliminar_sensor_definitivo/<sensor_id>` | Eliminar sensor permanentemente |
| `GET` | `/listar_sensores_campos` | Listar todos los sensores con campos |

### Endpoints de Medidas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/guardar` | Guardar medidas desde dispositivos IoT |
| `GET` | `/medidas` | Obtener medidas con filtros opcionales |
| `GET` | `/estado` | Estado general del sistema |

### Endpoints de Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página de inicio |
| `GET` | `/test-db` | Probar conexión a base de datos |
| `GET` | `/health` | Verificación de salud del servicio |

### Ejemplos de Uso de la API

#### Agregar Sensor
```bash
curl -X POST http://localhost:8860/agregar_sensor \
  -H "Content-Type: application/json" \
  -d '{
    "sensor": "SensorTemperatura",
    "tipo_sensor": "Temperatura",
    "activo": true,
    "campos": [
      {"nombre_campo": "temperatura", "tipo_campo": "float"},
      {"nombre_campo": "humedad", "tipo_campo": "float"}
    ]
  }'
```

#### Guardar Medidas
```bash
curl -X POST http://localhost:8860/guardar \
  -H "Content-Type: application/json" \
  -d '{
    "measures": {
      "SensorTemperatura": [
        {"detail": "temperatura", "value": 25.5},
        {"detail": "humedad", "value": 65.2}
      ]
    }
  }'
```

#### Obtener Medidas Recientes
```bash
curl "http://localhost:8860/medidas?limite=10"
```

## 🏗️ Estructura del Proyecto

```
SembrandoBits/
├── Backend/                          # Código del servidor
│   ├── servidor.py                   # Aplicación Flask principal
│   ├── database.py                   # Configuración y conexión MongoDB
│   ├── sensores.py                   # Blueprints para gestión de sensores
│   ├── medidas.py                    # Blueprints para gestión de medidas
│   ├── requirements.txt              # Dependencias Python
│   ├── backend_stdout.log            # Logs de salida
│   └── backend_stderr.log            # Logs de error
├── frontend/                         # Aplicación React
│   ├── src/
│   │   ├── app.jsx                   # Componente principal de la app
│   │   ├── main.jsx                  # Punto de entrada
│   │   ├── style.css                 # Estilos globales
│   │   ├── Components/               # Componentes reutilizables
│   │   │   ├── Navbar.jsx            # Barra de navegación
│   │   │   ├── Footer.jsx            # Pie de página
│   │   │   └── SensoresTabla.jsx     # Tabla de sensores
│   │   └── Pages/                    # Páginas de la aplicación
│   │       ├── home/
│   │       │   ├── Home.jsx          # Página de inicio
│   │       │   └── stylehome.css     # Estilos específicos
│   │       ├── Sensores/
│   │       │   ├── Sensores.jsx      # Gestión de sensores
│   │       │   └── Sensores.css      # Estilos de sensores
│   │       ├── Cultivos/             # (En desarrollo)
│   │       └── Tierras/              # (En desarrollo)
│   ├── public/
│   │   └── vite.svg                  # Ícono de Vite
│   ├── package.json                  # Dependencias y scripts
│   ├── vite.config.js                # Configuración de Vite
│   └── nginx.conf                    # Configuración Nginx (opcional)
├── .env                              # Variables de entorno (no versionado)
├── .env.example                      # Ejemplo de variables de entorno
├── .gitignore                        # Archivos ignorados por Git
├── .gitattributes                    # Atributos Git
├── package.json                      # Dependencias raíz (opcional)
├── README.md                         # Este archivo
└── README_DEPLOY.md                  # Guía de despliegue detallada
```

## 🎨 Interfaz de Usuario

### Páginas Disponibles
- **Inicio (/)**: Dashboard general con información del sistema
- **Sensores (/Sensores)**: Gestión completa de sensores y visualización de medidas

### Funcionalidades de la UI
- Formularios dinámicos para agregar/editar sensores
- Tablas responsivas con paginación
- Estados de carga y manejo de errores
- Actualización automática de medidas
- Modal para edición de sensores
- Confirmaciones para acciones destructivas

## 📊 Base de Datos

### Colecciones MongoDB

#### `sensores`
```javascript
{
  "_id": ObjectId,
  "nombre": "string",           // Nombre único del sensor
  "tipo": "string",             // Tipo de sensor (Temperatura, Humedad, etc.)
  "activo": boolean,            // Estado del sensor
  "campos": [{                  // Campos de medición
    "_id": ObjectId,
    "nombre_campo": "string",
    "tipo_campo": "string",     // float, number, int, boolean, string
    "activo": boolean
  }],
  "created_at": DateTime,
  "updated_at": DateTime
}
```

#### `medidas`
```javascript
{
  "_id": ObjectId,
  "sensor_id": ObjectId,        // Referencia al sensor
  "campo_id": ObjectId,         // Referencia al campo
  "valor": any,                 // Valor de la medición
  "timestamp": DateTime         // Fecha y hora de la medición
}
```

### Índices Optimizados
- `sensores`: nombre (único), activo + tipo_sensor, campos.nombre_campo
- `medidas`: sensor_id + campo_id + timestamp, timestamp

## 🚀 Despliegue

Para instrucciones detalladas de despliegue en producción, consulta [README_DEPLOY.md](README_DEPLOY.md).

### Resumen de Despliegue
1. Configurar MongoDB Atlas
2. Construir frontend (`npm run build`)
3. Configurar variables de entorno
4. Iniciar servidor Flask
5. Configurar firewall y port forwarding si es necesario

## 🔧 Configuración Avanzada

### Variables de Entorno
- `MONGO_URI`: URI de conexión MongoDB Atlas
- `PORT`: Puerto del servidor (default: 8860)
- `BIND_HOST`: Host de escucha (default: 0.0.0.0)
- `FLASK_DEBUG`: Modo debug (0/1)
- `ALLOW_START_WITHOUT_DB`: Permitir inicio sin DB (0/1)
- `DB_RETRY_ATTEMPTS`: Reintentos de conexión DB
- `DB_RETRY_DELAY`: Segundos entre reintentos

### Modo Degradado
Si no hay conexión a MongoDB, el servidor puede iniciarse en modo degradado devolviendo errores 503 en endpoints de escritura/lectura.

## 🐛 Solución de Problemas

### Problemas Comunes
- **Error de conexión MongoDB**: Verificar URI y credenciales
- **Assets no cargan**: Asegurar que `dist/` existe después del build
- **CORS errors**: Verificar configuración de orígenes permitidos
- **Puerto ocupado**: Cambiar PORT en variables de entorno

### Logs
Los logs se escriben en:
- `Backend/backend_stdout.log`
- `Backend/backend_stderr.log`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Guías de Desarrollo
- Seguir PEP 8 para código Python
- Usar ESLint para JavaScript/React
- Mantener compatibilidad con Python 3.10+
- Documentar nuevas funciones y endpoints

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Revisar logs del servidor
- Verificar documentación de API

---

**Desarrollado con ❤️ para la agricultura inteligente**

import os
import sys
from flask import Flask, jsonify, json
from flask_cors import CORS
from bson import ObjectId

# Importar configuración de base de datos
from database import inicializar_base_datos, get_sensores_collection, get_medidas_collection, get_db, get_client, log_error

# Importar Blueprints
from sensores import sensores_bp
from medidas import medidas_bp

# --- Configuración Inicial ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Obtener referencias a las colecciones
sensores_collection = get_sensores_collection()
medidas_collection = get_medidas_collection()
db = get_db()
client = get_client()

# --- Helpers ---
# Función para convertir ObjectId a string
def convert_objectids(obj):
    """Convierte recursivamente ObjectId en strings para serialización JSON."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [convert_objectids(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_objectids(value) for key, value in obj.items()}
    return obj

# Middleware para procesar respuestas JSON
@app.after_request
def after_request(response):
    """Middleware que convierte ObjectId en respuestas JSON a strings."""
    if response.is_json:
        try:
            data = response.get_json()
            if data is not None:
                response.set_data(json.dumps(convert_objectids(data)))
        except:
            pass  # Si no es JSON válido, no hacer nada
    return response

# --- Configuración de Índices y Validaciones ---
def configurar_base_datos():
    """Configura índices en las colecciones de la base de datos para optimizar consultas."""
    if db is None:
        print("[WARN] No se puede configurar base de datos: sin conexion")
        return
    try:
        # Indices para coleccion sensores
        sensores_collection.create_index([("nombre", 1)], unique=True, background=True)
        sensores_collection.create_index([("activo", 1), ("tipo_sensor", 1)], background=True)
        sensores_collection.create_index([("campos.nombre_campo", 1)], background=True)
        # Indices para coleccion medidas
        medidas_collection.create_index([("sensor_id", 1), ("campo_id", 1), ("timestamp", -1)], background=True)
        medidas_collection.create_index([("timestamp", -1)], background=True)
        medidas_collection.create_index([("sensor_id", 1), ("timestamp", 1)], background=True)
        print("[OK] Indices de la base de datos creados correctamente")
    except Exception as e:
        print(f"[WARN] Error al configurar indices: {e}. La app funcionara pero con rendimiento reducido.")

# Configurar la base de datos
configurar_base_datos()

# --- Registro de Blueprints ---
app.register_blueprint(sensores_bp)
app.register_blueprint(medidas_bp)

@app.route("/")
def home():
    """Endpoint raíz del servidor que confirma que el API está funcionando."""
    return "Servidor Flask con MongoDB Atlas"

# --- Endpoint de prueba de conexión ---
@app.route("/test-db")
def test_db():
    """Endpoint para probar la conexión a la base de datos MongoDB."""
    if client is not None:  # CORRECCIÓN: También aquí usar 'is not None'
        try:
            db_status = client.admin.command('serverStatus')
            return jsonify({
                "status": "success",
                "message": "Conexión a MongoDB establecida correctamente",
                "db_version": db_status.get('version', 'N/A')
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error en la conexión: {str(e)}"
            }), 500
    else:
        return jsonify({
            "status": "error",
            "message": "No hay conexión a la base de datos"
        }), 500

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    # Permitir override vía variables de entorno
    bind_host = os.getenv("BIND_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT", "8860"))
    except ValueError:
        print("[WARN] PORT invalido en variables de entorno, usando 8860")
        port = 8860

    debug_flag = os.getenv("FLASK_DEBUG", "0") == "1"
    allow_without_db = os.getenv("ALLOW_START_WITHOUT_DB", "1") == "1"

    if client is None:
        if allow_without_db:
            print("[INFO] Iniciando en MODO DEGRADADO: no hay conexion con la base de datos. Endpoints de escritura/lectura devolveran error 503.")
        else:
            print("[ERROR] No hay conexion a la base de datos y ALLOW_START_WITHOUT_DB=0. Abortando inicio.")
            import time; time.sleep(3)
            raise SystemExit(1)

    # Forzar UTF-8 para evitar errores de encoding al correr como servicio
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print(f"[INFO] Iniciando servidor en http://{bind_host}:{port} (debug={debug_flag})")
    app.run(host=bind_host, port=port, debug=debug_flag)
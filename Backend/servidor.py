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
def log_error(e, contexto=""):
    print(f"❌ ERROR {contexto}: {e}")

# Función para convertir ObjectId a string
def convert_objectids(obj):
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
    if db is None:  # CORRECCIÓN: Usar 'is None' en lugar de 'not db'
        print("⚠️  No se puede configurar base de datos: sin conexión")
        return
        
    try:
        # Índices para colección sensores
        sensores_collection.create_index([("nombre", 1)], unique=True, background=True)
        sensores_collection.create_index([("activo", 1), ("tipo_sensor", 1)], background=True)
        sensores_collection.create_index([("campos.nombre_campo", 1)], background=True)
        
        # Índices para colección medidas
        medidas_collection.create_index([("sensor_id", 1), ("campo_id", 1), ("timestamp", -1)], background=True)
        medidas_collection.create_index([("timestamp", -1)], background=True)
        medidas_collection.create_index([("sensor_id", 1), ("timestamp", 1)], background=True)
        
        print("✅ Índices de la base de datos creados correctamente")
        
    except Exception as e:
        print(f"⚠️  Error al configurar índices: {e}. La app funcionará pero con rendimiento reducido.")

# Configurar la base de datos
configurar_base_datos()

# --- Registro de Blueprints ---
app.register_blueprint(sensores_bp)
app.register_blueprint(medidas_bp)

@app.route("/")
def home():
    return "🌐 Servidor Flask con MongoDB Atlas 🚀"

# --- Endpoint de prueba de conexión ---
@app.route("/test-db")
def test_db():
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
    if client is not None:  # CORRECCIÓN: Usar 'is not None'
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("El servidor no se puede iniciar debido a un error de conexión con la base de datos.")
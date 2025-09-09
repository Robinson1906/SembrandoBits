from flask import Flask, request, jsonify
from flask.json.provider import JSONProvider
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId  # Para manejar los IDs de MongoDB
import os
from dotenv import load_dotenv
from pathlib import Path
import certifi # Importar certifi

# --- Configuración Inicial ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGO_URI")

# --- Conexión a MongoDB Atlas ---
try:
    # Se revierte al método seguro usando certifi.
    # El problema no es de validación de certificados, sino de handshake a bajo nivel.
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    # Enviar un ping para confirmar una conexión exitosa
    client.admin.command('ping')
    print("✅ Conexión a MongoDB Atlas exitosa.")
    # Definir la base de datos y las colecciones
    db = client.iotdb # Nombre de la base de datos
    sensores_collection = db.sensores # Colección para sensores
    medidas_collection = db.medidas # Colección para medidas
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
    client = None
    db = None
    sensores_collection = None
    medidas_collection = None

# --- Helpers ---
def log_error(e, contexto=""):
    print(f"❌ ERROR {contexto}: {e}")

# Clase para ayudar a convertir ObjectId a string para JSON
class CustomJSONProvider(JSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

app.json = CustomJSONProvider(app)

# --- Rutas ---

@app.route("/")
def home():
    return "🌐 Servidor Flask con MongoDB Atlas 🚀"

# ===========================
# AGREGAR/ACTUALIZAR SENSOR CON CAMPOS
# ===========================
@app.route("/agregar_sensor", methods=["POST"])
def agregar_sensor():
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        sensor_nombre = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo = data.get("activo", True)
        campos_nuevos = data.get("campos", [])

        if not sensor_nombre or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400

        # Buscar si el sensor ya existe por su nombre
        sensor_existente = sensores_collection.find_one({"nombre": sensor_nombre})

        if sensor_existente:
            # Actualizar sensor existente
            sensor_id = sensor_existente['_id']
            update_fields = {
                "tipo": tipo_sensor,
                "activo": activo
            }
            sensores_collection.update_one({"_id": sensor_id}, {"$set": update_fields})
            
            # Actualizar o agregar campos
            for campo in campos_nuevos:
                nombre_campo = campo.get("nombre_campo")
                tipo_campo = campo.get("tipo_campo")
                if not nombre_campo or not tipo_campo: continue

                # Buscar si el campo ya existe dentro del sensor
                campo_existente = sensores_collection.find_one(
                    {"_id": sensor_id, "campos.nombre_campo": nombre_campo}
                )
                if campo_existente:
                    # Actualizar campo existente
                    sensores_collection.update_one(
                        {"_id": sensor_id, "campos.nombre_campo": nombre_campo},
                        {"$set": {"campos.$.tipo_campo": tipo_campo, "campos.$.activo": True}}
                    )
                else:
                    # Agregar nuevo campo
                    nuevo_campo_doc = {
                        "_id": ObjectId(),
                        "nombre_campo": nombre_campo,
                        "tipo_campo": tipo_campo,
                        "activo": True
                    }
                    sensores_collection.update_one(
                        {"_id": sensor_id},
                        {"$push": {"campos": nuevo_campo_doc}}
                    )
            mensaje = f"Sensor '{sensor_nombre}' actualizado"
        else:
            # Crear nuevo sensor
            campos_doc = [{
                "_id": ObjectId(),
                "nombre_campo": c.get("nombre_campo"),
                "tipo_campo": c.get("tipo_campo"),
                "activo": True
            } for c in campos_nuevos if c.get("nombre_campo") and c.get("tipo_campo")]

            nuevo_sensor = {
                "nombre": sensor_nombre,
                "tipo": tipo_sensor,
                "activo": activo,
                "campos": campos_doc
            }
            result = sensores_collection.insert_one(nuevo_sensor)
            sensor_id = result.inserted_id
            mensaje = f"Sensor '{sensor_nombre}' agregado correctamente"

        return jsonify({"status": "ok", "mensaje": mensaje, "sensor_id": str(sensor_id)})

    except Exception as e:
        log_error(e, "agregar_sensor")
        return jsonify({"error": str(e)}), 500

# ===========================
# EDITAR SENSOR
# ===========================
@app.route("/editar_sensor/<string:sensor_id>", methods=["PUT"])
def editar_sensor(sensor_id):
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        obj_id = ObjectId(sensor_id)

        # Toggle de estado del sensor
        if 'activo' in data and len(data) == 1:
            activo = data.get("activo")
            sensores_collection.update_one({"_id": obj_id}, {"$set": {"activo": activo}})
            estado = "activado" if activo else "desactivado"
            return jsonify({"status": "ok", "mensaje": f"Sensor {estado} correctamente"})

        # Edición completa
        sensor_nombre = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo = data.get("activo", True)
        campos = data.get("campos", [])

        if not sensor_nombre or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400

        # Actualizar datos principales del sensor
        sensores_collection.update_one(
            {"_id": obj_id},
            {"$set": {"nombre": sensor_nombre, "tipo": tipo_sensor, "activo": activo}}
        )

        # Actualizar o agregar campos
        for campo in campos:
            nombre_campo = campo.get("nombre_campo")
            tipo_campo = campo.get("tipo_campo")
            campo_id_str = campo.get("campo_id") # En Mongo, el id del subdocumento es _id

            if not nombre_campo or not tipo_campo: continue

            if campo_id_str:
                # Actualizar campo existente
                campo_obj_id = ObjectId(campo_id_str)
                sensores_collection.update_one(
                    {"_id": obj_id, "campos._id": campo_obj_id},
                    {"$set": {"campos.$.nombre_campo": nombre_campo, "campos.$.tipo_campo": tipo_campo, "campos.$.activo": True}}
                )
            else:
                # Agregar nuevo campo
                nuevo_campo_doc = {
                    "_id": ObjectId(),
                    "nombre_campo": nombre_campo,
                    "tipo_campo": tipo_campo,
                    "activo": True
                }
                sensores_collection.update_one(
                    {"_id": obj_id},
                    {"$push": {"campos": nuevo_campo_doc}}
                )

        return jsonify({"status": "ok", "mensaje": f"Sensor {sensor_id} actualizado"})
    except Exception as e:
        log_error(e, "editar_sensor")
        return jsonify({"error": str(e)}), 500

# ===========================
# ELIMINAR SENSOR DEFINITIVAMENTE
# ===========================
@app.route("/eliminar_sensor_definitivo/<string:sensor_id>", methods=["DELETE"])
def eliminar_sensor_definitivo(sensor_id):
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        obj_id = ObjectId(sensor_id)
        
        # Primero, eliminar todas las medidas asociadas a este sensor
        medidas_collection.delete_many({"sensor_id": obj_id})
        
        # Luego, eliminar el sensor
        result = sensores_collection.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Sensor no encontrado"}), 404
            
        return jsonify({"status": "ok", "mensaje": f"Sensor {sensor_id} y sus medidas eliminados definitivamente"})
        
    except Exception as e:
        log_error(e, "eliminar_sensor_definitivo")
        return jsonify({"error": str(e)}), 500

# ===========================
# LISTAR SENSORES CON CAMPOS
# ===========================
@app.route("/listar_sensores_campos", methods=["GET"])
def listar_sensores_campos():
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        sensores = list(sensores_collection.find())
        
        # Renombrar _id a sensor_id para compatibilidad con frontend
        for sensor in sensores:
            sensor['sensor_id'] = sensor.pop('_id')
            sensor['sensor'] = sensor.get('nombre')
            sensor['tipo_sensor'] = sensor.get('tipo')
            if 'campos' in sensor:
                for campo in sensor['campos']:
                    campo['campo_id'] = campo.pop('_id')

        return jsonify(sensores)
    except Exception as e:
        log_error(e, "listar_sensores_campos")
        return jsonify({"error": str(e)}), 500

# ===========================
# GUARDAR MEDIDAS
# ===========================
@app.route("/guardar", methods=["POST"])
def guardar_medidas():
    if not medidas_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        if not data or "measures" not in data:
            return jsonify({"error": "El JSON debe contener 'measures'"}), 400

        measures = data["measures"]
        medidas_a_insertar = []

        # Optimización: Obtener todos los sensores y campos activos de una vez
        sensores_activos = list(sensores_collection.find({"activo": True}))
        mapa_sensores = {
            s['nombre']: {
                "id": s['_id'],
                "campos": {c['nombre_campo']: c['_id'] for c in s.get('campos', []) if c.get('activo')}
            } for s in sensores_activos
        }

        for sensor_name, lecturas in measures.items():
            if sensor_name not in mapa_sensores:
                continue
            
            sensor_info = mapa_sensores[sensor_name]
            sensor_id = sensor_info['id']

            for lectura in lecturas:
                detalle = lectura.get("detail")
                valor = lectura.get("value")

                if detalle in sensor_info['campos']:
                    campo_id = sensor_info['campos'][detalle]
                    medidas_a_insertar.append({
                        "sensor_id": sensor_id,
                        "campo_id": campo_id,
                        "valor": valor,
                        "fecha": ObjectId().generation_time # Fecha y hora de inserción
                    })
        
        if medidas_a_insertar:
            medidas_collection.insert_many(medidas_a_insertar)

        return jsonify({"status": "ok", "mensaje": "Medidas procesadas correctamente"})
    except Exception as e:
        log_error(e, "guardar_medidas")
        return jsonify({"error": str(e)}), 500

# ===========================
# LEER MEDIDAS
# ===========================
@app.route("/medidas", methods=["GET"])
def obtener_medidas():
    if not medidas_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        # Usar aggregation para hacer el "join" entre colecciones
        pipeline = [
            {
                '$sort': {'fecha': -1} # Ordenar primero para eficiencia
            },
            {
                '$limit': 200 # Limitar a las últimas 200 medidas
            },
            {
                '$lookup': {
                    'from': 'sensores',
                    'localField': 'sensor_id',
                    'foreignField': '_id',
                    'as': 'sensor_info'
                }
            },
            {
                '$unwind': '$sensor_info' # Descomponer el array de sensor_info
            },
            {
                '$unwind': '$sensor_info.campos' # Descomponer el array de campos
            },
            {
                '$match': {
                    '$expr': {'$eq': ['$campo_id', '$sensor_info.campos._id']}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'id': '$_id',
                    'sensor': '$sensor_info.nombre',
                    'nombre_campo': '$sensor_info.campos.nombre_campo',
                    'valor': '$valor',
                    'fecha': '$fecha'
                }
            }
        ]
        medidas = list(medidas_collection.aggregate(pipeline))
        return jsonify(medidas)
    except Exception as e:
        log_error(e, "obtener_medidas")
        return jsonify({"error": str(e)}), 500

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    if client:
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("El servidor no se puede iniciar debido a un error de conexión con la base de datos.")
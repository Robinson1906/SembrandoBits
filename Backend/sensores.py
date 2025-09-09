from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

# Importar desde database en lugar de servidor (EVITA CIRCULAR IMPORT)
from database import get_sensores_collection, get_medidas_collection, log_error

sensores_bp = Blueprint('sensores', __name__)

# Obtener colecciones desde database
sensores_collection = get_sensores_collection()
medidas_collection = get_medidas_collection()

@sensores_bp.route('/agregar_sensor', methods=['POST'])
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

        sensor_existente = sensores_collection.find_one({"nombre": sensor_nombre})

        if sensor_existente:
            sensor_id = sensor_existente['_id']
            update_fields = {
                "tipo": tipo_sensor,
                "activo": activo,
                "updated_at": datetime.utcnow()
            }
            sensores_collection.update_one({"_id": sensor_id}, {"$set": update_fields})
            for campo in campos_nuevos:
                nombre_campo = campo.get("nombre_campo")
                tipo_campo = campo.get("tipo_campo")
                if not nombre_campo or not tipo_campo: continue
                campo_existente = sensores_collection.find_one(
                    {"_id": sensor_id, "campos.nombre_campo": nombre_campo}
                )
                if campo_existente:
                    sensores_collection.update_one(
                        {"_id": sensor_id, "campos.nombre_campo": nombre_campo},
                        {"$set": {"campos.$.tipo_campo": tipo_campo, "campos.$.activo": True}}
                    )
                else:
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
                "campos": campos_doc,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = sensores_collection.insert_one(nuevo_sensor)
            sensor_id = result.inserted_id
            mensaje = f"Sensor '{sensor_nombre}' agregado correctamente"

        return jsonify({"status": "ok", "mensaje": mensaje, "sensor_id": str(sensor_id)})

    except Exception as e:
        log_error(e, "agregar_sensor")
        return jsonify({"error": str(e)}), 500

@sensores_bp.route('/editar_sensor/<string:sensor_id>', methods=['PUT'])
def editar_sensor(sensor_id):
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        obj_id = ObjectId(sensor_id)
        if 'activo' in data and len(data) == 1:
            activo = data.get("activo")
            sensores_collection.update_one(
                {"_id": obj_id}, 
                {"$set": {"activo": activo, "updated_at": datetime.utcnow()}}
            )
            estado = "activado" if activo else "desactivado"
            return jsonify({"status": "ok", "mensaje": f"Sensor {estado} correctamente"})
        sensor_nombre = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo = data.get("activo", True)
        campos = data.get("campos", [])
        if not sensor_nombre or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400
        sensores_collection.update_one(
            {"_id": obj_id},
            {"$set": {
                "nombre": sensor_nombre, 
                "tipo": tipo_sensor, 
                "activo": activo,
                "updated_at": datetime.utcnow()
            }}
        )
        for campo in campos:
            nombre_campo = campo.get("nombre_campo")
            tipo_campo = campo.get("tipo_campo")
            campo_id_str = campo.get("campo_id")
            if not nombre_campo or not tipo_campo:
                continue
            if campo_id_str:
                campo_obj_id = ObjectId(campo_id_str)
                sensores_collection.update_one(
                    {"_id": obj_id, "campos._id": campo_obj_id},
                    {"$set": {
                        "campos.$.nombre_campo": nombre_campo, 
                        "campos.$.tipo_campo": tipo_campo, 
                        "campos.$.activo": True
                    }}
                )
            else:
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

@sensores_bp.route('/eliminar_sensor_definitivo/<string:sensor_id>', methods=['DELETE'])
def eliminar_sensor_definitivo(sensor_id):
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        obj_id = ObjectId(sensor_id)
        medidas_collection.delete_many({"sensor_id": obj_id})
        result = sensores_collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Sensor no encontrado"}), 404
        return jsonify({"status": "ok", "mensaje": f"Sensor {sensor_id} y sus medidas eliminados definitivamente"})
    except Exception as e:
        log_error(e, "eliminar_sensor_definitivo")
        return jsonify({"error": str(e)}), 500

@sensores_bp.route('/listar_sensores_campos', methods=['GET'])
def listar_sensores_campos():
    if not sensores_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        sensores = list(sensores_collection.find())
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
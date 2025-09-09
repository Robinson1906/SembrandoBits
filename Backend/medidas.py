from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

# Importar desde database en lugar de servidor (EVITA CIRCULAR IMPORT)
from database import get_medidas_collection, get_sensores_collection, log_error

medidas_bp = Blueprint('medidas', __name__)

# Obtener colecciones desde database
medidas_collection = get_medidas_collection()
sensores_collection = get_sensores_collection()

@medidas_bp.route('/guardar', methods=['POST'])
def guardar_medidas():
    if not medidas_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        if not data or "measures" not in data:
            return jsonify({"error": "El JSON debe contener 'measures'"}), 400
        measures = data["measures"]
        medidas_a_insertar = []
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
                        "timestamp": datetime.utcnow()
                    })
        if medidas_a_insertar:
            medidas_collection.insert_many(medidas_a_insertar)
        return jsonify({"status": "ok", "mensaje": "Medidas procesadas correctamente"})
    except Exception as e:
        log_error(e, "guardar_medidas")
        return jsonify({"error": str(e)}), 500

@medidas_bp.route('/medidas', methods=['GET'])
def obtener_medidas():
    if not medidas_collection:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        limite = int(request.args.get('limite', 100))
        sensor_id = request.args.get('sensor_id')
        campo_id = request.args.get('campo_id')
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        query = {}
        if sensor_id:
            query["sensor_id"] = ObjectId(sensor_id)
        if campo_id:
            query["campo_id"] = ObjectId(campo_id)
        if desde or hasta:
            query["timestamp"] = {}
            if desde:
                query["timestamp"]["$gte"] = datetime.fromisoformat(desde.replace('Z', '+00:00'))
            if hasta:
                query["timestamp"]["$lte"] = datetime.fromisoformat(hasta.replace('Z', '+00:00'))
        pipeline = [
            {"$match": query},
            {"$sort": {"timestamp": -1}},
            {"$limit": limite},
            {
                "$lookup": {
                    "from": "sensores",
                    "localField": "sensor_id",
                    "foreignField": "_id",
                    "as": "sensor_info"
                }
            },
            {"$unwind": "$sensor_info"},
            {"$unwind": "$sensor_info.campos"},
            {
                "$match": {
                    "$expr": {"$eq": ["$campo_id", "$sensor_info.campos._id"]}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "sensor": "$sensor_info.nombre",
                    "nombre_campo": "$sensor_info.campos.nombre_campo",
                    "valor": "$valor",
                    "timestamp": "$timestamp"
                }
            }
        ]
        medidas = list(medidas_collection.aggregate(pipeline))
        return jsonify(medidas)
    except Exception as e:
        log_error(e, "obtener_medidas")
        return jsonify({"error": str(e)}), 500

@medidas_bp.route('/estado', methods=['GET'])
def estado_sistema():
    try:
        total_sensores = sensores_collection.count_documents({}) if sensores_collection else 0
        total_medidas = medidas_collection.count_documents({}) if medidas_collection else 0
        ultima_medida = medidas_collection.find_one(
            {}, 
            {"sort": [("timestamp", -1)], "projection": {"timestamp": 1}}
        ) if medidas_collection else None
        return jsonify({
            "estado": "conectado" if medidas_collection else "desconectado",
            "total_sensores": total_sensores,
            "total_medidas": total_medidas,
            "ultima_medida": ultima_medida["timestamp"] if ultima_medida else None
        })
    except Exception as e:
        log_error(e, "estado_sistema")
        return jsonify({"error": str(e)}), 500
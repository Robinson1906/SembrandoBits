from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

# Importar desde database en lugar de servidor (EVITA CIRCULAR IMPORT)
from database import get_medidas_collection, get_sensores_collection, log_error

def validar_valor_por_tipo(valor, tipo_campo, nombre_campo):
    """
    Valida y convierte un valor según el tipo de campo definido.
    
    Args:
        valor: Valor a validar
        tipo_campo: Tipo de campo ('boolean', 'float', 'integer', etc.)
        nombre_campo: Nombre del campo para mensajes de error
    
    Returns:
        tuple: (valor_convertido, mensaje_error)
        Si hay error, el primer elemento es None
    """
    if valor is None:
        return None, None
    
    if tipo_campo.lower() == 'boolean':
        # Usar la misma lógica de validación que en sensores.py
        if isinstance(valor, bool):
            return valor, None
        elif isinstance(valor, str):
            valor_lower = valor.lower()
            if valor_lower in ['true', '1', 'yes', 'on']:
                return True, None
            elif valor_lower in ['false', '0', 'no', 'off']:
                return False, None
            else:
                return None, f"El campo '{nombre_campo}' debe ser un booleano válido (true/false)"
        elif isinstance(valor, int):
            return bool(valor), None
        else:
            return None, f"El campo '{nombre_campo}' debe ser un booleano válido"
    elif tipo_campo.lower() in ['float', 'double']:
        try:
            return float(valor), None
        except (ValueError, TypeError):
            return None, f"El campo '{nombre_campo}' debe ser un número decimal válido"
    elif tipo_campo.lower() in ['integer', 'int']:
        try:
            return int(valor), None
        except (ValueError, TypeError):
            return None, f"El campo '{nombre_campo}' debe ser un número entero válido"
    else:
        # Para otros tipos, devolver el valor tal como está
        return valor, None

medidas_bp = Blueprint('medidas', __name__)

# Obtener colecciones desde database
medidas_collection = get_medidas_collection()
sensores_collection = get_sensores_collection()

@medidas_bp.route('/guardar', methods=['POST'])
def guardar_medidas():
    """Guarda medidas de sensores en la base de datos. Espera un JSON con 'measures'."""
    if medidas_collection is None:
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
                "campos": {
                    c['nombre_campo']: {
                        'id': c['_id'],
                        'tipo': c['tipo_campo']
                    } for c in s.get('campos', []) if c.get('activo')
                }
            } for s in sensores_activos
        }
        for sensor_name, lecturas in measures.items():
            if sensor_name not in mapa_sensores:
                continue
            sensor_info = mapa_sensores[sensor_name]
            sensor_id = sensor_info['id']
            for lectura in lecturas:
                detalle = lectura.get("detail")
                valor_raw = lectura.get("value")
                
                if detalle in sensor_info['campos']:
                    campo_info = sensor_info['campos'][detalle]
                    campo_id = campo_info['id']
                    tipo_campo = campo_info['tipo']
                    
                    # Validar y convertir el valor según el tipo de campo
                    valor_validado, error_validacion = validar_valor_por_tipo(
                        valor_raw, tipo_campo, detalle
                    )
                    
                    if error_validacion:
                        return jsonify({"error": f"Sensor '{sensor_name}', campo '{detalle}': {error_validacion}"}), 400
                    
                    medidas_a_insertar.append({
                        "sensor_id": sensor_id,
                        "campo_id": campo_id,
                        "valor": valor_validado,
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
    """Obtiene medidas filtradas por parámetros opcionales: limite, sensor_id, campo_id, desde, hasta."""
    if medidas_collection is None:
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
                    "_id": {"$toString": "$_id"},  # Convertir ObjectId a string
                    "sensor": "$sensor_info.nombre",
                    "nombre_campo": "$sensor_info.campos.nombre_campo",
                    "valor": "$valor",
                    "timestamp": "$timestamp"
                }
            }
        ]
        medidas = list(medidas_collection.aggregate(pipeline))
        
        # Convertir timestamp a formato ISO para JSON y asegurar que los booleanos se muestren correctamente
        for medida in medidas:
            if 'timestamp' in medida and medida['timestamp']:
                medida['timestamp'] = medida['timestamp'].isoformat()
            
            # Convertir valores booleanos a string para que el frontend los muestre correctamente
            if 'valor' in medida and isinstance(medida['valor'], bool):
                medida['valor'] = str(medida['valor']).lower()  # true/false en minúsculas
        
        return jsonify(medidas)
    except Exception as e:
        log_error(e, "obtener_medidas")
        return jsonify({"error": str(e)}), 500

@medidas_bp.route('/estado', methods=['GET'])
def estado_sistema():
    """Retorna el estado del sistema: conexión, total sensores, total medidas, última medida."""
    try:
        total_sensores = sensores_collection.count_documents({}) if sensores_collection is not None else 0
        total_medidas = medidas_collection.count_documents({}) if medidas_collection is not None else 0
        ultima_medida = medidas_collection.find_one(
            {}, 
            {"sort": [("timestamp", -1)], "projection": {"timestamp": 1}}
        ) if medidas_collection is not None else None
        
        # Convertir timestamp si existe
        ultima_medida_timestamp = None
        if ultima_medida and 'timestamp' in ultima_medida:
            ultima_medida_timestamp = ultima_medida['timestamp'].isoformat()
        
        return jsonify({
            "estado": "conectado" if medidas_collection is not None else "desconectado",
            "total_sensores": total_sensores,
            "total_medidas": total_medidas,
            "ultima_medida": ultima_medida_timestamp
        })
    except Exception as e:
        log_error(e, "estado_sistema")
        return jsonify({"error": str(e)}), 500

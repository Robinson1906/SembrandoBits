from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

# Importar desde database en lugar de servidor (EVITA CIRCULAR IMPORT)
from database import get_sensores_collection, get_medidas_collection, log_error

def validar_booleano(valor, campo_nombre="activo", valor_defecto=True):
    """
    Valida y convierte un valor a booleano de forma robusta.
    
    Args:
        valor: Valor a validar
        campo_nombre: Nombre del campo para mensajes de error
        valor_defecto: Valor por defecto si el valor es None
    
    Returns:
        tuple: (valor_booleano, mensaje_error)
        Si hay error, el primer elemento es None
    """
    if valor is None:
        return valor_defecto, None
    
    if isinstance(valor, bool):
        return valor, None
    elif isinstance(valor, str):
        valor_lower = valor.lower()
        if valor_lower in ['true', '1', 'yes', 'on']:
            return True, None
        elif valor_lower in ['false', '0', 'no', 'off']:
            return False, None
        else:
            return None, f"El campo '{campo_nombre}' debe ser un booleano válido (true/false)"
    elif isinstance(valor, int):
        return bool(valor), None
    else:
        return None, f"El campo '{campo_nombre}' debe ser un booleano válido"

sensores_bp = Blueprint('sensores', __name__)

# Obtener colecciones desde database
sensores_collection = get_sensores_collection()
medidas_collection = get_medidas_collection()

def convertir_sensor_a_json(sensor):
    """Convierte un documento de sensor de MongoDB a JSON serializable"""
    if not sensor:
        return None
        
    sensor_convertido = {
        "sensor_id": str(sensor['_id']),
        "sensor": sensor.get('nombre', ''),
        "tipo_sensor": sensor.get('tipo', ''),
        "activo": sensor.get('activo', False),
        "created_at": sensor.get('created_at'),
        "updated_at": sensor.get('updated_at'),
        "campos": []
    }
    
    # Convertir campos si existen
    if 'campos' in sensor:
        for campo in sensor['campos']:
            campo_convertido = {
                "campo_id": str(campo['_id']),
                "nombre_campo": campo.get('nombre_campo', ''),
                "tipo_campo": campo.get('tipo_campo', ''),
                "activo": campo.get('activo', True)
            }
            sensor_convertido['campos'].append(campo_convertido)
    
    # Convertir fechas a string si existen
    if sensor_convertido['created_at']:
        sensor_convertido['created_at'] = sensor_convertido['created_at'].isoformat()
    if sensor_convertido['updated_at']:
        sensor_convertido['updated_at'] = sensor_convertido['updated_at'].isoformat()
    
    return sensor_convertido

@sensores_bp.route('/agregar_sensor', methods=['POST'])
def agregar_sensor():
    """Agrega o actualiza un sensor con sus campos. Espera JSON con sensor, tipo_sensor, activo, campos."""
    if sensores_collection is None:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        sensor_nombre = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo_raw = data.get("activo", True)
        campos_nuevos = data.get("campos", [])

        if not sensor_nombre or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400

        # Validación robusta del campo booleano 'activo'
        activo, error_activo = validar_booleano(activo_raw, "activo", True)
        if error_activo:
            return jsonify({"error": error_activo}), 400

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
                
                # Validar el campo activo del campo anidado
                campo_activo_raw = campo.get("activo", True)
                campo_activo, error_campo_activo = validar_booleano(
                    campo_activo_raw, f"activo del campo '{nombre_campo}'", True
                )
                if error_campo_activo:
                    return jsonify({"error": error_campo_activo}), 400
                
                campo_existente = sensores_collection.find_one(
                    {"_id": sensor_id, "campos.nombre_campo": nombre_campo}
                )
                if campo_existente:
                    sensores_collection.update_one(
                        {"_id": sensor_id, "campos.nombre_campo": nombre_campo},
                        {"$set": {"campos.$.tipo_campo": tipo_campo, "campos.$.activo": campo_activo}}
                    )
                else:
                    nuevo_campo_doc = {
                        "_id": ObjectId(),
                        "nombre_campo": nombre_campo,
                        "tipo_campo": tipo_campo,
                        "activo": campo_activo
                    }
                    sensores_collection.update_one(
                        {"_id": sensor_id},
                        {"$push": {"campos": nuevo_campo_doc}}
                    )
            mensaje = f"Sensor '{sensor_nombre}' actualizado"
        else:
            campos_doc = []
            for c in campos_nuevos:
                if c.get("nombre_campo") and c.get("tipo_campo"):
                    # Validar el campo activo del campo anidado
                    campo_activo_raw = c.get("activo", True)
                    campo_activo, error_campo_activo = validar_booleano(
                        campo_activo_raw, f"activo del campo '{c.get('nombre_campo')}'", True
                    )
                    if error_campo_activo:
                        return jsonify({"error": error_campo_activo}), 400
                    
                    campos_doc.append({
                        "_id": ObjectId(),
                        "nombre_campo": c.get("nombre_campo"),
                        "tipo_campo": c.get("tipo_campo"),
                        "activo": campo_activo
                    })

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

        return jsonify({
            "status": "ok", 
            "mensaje": mensaje, 
            "sensor_id": str(sensor_id)
        })

    except Exception as e:
        log_error(e, "agregar_sensor")
        return jsonify({"error": str(e)}), 500

@sensores_bp.route('/editar_sensor/<string:sensor_id>', methods=['PUT'])
def editar_sensor(sensor_id):
    """Edita un sensor existente por ID. Puede activar/desactivar o actualizar nombre, tipo y campos."""
    if sensores_collection is None:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        data = request.get_json()
        obj_id = ObjectId(sensor_id)
        if 'activo' in data and len(data) == 1:
            activo_raw = data.get("activo")
            activo, error_activo = validar_booleano(activo_raw, "activo")
            if error_activo:
                return jsonify({"error": error_activo}), 400
            
            sensores_collection.update_one(
                {"_id": obj_id}, 
                {"$set": {"activo": activo, "updated_at": datetime.utcnow()}}
            )
            estado = "activado" if activo else "desactivado"
            return jsonify({"status": "ok", "mensaje": f"Sensor {estado} correctamente"})
        sensor_nombre = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo_raw = data.get("activo", True)
        campos = data.get("campos", [])
        
        if not sensor_nombre or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400
            
        # Validación robusta del campo booleano 'activo'
        activo, error_activo = validar_booleano(activo_raw, "activo", True)
        if error_activo:
            return jsonify({"error": error_activo}), 400
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
                
            # Validar el campo activo del campo anidado
            campo_activo_raw = campo.get("activo", True)
            campo_activo, error_campo_activo = validar_booleano(
                campo_activo_raw, f"activo del campo '{nombre_campo}'", True
            )
            if error_campo_activo:
                return jsonify({"error": error_campo_activo}), 400
                
            if campo_id_str:
                campo_obj_id = ObjectId(campo_id_str)
                sensores_collection.update_one(
                    {"_id": obj_id, "campos._id": campo_obj_id},
                    {"$set": {
                        "campos.$.nombre_campo": nombre_campo, 
                        "campos.$.tipo_campo": tipo_campo, 
                        "campos.$.activo": campo_activo
                    }}
                )
            else:
                nuevo_campo_doc = {
                    "_id": ObjectId(),
                    "nombre_campo": nombre_campo,
                    "tipo_campo": tipo_campo,
                    "activo": campo_activo
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
    """Elimina definitivamente un sensor y todas sus medidas asociadas."""
    if sensores_collection is None:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        obj_id = ObjectId(sensor_id)
        if medidas_collection is not None:
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
    """Lista todos los sensores con sus campos, convirtiendo a formato JSON serializable."""
    if sensores_collection is None:
        return jsonify({"error": "Conexión a la base de datos no disponible"}), 503
    try:
        sensores = list(sensores_collection.find())
        
        # Convertir todos los sensores a JSON serializable
        sensores_convertidos = [convertir_sensor_a_json(sensor) for sensor in sensores]
        
        return jsonify(sensores_convertidos)
        
    except Exception as e:
        log_error(e, "listar_sensores_campos")
        return jsonify({"error": str(e)}), 500

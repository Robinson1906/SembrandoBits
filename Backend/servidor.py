from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS
import os
from dotenv import load_dotenv
import socket

load_dotenv(dotenv_path='../.env')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ===========================
# Configuración MySQL
# ===========================
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# ===========================
# Helpers
# ===========================
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def log_error(e, contexto=""):
    print(f"❌ ERROR {contexto}: {e}")

# ===========================
# Rutas
# ===========================

@app.route("/")
def home():
    return "🌐 Servidor Flask con MySQL dinámico 🚀"

# ===========================
# AGREGAR SENSOR CON CAMPOS
# ===========================
@app.route("/agregar_sensor", methods=["POST"])
def agregar_sensor():
    try:
        data = request.get_json()
        sensor = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo = data.get("activo", True)
        campos = data.get("campos", [])

        if not sensor or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el sensor ya existe
        cursor.execute("SELECT id, activo FROM sensores_registrados WHERE nombre=%s", (sensor,))
        row = cursor.fetchone()

        if row:
            sensor_id, sensor_activo = row
            cursor.execute("UPDATE sensores_registrados SET tipo=%s, activo=%s WHERE id=%s",
                           (tipo_sensor, activo, sensor_id))
            mensaje = f"Sensor '{sensor}' actualizado"
        else:
            cursor.execute("INSERT INTO sensores_registrados (nombre, tipo, activo) VALUES (%s, %s, %s) RETURNING id",
                           (sensor, tipo_sensor, activo))
            sensor_id = cursor.fetchone()[0]
            mensaje = f"Sensor '{sensor}' agregado correctamente"

        # Insertar/actualizar campos
        for campo in campos:
            nombre_campo = campo.get("nombre_campo")
            tipo_campo = campo.get("tipo_campo")
            if not nombre_campo or not tipo_campo:
                continue

            cursor.execute("SELECT id FROM campos_sensor WHERE sensor_id=%s AND nombre_campo=%s",
                           (sensor_id, nombre_campo))
            campo_row = cursor.fetchone()
            if campo_row:
                cursor.execute("UPDATE campos_sensor SET tipo_campo=%s, activo=TRUE WHERE id=%s",
                               (tipo_campo, campo_row[0]))
            else:
                cursor.execute(
                    "INSERT INTO campos_sensor (sensor_id, nombre_campo, tipo_campo, activo) VALUES (%s, %s, %s, TRUE)",
                    (sensor_id, nombre_campo, tipo_campo)
                )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "ok", "mensaje": mensaje, "sensor_id": sensor_id})

    except Exception as e:
        log_error(e, "agregar_sensor")
        return jsonify({"error": str(e)}), 500

# ===========================
# EDITAR SENSOR (ahora permite editar solo el estado)
# ===========================
@app.route("/editar_sensor/<int:sensor_id>", methods=["PUT"])
def editar_sensor(sensor_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Si solo se envía el campo activo (para toggle)
        if 'activo' in data and len(data) == 1:
            activo = data.get("activo")
            cursor.execute("UPDATE sensores_registrados SET activo=%s WHERE id=%s",
                           (activo, sensor_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            estado = "activado" if activo else "desactivado"
            return jsonify({"status": "ok", "mensaje": f"Sensor {estado} correctamente"})

        # Edición completa del sensor
        sensor = data.get("sensor")
        tipo_sensor = data.get("tipo_sensor")
        activo = data.get("activo", True)
        campos = data.get("campos", [])

        if not sensor or not tipo_sensor:
            return jsonify({"error": "Se requiere 'sensor' y 'tipo_sensor'"}), 400

        # Actualizar sensor
        cursor.execute("UPDATE sensores_registrados SET nombre=%s, tipo=%s, activo=%s WHERE id=%s",
                       (sensor, tipo_sensor, activo, sensor_id))

        # Actualizar campos
        for campo in campos:
            campo_id = campo.get("campo_id")
            nombre_campo = campo.get("nombre_campo")
            tipo_campo = campo.get("tipo_campo")
            if campo_id:
                cursor.execute("UPDATE campos_sensor SET nombre_campo=%s, tipo_campo=%s, activo=TRUE WHERE id=%s",
                               (nombre_campo, tipo_campo, campo_id))
            else:
                cursor.execute(
                    "INSERT INTO campos_sensor (sensor_id, nombre_campo, tipo_campo, activo) VALUES (%s, %s, %s, TRUE)",
                    (sensor_id, nombre_campo, tipo_campo)
                )

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "ok", "mensaje": f"Sensor {sensor_id} actualizado"})
    except Exception as e:
        log_error(e, "editar_sensor")
        return jsonify({"error": str(e)}), 500

# ===========================
# ELIMINAR SENSOR DEFINITIVAMENTE
# ===========================
@app.route("/eliminar_sensor_definitivo/<int:sensor_id>", methods=["DELETE"])
def eliminar_sensor_definitivo(sensor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primero eliminar las medidas relacionadas
        cursor.execute("DELETE FROM medidas WHERE campo_id IN (SELECT id FROM campos_sensor WHERE sensor_id = %s)", (sensor_id,))
        
        # Luego eliminar los campos del sensor
        cursor.execute("DELETE FROM campos_sensor WHERE sensor_id = %s", (sensor_id,))
        
        # Finalmente eliminar el sensor
        cursor.execute("DELETE FROM sensores_registrados WHERE id = %s", (sensor_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "ok", "mensaje": f"Sensor {sensor_id} eliminado definitivamente"})
        
    except Exception as e:
        log_error(e, "eliminar_sensor_definitivo")
        return jsonify({"error": str(e)}), 500

# ===========================
# LISTAR SENSORES AGRUPADOS
# ===========================
@app.route("/listar_sensores_campos", methods=["GET"])
def listar_sensores_campos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT s.id AS sensor_id, s.nombre AS sensor, s.tipo AS tipo_sensor, s.activo,
                   c.id AS campo_id, c.nombre_campo, c.tipo_campo, c.activo AS campo_activo
            FROM sensores_registrados s
            LEFT JOIN campos_sensor c ON s.id = c.sensor_id
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Agrupar por sensor
        sensores_dict = {}
        for row in rows:
            sid = row["sensor_id"]
            if sid not in sensores_dict:
                sensores_dict[sid] = {
                    "sensor_id": sid,
                    "sensor": row["sensor"],
                    "tipo_sensor": row["tipo_sensor"],
                    "activo": row["activo"],
                    "campos": []
                }
            if row["campo_id"]:
                sensores_dict[sid]["campos"].append({
                    "campo_id": row["campo_id"],
                    "nombre_campo": row["nombre_campo"],
                    "tipo_campo": row["tipo_campo"],
                    "activo": row["campo_activo"]
                })

        return jsonify(list(sensores_dict.values()))
    except Exception as e:
        log_error(e, "listar_sensores_campos")
        return jsonify({"error": str(e)}), 500

# ===========================
# GUARDAR MEDIDAS
# ===========================
@app.route("/guardar", methods=["POST"])
def guardar_medidas():
    try:
        data = request.get_json()
        if not data or "measures" not in data:
            return jsonify({"error": "El JSON debe contener 'measures'"}), 400

        measures = data["measures"]
        conn = get_db_connection()
        cursor = conn.cursor()

        for sensor_name, lecturas in measures.items():
            cursor.execute("SELECT id FROM sensores_registrados WHERE nombre=%s AND activo=TRUE", (sensor_name,))
            sensor_row = cursor.fetchone()
            if not sensor_row:
                continue  # Saltar sensores inactivos
            sensor_id = sensor_row[0]

            for lectura in lecturas:
                valor = lectura.get("value")
                detalle = lectura.get("detail")
                cursor.execute("SELECT id FROM campos_sensor WHERE nombre_campo=%s AND sensor_id=%s AND activo=TRUE",
                               (detalle, sensor_id))
                campo_row = cursor.fetchone()
                if not campo_row:
                    continue  # Saltar campos inactivos
                campo_id = campo_row[0]

                cursor.execute(
                    "INSERT INTO medidas (sensor_id, campo_id, valor, fecha) VALUES (%s, %s, %s, NOW())",
                    (sensor_id, campo_id, valor)
                )

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "ok", "mensaje": "Medidas insertadas correctamente"})
    except Exception as e:
        log_error(e, "guardar_medidas")
        return jsonify({"error": str(e)}), 500

# ===========================
# LEER MEDIDAS
# ===========================
@app.route("/medidas", methods=["GET"])
def obtener_medidas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id, s.nombre AS sensor, c.nombre_campo, m.valor, m.fecha
            FROM medidas m
            JOIN sensores_registrados s ON m.sensor_id = s.id
            JOIN campos_sensor c ON m.campo_id = c.id
            ORDER BY m.fecha DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        log_error(e, "obtener_medidas")
        return jsonify({"error": str(e)}), 500

# ===========================
# INICIO DEL SERVIDOR
# ===========================
if __name__ == "__main__":
    # Debug: Verificar conexión a internet
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✅ Conexión a internet verificada.")
    except OSError:
        print("❌ No se pudo verificar la conexión a internet.")

    try:
        conn = get_db_connection()
        conn.close()
        print("✅ Conexión a la base de datos exitosa.")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        
    app.run(host="0.0.0.0", port=5000, debug=True)
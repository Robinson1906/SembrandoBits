# database.py
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from dotenv import load_dotenv
from pathlib import Path
import ssl
import time

# Parámetros de reintentos configurables vía entorno
RETRY_ATTEMPTS = int(os.getenv("DB_RETRY_ATTEMPTS", "5"))  # Número de reintentos antes de rendirse
RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "5"))        # Segundos entre reintentos
ALLOW_START_WITHOUT_DB = os.getenv("ALLOW_START_WITHOUT_DB", "1") == "1"  # Permitir que el servidor arranque aunque no conecte

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGO_URI")

# Variables globales de la base de datos
client = None
db = None
sensores_collection = None
medidas_collection = None


def _intento_conectar(uri: str):
    """Realiza un intento de conexión normal y alternativa; retorna True si tuvo éxito."""
    global client, db, sensores_collection, medidas_collection
    try:
        client = MongoClient(
            uri,
            server_api=ServerApi('1'),
            tls=True,
            tlsAllowInvalidCertificates=True,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000,
            retryWrites=True
        )
        client.admin.command('ping')
        print("✅ Conexión a MongoDB Atlas exitosa.")
        db = client.iotdb
        sensores_collection = db.sensores
        medidas_collection = db.medidas
        return True
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB (modo TLS): {e}")
        # Intentar alternativa sin TLS
        try:
            if uri and "@" in uri:
                partes = uri.split('@')
                credenciales = partes[0].replace('mongodb+srv://', '')
                cluster_info = partes[1]
                alt_uri = f"mongodb://{credenciales}@{cluster_info}&ssl=false"
                print("⚠️  Intentando conexión alternativa sin SSL...")
                client = MongoClient(
                    alt_uri,
                    server_api=ServerApi('1'),
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000
                )
                client.admin.command('ping')
                print("✅ Conexión alternativa exitosa (sin SSL).")
                db = client.iotdb
                sensores_collection = db.sensores
                medidas_collection = db.medidas
                return True
        except Exception as alt_e:
            print(f"❌ Error en conexión alternativa: {alt_e}")
        return False

def inicializar_base_datos():
    """Inicializa la conexión con reintentos. No aborta el proceso inmediatamente.
    Retorna True si logró conectar, False si agotó reintentos.
    """
    objetivo = None
    if MONGO_URI and "@" in MONGO_URI:
        try:
            objetivo = MONGO_URI.split('@')[1].split('/')[0]
        except Exception:
            objetivo = "(parse error)"
    else:
        objetivo = 'URI no configurada'
    print(f"🔗 Intentando conectar con: {objetivo}")

    if not MONGO_URI:
        print("⚠️  MONGO_URI no definida. Saltando conexión inicial.")
        return False

    for intento in range(1, RETRY_ATTEMPTS + 1):
        print(f"🔁 Intento {intento}/{RETRY_ATTEMPTS} de conexión...")
        if _intento_conectar(MONGO_URI):
            return True
        if intento < RETRY_ATTEMPTS:
            print(f"⏳ Esperando {RETRY_DELAY}s antes del próximo intento...")
            time.sleep(RETRY_DELAY)

    print("❌ No se logró conectar a MongoDB tras reintentos.")
    if ALLOW_START_WITHOUT_DB:
        print("🚧 Continuando en modo degradado (sin base de datos).")
    else:
        print("🛑 Saliendo porque ALLOW_START_WITHOUT_DB=0")
        # No forzamos exit aquí para que NSSM vea un proceso 'vivo' si se maneja arriba.
    return False

def get_sensores_collection():
    """Retorna la colección de sensores si está conectada, de lo contrario None."""
    return sensores_collection if sensores_collection is not None else None

def get_medidas_collection():
    """Retorna la colección de medidas si está conectada, de lo contrario None."""
    return medidas_collection if medidas_collection is not None else None

def get_db():
    """Retorna la base de datos si está conectada, de lo contrario None."""
    return db if db is not None else None

def get_client():
    """Retorna el cliente de MongoDB si está conectado, de lo contrario None."""
    return client if client is not None else None

# Helper function para logs de error
def log_error(e, contexto=""):
    """Registra un error en la consola con el contexto proporcionado."""
    print(f"❌ ERROR {contexto}: {e}")

# Inicializar la base de datos al importar el módulo
inicializar_base_datos()
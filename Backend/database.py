# database.py
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from dotenv import load_dotenv
from pathlib import Path
import ssl

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
MONGO_URI = os.getenv("MONGO_URI")

# Variables globales de la base de datos
client = None
db = None
sensores_collection = None
medidas_collection = None

def inicializar_base_datos():
    global client, db, sensores_collection, medidas_collection
    
    try:
        # Configurar opciones SSL específicas
        client = MongoClient(
            MONGO_URI,
            server_api=ServerApi('1'),
            tls=True,
            tlsAllowInvalidCertificates=True,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000,
            retryWrites=True
        )
        
        # Enviar un ping para confirmar una conexión exitosa
        client.admin.command('ping')
        print("✅ Conexión a MongoDB Atlas exitosa.")
        
        # Definir la base de datos y las colecciones
        db = client.iotdb
        sensores_collection = db.sensores
        medidas_collection = db.medidas
        
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        # Intenta una conexión alternativa sin SSL
        try:
            print("⚠️  Intentando conexión alternativa sin SSL...")
            alt_uri = MONGO_URI.replace("mongodb+srv://", "mongodb://") + "&ssl=false"
            client = MongoClient(alt_uri, server_api=ServerApi('1'))
            client.admin.command('ping')
            print("✅ Conexión alternativa exitosa (sin SSL).")
            
            db = client.SembrandoBits 
            sensores_collection = db.sensores
            medidas_collection = db.medidas
            
            return True
            
        except Exception as alt_e:
            print(f"❌ Error en conexión alternativa: {alt_e}")
            return False

def get_sensores_collection():
    return sensores_collection

def get_medidas_collection():
    return medidas_collection

def get_db():
    return db

def get_client():
    return client

# Helper function para logs de error
def log_error(e, contexto=""):
    print(f"❌ ERROR {contexto}: {e}")

# Inicializar la base de datos al importar el módulo
inicializar_base_datos()
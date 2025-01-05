from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "chat_history")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "messages")

class MongoDBCheckpointer:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION_NAME]
    
    def save_message(self, thread_id: str, user: str, message: str, useful_docs: List[str] = None, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        document = {
            "thread_id": thread_id,
            "user": user,
            "message": message,
            "useful_docs": useful_docs if useful_docs else [],
            "timestamp": timestamp
        }
        self.collection.insert_one(document)
    
    def get_history(self, thread_id: str, user: str = None, limit: int = 100) -> List[Dict]:
        query = {"thread_id": thread_id}
        if user:
            query["user"] = user
        return list(
            self.collection.find(query).sort("timestamp", -1).limit(limit)
        )
    
    def get_thread_documents(self, thread_id: str) -> set[str]:
        """
        Obtiene todos los documentos útiles únicos de una conversación.
        
        Args:
            thread_id (str): ID del hilo de conversación
            
        Returns:
            set[str]: Conjunto de nombres de documentos únicos
        """
        # Buscar todos los mensajes del bot en este hilo que tengan documentos útiles
        query = {
            "thread_id": thread_id,
            "user": "bot",
            "useful_docs": {"$exists": True, "$ne": []}
        }
        
        # Usar agregación para obtener todos los documentos únicos
        docs = self.collection.find(query, {"useful_docs": 1})
        
        # Crear un set con todos los documentos
        all_docs = set()
        for doc in docs:
            all_docs.update(doc.get("useful_docs", []))
            
        return all_docs 
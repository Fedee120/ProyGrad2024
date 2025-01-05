### Build Index
import os
from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Milvus
MILVUS_URL = os.getenv("MILVUS_STANDALONE_URL", "localhost:19530")
COLLECTION_NAME = "real_collection"

# Set embeddings
embd = OpenAIEmbeddings(model="text-embedding-3-small")

def init_db():
    """
    Inicializa la base de datos y retorna el retriever
    """
    print("Inicializando nueva base de datos...")
    
    # Crear y retornar el retriever de Milvus
    vectorstore = Milvus(
        embedding_function=embd,
        connection_args={"uri": MILVUS_URL},
        collection_name=COLLECTION_NAME
    )
    
    return vectorstore.as_retriever()

def load_db():
    """
    Carga la base de datos existente o crea una nueva si no existe
    """
    try:
        print("Intentando conectar a Milvus...")
        vectorstore = Milvus(
            embedding_function=embd,
            connection_args={"uri": MILVUS_URL},
            collection_name=COLLECTION_NAME
        )
        print("Conexión exitosa a Milvus")
        return vectorstore.as_retriever()
    except Exception as e:
        print(f"Error al conectar a Milvus: {e}")
        print("Inicializando nueva base de datos...")
        return init_db()

if __name__ == "__main__":
    # Inicializar la base de datos
    retriever = load_db()

    # probar el retriever
    question = "¿Que es un agente de IA?"
    docs = retriever.invoke(question)
    print(docs)
    print("¡Proceso completado!")
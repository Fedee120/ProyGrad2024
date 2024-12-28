# rag_factory.py
from rags.openai.rag import RAG

class RAGFactory:
    @staticmethod
    def create_rag(URI, COLLECTION_NAME, search_kwargs, search_type, embeddings_model_name):
        """
        Crea y retorna una instancia de RAG con los parámetros deseados.
        
        :param URI: URI de conexión a Milvus
        :param COLLECTION_NAME: Nombre de la colección en Milvus
        :param search_kwargs: Parámetros de búsqueda para la retriever
        :param search_type: Tipo de búsqueda (p.ej. "mmr", "similarity", etc.)
        :param embeddings_model_name: Nombre del modelo de embeddings OpenAI
        """
        return RAG(
            URI=URI,
            COLLECTION_NAME=COLLECTION_NAME,
            search_kwargs=search_kwargs,
            search_type=search_type,
            embeddings_model_name=embeddings_model_name
        )

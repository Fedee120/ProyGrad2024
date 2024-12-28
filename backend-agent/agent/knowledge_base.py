from dotenv import load_dotenv
import os
from langchain.schema import BaseMessage
from rags.factory.RAGFactory import RAGFactory

class KnowledgeBase():
    def search(self, query: str, history: list[BaseMessage] = None) -> tuple[str, list[dict]]:
        """
        Busca y genera una respuesta basada en la consulta proporcionada utilizando un sistema RAG (Retrieval-Augmented Generation).

        Args:
            query (str): La consulta o pregunta del usuario.
            history (List[BaseMessage], opcional): Historial de mensajes previos para contexto. Por defecto es None.

        Returns:
            dict: Respuesta generada junto con los artefactos relacionados.
        """
        load_dotenv()
        rag = RAGFactory.create_rag(
            URI=os.getenv("MILVUS_STANDALONE_URL"), 
            COLLECTION_NAME="real_collection", 
            search_kwargs={"k": 4, "fetch_k": 20, "ef": 100}, 
            search_type="mmr", 
            embeddings_model_name="text-embedding-3-small"
        )
        return rag.generate_answer(query, history)

if __name__ == "__main__":
    kb = KnowledgeBase()
    result = kb.search("¿Que es la IA?")
    print(result) 
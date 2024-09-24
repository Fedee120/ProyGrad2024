from rags.IRAG import IRAG
from rags.openai.rag import RAG

class RAGFactory:
    @staticmethod
    def create_rag(URI: str, COLLECTION_NAME: str, search_kwargs: dict, search_type: str, llm_model_name: str, embeddings_model_name: str) -> IRAG:
        return RAG(
            URI=URI,
            COLLECTION_NAME=COLLECTION_NAME,
            search_kwargs=search_kwargs,
            search_type=search_type,
            llm_model_name=llm_model_name,
            embeddings_model_name=embeddings_model_name
        )

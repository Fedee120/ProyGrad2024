from dotenv import load_dotenv
import os
from typing import List
from langchain_core.messages import BaseMessage
from langsmith import traceable

from rags.factory.RAGFactory import RAGFactory

class KnowledgeBase():
    @traceable
    def search(self, query: str, history: List[BaseMessage] = None):
        rag = RAGFactory.create_rag(
            URI=os.getenv("MILVUS_STANDALONE_URL"), 
            COLLECTION_NAME="real_collection", 
            search_kwargs={"k": 4, "fetch_k": 20, "ef": 100}, 
            search_type="mmr", 
            embeddings_model_name="text-embedding-3-small")
        return rag.generate_answer(query, history)

if __name__ == "__main__":
    load_dotenv()

    tool = KnowledgeBase()
    print(tool.search("¿Cuál es el color del cielo?"))

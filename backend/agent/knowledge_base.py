from dotenv import load_dotenv
import os
from typing import List
from langchain_core.messages import BaseMessage

from rags.factory.RAGFactory import RAGFactory

class KnowledgeBase():
    def search(self, query: str, history: List[BaseMessage] = None):
        load_dotenv()
        rag = RAGFactory.create_rag(
            URI=os.getenv("MILVUS_STANDALONE_URL"), 
            COLLECTION_NAME="real_collection", 
            search_kwargs={"k": 5}, 
            search_type="mmr", 
            embeddings_model_name="text-embedding-3-small")
        return rag.generate_answer(query, history)

if __name__ == "__main__":
    tool = KnowledgeBase()
    print(tool.search("¿Cuál es el color del cielo?"))

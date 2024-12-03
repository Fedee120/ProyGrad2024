from dotenv import load_dotenv
import os

from rags.factory.RAGFactory import RAGFactory

class KnowledgeBase():
    def search(self, query: str):
        load_dotenv()
        rag = RAGFactory.create_rag(
            URI=os.getenv("MILVUS_STANDALONE_URL"), 
            COLLECTION_NAME="real_collection", 
            search_kwargs={"k": 10}, 
            search_type="mmr", 
            llm_model_name="gpt-4o", 
            embeddings_model_name="text-embedding-3-small")
        return rag.generate_answer(query)

if __name__ == "__main__":
    tool = KnowledgeBase()
    print(tool.search("¿Cuál es el color del cielo?"))

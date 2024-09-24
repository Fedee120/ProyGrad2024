from typing import Optional, Type
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from rags.factory.RAGFactory import RAGFactory

class KnowledgeBaseInput(BaseModel):
    query: str = Field(description="query")
    fallback: str = Field(description="Fallback answer")

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class KnowledgeBase(BaseTool):
    name: str = "Knowledge_Base"
    description: str = "Útil para responder preguntas."
    args_schema: Type[BaseModel] = KnowledgeBaseInput
    return_direct: bool = True

    def _run(
        self, query: str, fallback: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        rag = RAGFactory.create_rag(
            URI="http://standalone:19530", 
            COLLECTION_NAME="real_collection", 
            search_kwargs={"k": 10}, 
            search_type="mmr", 
            llm_model_name="gpt-4o-mini", 
            embeddings_model_name="text-embedding-3-small")
        return rag.generate_answer(query)
    
def create_tool():
    return KnowledgeBase()

if __name__ == "__main__":
    tool = create_tool()
    print(tool.run({"query": "¿Cuál es el color del cielo?", "fallback": "No sé"}).get("answer"))

from typing import List
import os
from pydantic import BaseModel
from langchain_core.documents import Document
from langsmith import traceable

class SearchResult(BaseModel):
    """Resultado de una única consulta de búsqueda"""
    query: str
    documents: List[Document]

class FormatResultsStep:
    @traceable
    def format_search_results(self, results: List[SearchResult]) -> str:
        """
        Formatea los resultados de búsqueda en un formato legible
        
        Args:
            results: Lista de resultados de búsqueda
            
        Returns:
            str: Resultados formateados como texto
        """
        formatted = []
        for result in results:
            for doc in result.documents:
                metadata_str = f"---- Context METADATA ----\n{str({**doc.metadata, 'source': os.path.basename(doc.metadata.get('source', ''))} if doc.metadata else {})}"
                content_str = f"---- Context Start ----\n{doc.page_content}\n---- Context End ----"
                formatted.append(f"{metadata_str}\n{content_str}")
        return "\n\n".join(formatted) 
    

if __name__ == "__main__":
    formatter = FormatResultsStep()
    results = [SearchResult(query="query1", documents=[Document(page_content="content1", metadata={"source": "source1"}), Document(page_content="content2", metadata={"source": "source2"})])]
    formatted_results = formatter.format_search_results(results)
    print(formatted_results)

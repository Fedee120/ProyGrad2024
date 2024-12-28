# post_processing.py

from typing import List
from langchain.schema import Document

def post_process(docs: List[Document], user_query: str) -> str:
    """
    Lógica de post-procesamiento. 
    Podrías hacer fusión de documentos, resúmenes, clasificación adicional, etc.
    Retorna un texto final que condensa la información relevante.
    """
    # Ejemplo mínimo: concatenar contenido de los documentos
    # y retornar un string (en un caso real, aquí se usaría un LLM para hacer un summary).
    
    if not docs:
        return "No se encontraron documentos relevantes."

    contents = [doc.page_content for doc in docs]
    combined_text = "\n\n".join(contents)
    final_text = f"A continuación tienes la información recuperada:\n{combined_text}"
    
    return final_text

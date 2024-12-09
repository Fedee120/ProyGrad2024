from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

def semantic_split(documents):
    """
    Divide los documentos usando chunking semántico basado en embeddings.
    """
    text_splitter = SemanticChunker(
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        breakpoint_threshold_type="standard_deviation",  # Usa detección de cambios semánticos basada en gradiente
    )
    
    return text_splitter.split_documents(documents) 
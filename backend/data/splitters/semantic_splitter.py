from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

def semantic_split(documents):
    """
    Divide los documentos usando chunking semántico basado en embeddings.
    Muestra una barra de progreso durante el proceso.
    Preserva todos los metadatos del documento original en cada chunk.
    """
    text_splitter = SemanticChunker(
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
        breakpoint_threshold_type="standard_deviation",
        breakpoint_threshold_amount=1.0
    )
    
    # Modificamos el método de división para mostrar una barra de progreso
    # Como SemanticChunker no tiene un método directo para procesar con tqdm,
    # haremos un workaround procesando los documentos en lotes y mostrando progreso
    
    result_chunks = []
    # Mostrar barra de progreso durante el procesamiento
    for doc in tqdm(documents, desc="Aplicando chunking semántico", unit="doc"):
        # Dividir cada documento individualmente
        doc_chunks = text_splitter.split_documents([doc])
        
        # Asegurarse de que todos los metadatos se conserven en cada chunk
        metadata_keys = ['title', 'authors', 'publication_year', 'source', 'page', 'total_pages']
        for chunk in doc_chunks:
            for key in metadata_keys:
                if key not in chunk.metadata and key in doc.metadata:
                    chunk.metadata[key] = doc.metadata[key]
        
        result_chunks.extend(doc_chunks)
    
    return result_chunks 
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
        for chunk in doc_chunks:
            # Verificar que los metadatos importantes estén preservados
            if 'title' not in chunk.metadata and 'title' in doc.metadata:
                chunk.metadata['title'] = doc.metadata['title']
            if 'authors' not in chunk.metadata and 'authors' in doc.metadata:
                chunk.metadata['authors'] = doc.metadata['authors']
            if 'publication_year' not in chunk.metadata and 'publication_year' in doc.metadata:
                chunk.metadata['publication_year'] = doc.metadata['publication_year']
            
            # Otros metadatos importantes para la referencia
            if 'source' not in chunk.metadata and 'source' in doc.metadata:
                chunk.metadata['source'] = doc.metadata['source']
            if 'page' not in chunk.metadata and 'page' in doc.metadata:
                chunk.metadata['page'] = doc.metadata['page']
            if 'total_pages' not in chunk.metadata and 'total_pages' in doc.metadata:
                chunk.metadata['total_pages'] = doc.metadata['total_pages']
            
        result_chunks.extend(doc_chunks)
    
    return result_chunks 
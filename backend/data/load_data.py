import os
from dotenv import load_dotenv
from agent.rag import RAG
from langchain_community.document_loaders import PyMuPDFLoader
from data.splitters.semantic_splitter import semantic_split
import re
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import concurrent.futures
from tqdm import tqdm

load_dotenv()

class DocumentMetadata(BaseModel):
    """Estructura para los metadatos de un documento"""
    title: str = Field(description="El título completo del documento")
    authors: List[str] = Field(description="Lista de autores del documento")
    publication_year: Optional[int] = Field(description="Año de publicación del documento como número entero")

def extract_metadata(document_text: str) -> DocumentMetadata:
    """
    Extrae metadatos (título, autores, año) de un documento usando LLM.
    Sólo envía los primeros y últimos 1K tokens al modelo.
    """
    # Dividir el texto en tokens aproximadamente (asumiendo que un token es ~4 caracteres)
    char_limit = 1000 * 4  # ~1000 tokens
    
    # Obtener primeros y últimos 1K tokens aproximados
    start_text = document_text[:char_limit]
    end_text = document_text[-char_limit:] if len(document_text) > char_limit else ""
    
    sample_text = f"INICIO DEL DOCUMENTO:\n{start_text}\n\nFINAL DEL DOCUMENTO:\n{end_text}"
    
    # Crear el prompt para extraer metadatos
    prompt = ChatPromptTemplate.from_template("""
    Eres un asistente especializado en extraer metadatos precisos de documentos académicos.
    Analiza cuidadosamente el texto proporcionado y extrae la siguiente información:
    
    1. Título completo del documento
    2. Lista de todos los autores (nombres completos si es posible)
    3. Año de publicación (solo el año como número entero, ej: 2023)
    
    Si algún dato no está disponible o no puedes identificarlo con certeza, déjalo vacío o como null.
    El texto del documento es el siguiente:
    
    {document_text}
    """)
    
    # Usar ChatOpenAI con la versión más reciente
    model = ChatOpenAI(temperature=0, model="gpt-4o")
    
    # Crear la cadena con salida estructurada
    extraction_chain = prompt | model.with_structured_output(DocumentMetadata)
    
    # Extraer metadatos
    return extraction_chain.invoke({"document_text": sample_text})

def clean_text(text: str) -> str:
    """Limpia el texto eliminando caracteres no deseados y espacios múltiples."""
    # Reemplazar saltos de línea múltiples por uno solo
    text = re.sub(r'\n+', ' ', text)
    # Reemplazar espacios múltiples por uno solo
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()

def get_docs(path):
    loader = PyMuPDFLoader(path)
    docs = loader.load()
    
    # Limpiar el texto de cada documento
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
        
        # Extraer metadatos avanzados usando LLM
        metadata = extract_metadata(doc.page_content)
        
        # Añadir metadatos al documento
        doc.metadata["title"] = metadata.title
        doc.metadata["authors"] = metadata.authors
        doc.metadata["publication_year"] = metadata.publication_year
        
    return docs

def load_data(rag: RAG):
    print("Loading and extracting documents")
    samples = os.path.join(os.path.dirname(__file__), "raw/")
    pdfs = [f for f in os.listdir(samples) if f.endswith(".pdf")]
    paths = [os.path.join(samples, f) for f in pdfs]
    
    docs = []
    
    # Procesamiento en paralelo de PDFs con barra de progreso
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Crear tareas para cada PDF y mostrar progreso con tqdm
        futures = {executor.submit(get_docs, path): path for path in paths}
        
        # Procesar resultados a medida que se completan con barra de progreso
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), 
                           desc="Procesando PDFs", unit="doc"):
            path = futures[future]
            try:
                # Añadir documentos procesados a la lista
                docs.extend(future.result())
                print(f"Procesado: {os.path.basename(path)}")
            except Exception as e:
                print(f"Error procesando {os.path.basename(path)}: {e}")
    
    print("Extracted docs:", len(docs))

    print("Splitting documents using semantic chunking")
    # Aplicar chunking con barra de progreso
    splits = semantic_split(docs)
    print("Splitted docs:", len(splits))

    print("Adding documents to collection")
    # Añadir documentos a la colección con barra de progreso
    rag.add_documents(splits)
    print("Added docs to collection")

if __name__ == "__main__":
    rag = RAG()
    rag.delete_all_documents()
    load_data(rag)
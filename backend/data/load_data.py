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
import time

load_dotenv()

class DocumentMetadata(BaseModel):
    """Estructura para los metadatos de un documento"""
    title: str = Field(description="El título completo del documento")
    authors: List[str] = Field(description="Lista de autores del documento")
    publication_year: Optional[int] = Field(description="Año de publicación del documento como número entero")

def extract_document_metadata(document_path: str) -> DocumentMetadata:
    """
    Extrae metadatos (título, autores, año) de un documento completo.
    Lee el PDF completo, extrae todo el texto, y luego envía muestras al modelo.
    """
    # Cargar el documento completo para extraer metadata
    loader = PyMuPDFLoader(document_path)
    pages = loader.load()
    
    # Concatenar el texto de todas las páginas para tener una vista completa del documento
    full_text = " ".join([clean_text(page.page_content) for page in pages])
    
    # Dividir el texto en tokens aproximadamente (asumiendo que un token es ~4 caracteres)
    char_limit = 500 * 4  # ~2000 tokens
    
    # Obtener primeros y últimos tokens aproximados
    start_text = full_text[:char_limit]
    end_text = full_text[-char_limit:] if len(full_text) > char_limit else ""
    
    sample_text = f"INICIO DEL DOCUMENTO:\n{start_text}\n\nFINAL DEL DOCUMENTO:\n{end_text}"
    
    # Print para debug - mostrar muestras de texto
    print("\n" + "="*80)
    print(f"DOCUMENTO: {os.path.basename(document_path)}")
    print(f"MUESTRA INICIO (primeros 200 caracteres):\n{start_text[:200]}...")
    print(f"MUESTRA FINAL (últimos 200 caracteres):\n{end_text[-200:] if end_text else 'N/A'}")
    
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
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    # Crear la cadena con salida estructurada
    extraction_chain = prompt | model.with_structured_output(DocumentMetadata)
    
    # Extraer metadatos
    metadata = extraction_chain.invoke({"document_text": sample_text})
    
    # Print para debug - mostrar metadata extraída
    print("\nMETADATA EXTRAÍDA:")
    print(f"Título: {metadata.title}")
    print(f"Autores: {metadata.authors}")
    print(f"Año: {metadata.publication_year}")
    print("="*80 + "\n")
    
    return metadata, len(pages)

def clean_text(text: str) -> str:
    """Limpia el texto eliminando caracteres no deseados y espacios múltiples."""
    # Reemplazar saltos de línea múltiples por uno solo
    text = re.sub(r'\n+', ' ', text)
    # Reemplazar espacios múltiples por uno solo
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()

def get_docs(path):
    print(f"\n{'-'*40}")
    print(f"Procesando: {os.path.basename(path)}")
    
    # Primero extraer la metadata una sola vez para todo el documento
    doc_metadata, num_pages = extract_document_metadata(path)
    print(f"Número total de páginas: {num_pages}")
    
    # Luego cargar las páginas y aplicar la misma metadata a todas
    loader = PyMuPDFLoader(path)
    docs = loader.load()
    
    # Verificar que el número de páginas coincide con lo esperado
    if len(docs) != num_pages:
        print(f"ADVERTENCIA: El número de páginas cambió: esperado {num_pages}, obtenido {len(docs)}")
    
    # Limpiar el texto de cada documento y aplicar la misma metadata a todas las páginas
    for i, doc in enumerate(docs):
        doc.page_content = clean_text(doc.page_content)
        
        # Aplicar la metadata extraída una sola vez a todas las páginas
        doc.metadata["title"] = doc_metadata.title
        doc.metadata["authors"] = doc_metadata.authors
        doc.metadata["publication_year"] = doc_metadata.publication_year
        doc.metadata["source"] = os.path.basename(path)
        doc.metadata["page"] = i+1
        doc.metadata["total_pages"] = len(docs)
        
    print(f"Metadata aplicada a todas las {len(docs)} páginas")
    print(f"{'-'*40}\n")
    return docs

def load_data(rag: RAG):
    print(f"\n{'='*80}")
    print("INICIO DEL PROCESO DE CARGA DE DOCUMENTOS")
    print(f"{'='*80}")
    
    # Cambiar de 'raw' a 'selected_documents'
    samples = os.path.join(os.path.dirname(__file__), "raw/")
    pdfs = [f for f in os.listdir(samples) if f.endswith(".pdf")]
    paths = [os.path.join(samples, f) for f in pdfs]
    
    print(f"\nSe encontraron {len(pdfs)} archivos PDF:")
    for i, pdf in enumerate(pdfs):
        print(f"{i+1}. {pdf}")
    
    docs = []
    
    # Procesamiento en paralelo de PDFs con barra de progreso
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Crear tareas para cada PDF y mostrar progreso con tqdm
        futures = {executor.submit(get_docs, path): path for path in paths}
        
        # Procesar resultados a medida que se completan con barra de progreso
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), 
                           desc="Procesando PDFs", unit="doc"):
            path = futures[future]
            try:
                # Añadir documentos procesados a la lista
                result_docs = future.result()
                docs.extend(result_docs)
                print(f"Completado: {os.path.basename(path)} - {len(result_docs)} páginas procesadas")
            except Exception as e:
                print(f"Error procesando {os.path.basename(path)}: {e}")
    
    print(f"\n{'='*80}")
    print(f"FASE 1: EXTRACCIÓN COMPLETADA")
    print(f"Total de documentos extraídos: {len(docs)} páginas")
    print(f"{'='*80}\n")

    print(f"\n{'='*80}")
    print("FASE 2: SPLITTING DE DOCUMENTOS (CHUNKING SEMÁNTICO)")
    print(f"{'='*80}")
    # Aplicar chunking con barra de progreso
    splits = semantic_split(docs)
    print(f"\nTotal de chunks creados: {len(splits)}")
    
    print(f"\n{'='*80}")
    print("FASE 3: INDEXACIÓN DE DOCUMENTOS")
    print(f"{'='*80}")
    print(f"Añadiendo {len(splits)} chunks a la colección...")
    # Añadir documentos a la colección
    rag.add_documents(splits)
    print("\nProceso completado con éxito!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    rag = RAG()
    rag.delete_all_documents()
    print("Colección anterior limpiada con éxito.")

    # Cargar datos
    load_data(rag)
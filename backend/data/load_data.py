import os
from dotenv import load_dotenv
from agent.rag import RAG
from langchain_community.document_loaders import PyPDFLoader
from data.splitters.semantic_splitter import semantic_split
from data.utils.keyword_extractor import extract_keywords
import re

load_dotenv()

def clean_text(text: str) -> str:
    """Limpia el texto eliminando caracteres no deseados y espacios múltiples."""
    # Reemplazar saltos de línea múltiples por uno solo
    text = re.sub(r'\n+', ' ', text)
    # Reemplazar espacios múltiples por uno solo
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()

def get_docs(path):
    loader = PyPDFLoader(path)
    docs = loader.load()
    # Limpiar el texto de cada documento
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
    return docs

def add_keywords_to_chunks(chunks):
    """Agrega keywords como metadata a cada chunk."""
    print("Extrayendo keywords para cada chunk...")
    for i, chunk in enumerate(chunks, 1):
        print(f"Procesando chunk {i}/{len(chunks)}...")
        try:
            keywords = extract_keywords(chunk.page_content)
            chunk.metadata['keywords'] = keywords
        except Exception as e:
            print(f"Error al extraer keywords del chunk {i}: {str(e)}")
            chunk.metadata['keywords'] = []
    return chunks

def load_data(rag):
    print("Loading and extracting documents")
    samples = os.path.join(os.path.dirname(__file__), "raw/")
    pdfs = [f for f in os.listdir(samples) if f.endswith(".pdf")]
    paths = [os.path.join(samples, f) for f in pdfs]
    docs = []
    for path in paths:
        docs.extend(get_docs(path))
    print("Extracted docs:", len(docs))

    print("Splitting documents using semantic chunking")
    splits = semantic_split(docs)
    print("Splitted docs:", len(splits))

    print("Adding keywords to chunks")
    splits = add_keywords_to_chunks(splits)
    print("Keywords added to all chunks")

    print("Adding documents to collection")
    rag.add_documents(splits)
    print("Added docs to collection")

if __name__ == "__main__":
    rag = RAG()
    rag.delete_all_documents()
    load_data(rag)
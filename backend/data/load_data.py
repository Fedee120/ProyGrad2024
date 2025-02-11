import os
from dotenv import load_dotenv
from agent.rag import RAG
from langchain_community.document_loaders import PyMuPDFLoader
from data.splitters.semantic_splitter import semantic_split
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
    loader = PyMuPDFLoader(path)
    docs = loader.load()
    # Limpiar el texto de cada documento
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
    return docs

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

    print("Adding documents to collection")
    rag.add_documents(splits)
    print("Added docs to collection")

if __name__ == "__main__":
    rag = RAG()
    rag.delete_all_documents()
    load_data(rag)
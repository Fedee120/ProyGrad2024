import os
from dotenv import load_dotenv
from rags.openai.rag import RAG
from langchain_community.document_loaders import PyPDFLoader
from data.splitters.semantic_splitter import semantic_split
import os

def get_docs(path):
    loader = PyPDFLoader(path)
    return loader.load()

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
    from dotenv import load_dotenv
    from rags.openai.rag import RAG
    load_dotenv()

    rag = RAG(
        URI=os.getenv("MILVUS_STANDALONE_URL"), 
        COLLECTION_NAME="real_collection", 
        search_kwargs={"k": 10}, 
        search_type="mmr", 
        llm_model_name="gpt-4o", 
        embeddings_model_name="text-embedding-3-small"
    )

    rag.delete_all_documents()
    load_data(rag)
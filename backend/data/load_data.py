import os
from dotenv import load_dotenv
from rags.openai.rag import RAG
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_docs(path):
    loader = PyPDFLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = os.path.basename(doc.metadata["source"])
    return docs

def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(docs)

def load_data(rag):
    print("Loading and extracting documents")
    samples = os.path.join(os.path.dirname(__file__), "raw/")
    pdfs = [f for f in os.listdir(samples) if f.endswith(".pdf")]
    paths = [os.path.join(samples, f) for f in pdfs]
    docs = []
    for path in paths:
        docs += get_docs(path)
    print("Extracted docs: ",len(docs))

    print("Splitting documents")
    splits = split_docs(docs)
    print("Splitted docs: ",len(splits))

    print("Adding documents to collection")
    rag.add_documents(splits)
    print("Added docs to collection")

if __name__ == "__main__":
    load_dotenv()

    rag = RAG(URI=os.getenv("MILVUS_STANDALONE_URL"), COLLECTION_NAME="real_collection", search_kwargs={"k": 5}, search_type="mmr", embeddings_model_name="text-embedding-3-small")

    rag.delete_all_documents()
    load_data(rag)
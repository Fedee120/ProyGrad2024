import os
from dotenv import load_dotenv
from langchain_ai21 import AI21SemanticTextSplitter

load_dotenv()
AI21_API_KEY = os.environ["AI21_API_KEY"]

def ai21_semantic_split(documents):
    text_splitter = AI21SemanticTextSplitter()
    chunks = text_splitter.split_documents(documents)
    return chunks
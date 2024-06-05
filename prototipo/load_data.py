import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
API_KEY = os.getenv('OPENAI_API_KEY')

loader = PyPDFLoader("data.pdf")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=API_KEY)
db = FAISS.from_documents(texts, embeddings)
db.save_local("data_embeddings.db")
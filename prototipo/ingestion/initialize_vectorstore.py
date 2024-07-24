import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL')

embeddings_model = OpenAIEmbeddings(model=EMBEDDINGS_MODEL, api_key=API_KEY)
dimension = 1536
index = faiss.IndexFlatL2(dimension)
docstore = InMemoryDocstore()
index_to_docstore_id = {}
faiss_store = FAISS(
    embedding_function=embeddings_model, 
    index=index, 
    docstore=docstore, 
    index_to_docstore_id=index_to_docstore_id
)
faiss_store.save_local('faiss_index')
print('Database created and successfully saved to "faiss_index".')

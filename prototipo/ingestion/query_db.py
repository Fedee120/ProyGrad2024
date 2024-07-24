import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL')

def format_docs(docs):
    return "\n\n".join(('\n'.join([doc.page_content, 'Page: ', str(doc.metadata['page'])])) for doc in docs)

embeddings_model = OpenAIEmbeddings(model=EMBEDDINGS_MODEL, api_key=API_KEY)
db = FAISS.load_local('faiss_index', embeddings=embeddings_model, allow_dangerous_deserialization=True)
query = "Is AI better than professors?"
docs = db.similarity_search(query)
print(format_docs(docs))
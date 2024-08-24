import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from prototipo.ingestion.splitters.character_splitter import split_by_character
from prototipo.ingestion.splitters.recursive_splitter import recursively_split
from prototipo.ingestion.splitters.ai21_semantic_splitter import ai21_semantic_split

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL')

def format_docs(docs):
    return "\n\n".join(('\n'.join([doc.page_content, 'Page: ', str(doc.metadata['page'])])) for doc in docs)

def generate_metadatas(chunks):
    # Substitute with document data
    metadatas = []
    for chunk in chunks:
        dict = {
            'doc_id': 1,
            'title': '“Better than my professor?” How to develop artificial intelligence tools for higher education',
            'authors': 'Triberti, S., Di Fuccio, R., Scuotto, C., Marsico, E., and Limone, P.',
            'year': '2024',
            'page': chunk.metadata.get('page') + 1,
        }
        metadatas.append(dict)
    return metadatas

embeddings_model = OpenAIEmbeddings(model=EMBEDDINGS_MODEL, api_key=API_KEY)
db = FAISS.load_local('faiss_index', embeddings=embeddings_model, allow_dangerous_deserialization=True)
print(f'Number of vectors in the index: {db.index.ntotal}')

# Substitute with document path
document_path = 'pdf_documents/1.pdf'
loader = PyPDFLoader(document_path)
documents = loader.load() # Returns a list of Document, each containing 'source' (file path) and 'page' (starting from 0) as metadata

# chunks = split_by_character(documents)
# chunks = recursively_split(documents)
chunks = ai21_semantic_split(documents)

print('Updating the index with the new document...')
db.add_texts(texts=[chunk.page_content for chunk in chunks], metadatas=generate_metadatas(chunks))
db.save_local('faiss_index')

print(f'Number of vectors in the index after update: {db.index.ntotal}')

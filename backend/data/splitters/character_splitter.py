from langchain_text_splitters import CharacterTextSplitter

def split_by_character(documents):
    text_splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    return chunks
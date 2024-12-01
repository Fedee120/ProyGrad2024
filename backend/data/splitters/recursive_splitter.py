from langchain_text_splitters import RecursiveCharacterTextSplitter

def recursively_split(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks
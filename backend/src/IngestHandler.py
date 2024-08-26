from src.MilvusHandler import MilvusHandler
from src.Chunker import Chunking
from src.OpenAIEmbedding import OpenAIEmbedding

class IngestHandler:
    def __init__(self, milvusHandler ,chunker):
        self.milvus_handler = milvusHandler
        self.chunker = chunker

    def ingest_pdf(self, pdf_file_path):
        # Chunk the text from the PDF
        chunks = self.chunker.chunk_pdf(pdf_file_path)

        # Insert the chunks into the Milvus database
        self.milvus_handler.insert_data(chunks)
        print(f"Inserted {len(chunks)} chunks from {pdf_file_path} into Milvus.")

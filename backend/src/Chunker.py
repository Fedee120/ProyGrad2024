from langchain.text_splitter import CharacterTextSplitter
from PyPDF2 import PdfReader

class Chunking:

    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, pdf_file_path):
        # Implement the text extraction logic from the PDF
        text = ""
        with open(pdf_file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def chunk_pdf(self, pdf_file_path):
        # Extract text from the PDF
        text = self.extract_text_from_pdf(pdf_file_path)

        # Split the text into chunks
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks

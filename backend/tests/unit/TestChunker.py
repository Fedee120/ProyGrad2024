import unittest
import os
import sys

# Add the path to the source code for the Chunking class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.Chunker import Chunking

class TestChunking(unittest.TestCase):

    def setUp(self):
        # Set up the Chunking instance for the test with smaller chunk size
        self.chunk_size = 500  # Adjusted to a smaller size to create more chunks
        self.chunk_overlap = 50
        self.chunker = Chunking(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

        # Path to the real PDF file
        self.test_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/test/test_sample.pdf'))

    def test_chunking_pdf(self):
        # Ensure that the file exists before testing
        self.assertTrue(os.path.exists(self.test_pdf_path))

        # Perform chunking on the PDF file
        chunks = self.chunker.chunk_pdf(self.test_pdf_path)

        # Check that chunks are returned and not empty
        self.assertGreater(len(chunks), 0)

        # Print detailed information about each chunk
        print(f"Total number of chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}:")
            print(f"Length: {len(chunk)} characters")
            print(f"Content: {chunk[:200]}...")  # Print the first 200 characters of each chunk for clarity
            print("-" * 50)

if __name__ == "__main__":
    unittest.main()

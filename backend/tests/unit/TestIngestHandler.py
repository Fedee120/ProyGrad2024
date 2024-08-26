import unittest
import os
import sys
from dotenv import load_dotenv

# Adjust the path to access the source files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

load_dotenv()

from src.IngestHandler import IngestHandler
from src.Chunker import Chunking
from src.MilvusHandler import MilvusHandler
from src.OpenAIEmbedding import OpenAIEmbedding

class TestIngestHandler(unittest.TestCase):

    def setUp(self):
        # Setup the MilvusHandler and Chunker for the test
        self.collection_name = "test_collection_pdf"
        self.milvus_handler = MilvusHandler(OpenAIEmbedding(), collection_name=self.collection_name)
        self.chunker = Chunking(chunk_size=500, chunk_overlap=100)  # Adjust chunk size as needed
        self.ingest_handler = IngestHandler(chunker=self.chunker, milvusHandler=self.milvus_handler)

        # Path to the test PDF file
        self.test_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/test/test_sample.pdf'))

        # Drop the collection if it already exists
        self.milvus_handler.drop_collection()

        # Ensure the collection is created
        self.milvus_handler.create_collection()

    def tearDown(self):
        # Drop the collection after the test to clean up
        self.milvus_handler.drop_collection()

    def test_ingest_pdf_and_search(self):
        # Ensure that the file exists before testing
        self.assertTrue(os.path.exists(self.test_pdf_path))

        # Ingest the PDF file into the Milvus collection
        print("Starting PDF ingestion...")
        self.ingest_handler.ingest_pdf(self.test_pdf_path)
        print("PDF ingestion completed.")

        # Create an index to optimize search performance
        print("Creating index...")
        self.milvus_handler.create_index()

        # Load the collection for querying
        print("Loading collection...")
        self.milvus_handler.load_collection()

        # Debug: Print some chunks that were inserted to verify
        print("Debugging chunks inserted into Milvus:")
        for chunk in self.chunker.chunk_pdf(self.test_pdf_path)[:5]:  # Print first 5 chunks
            print(f"Chunk: {chunk[:200]}...")  # Print the first 200 characters of each chunk

        # Perform a search to verify the content was ingested correctly
        query_sentence = "communication with the professor"  # Adjust this to a sentence from the PDF
        print(f"Searching for: '{query_sentence}'")
        search_results = self.milvus_handler.search(query_sentence, top_k=3)
        print("Search results:")
        print(search_results)

        # Debug: Print search results
        if search_results and len(search_results[0]) > 0:
            print("Search results found:")
            for result in search_results[0]:
                print(f"ID: {result.id}, Sentence: {result.entity.get('sentence')}, Distance: {result.distance}")
        else:
            print("No search results found.")

        # Ensure that search results are returned
        self.assertGreater(len(search_results[0]), 0)

if __name__ == "__main__":
    unittest.main()

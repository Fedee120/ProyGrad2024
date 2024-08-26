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
from src.Retriever import Retriever

class TestRetriever(unittest.TestCase):

    def setUp(self):
        # Set up the MilvusHandler and Chunker for the test
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

        # Perform PDF ingestion
        self.ingest_handler.ingest_pdf(self.test_pdf_path)

        # Create an index to optimize search performance
        self.milvus_handler.create_index()

        # Load the collection for querying
        self.milvus_handler.load_collection()

        # Set up the Retriever instance
        self.retriever = Retriever(milvus_handler=self.milvus_handler)

    def tearDown(self):
        # Drop the collection after the test to clean up
        self.milvus_handler.drop_collection()

    def test_retrieve_from_pdf(self):
        # Perform a search using the Retriever
        query_sentence = "communication with the professor"  # Adjust this to a sentence from the PDF
        retrieved_results = self.retriever.retrieve(query_sentence, top_k=5)

        # Ensure that results are returned
        self.assertGreater(len(retrieved_results), 0)

        # Optionally, print the retrieved results for manual inspection
        for result in retrieved_results:
            print(f"ID: {result['id']}, Sentence: {result['sentence']}, Distance: {result['distance']}")

        # Validate that the results contain the expected text
        self.assertTrue(any("communication" in result['sentence'] for result in retrieved_results))

if __name__ == "__main__":
    unittest.main()

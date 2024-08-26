import unittest
from pymilvus import connections, utility
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

load_dotenv()

from src.OpenAIEmbedding import OpenAIEmbedding
from src.MilvusHandler import MilvusHandler

class TestMilvusHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load environment variables from .env file
        
        # Initialize OpenAIEmbedding with a valid API key from the .env file
        cls.api_key = os.getenv("OPENAI_API_KEY")  # Make sure .env has the OPENAI_API_KEY
        cls.openai_embedder = OpenAIEmbedding(api_key=cls.api_key)
        
        # Create an instance of MilvusHandler with the embedding calculator
        cls.collection_name = "test_embeddings_collection"
        cls.milvus_handler = MilvusHandler(embedding_calculator=cls.openai_embedder, collection_name=cls.collection_name)
    
    def setUp(self):
        # Ensure the collection is created for each test
        self.milvus_handler.create_collection()

    def tearDown(self):
        # Drop the collection after each test to ensure isolation
        self.milvus_handler.drop_collection()

    def test_insert_data(self):
        # Test inserting data into Milvus
        sentences = ["The quick brown fox jumps over the lazy dog.", "AI is the future.", "OpenAI provides powerful models."]
        insert_result = self.milvus_handler.insert_data(sentences)

        # Verify that data was inserted correctly
        self.assertIsNotNone(insert_result)
        self.assertEqual(len(insert_result.primary_keys), len(sentences))

    def test_create_index(self):
        # Test creating an index on the embedding field
        self.milvus_handler.create_index()
        index_info = self.milvus_handler.collection.indexes

        # Check that the index was created
        self.assertIsNotNone(index_info)
        self.assertGreater(len(index_info), 0)

    def test_search(self):
        # Insert some data first
        sentences = ["The quick brown fox jumps over the lazy dog.", "AI is the future.", "OpenAI provides powerful models."]
        self.milvus_handler.insert_data(sentences)

        # Create an index and load the collection
        self.milvus_handler.create_index()
        self.milvus_handler.load_collection()

        # Perform a search with a query sentence
        query_sentence = "AI technology"
        search_results = self.milvus_handler.search(query_sentence, top_k=2)
        print(search_results)

        # Check that results are returned
        self.assertIsNotNone(search_results)
        self.assertGreater(len(search_results[0]), 0)

    @classmethod
    def tearDownClass(cls):
        # Ensure the collection is dropped at the end of all tests
        if utility.has_collection(cls.collection_name):
            cls.milvus_handler.drop_collection()

if __name__ == "__main__":
    unittest.main()

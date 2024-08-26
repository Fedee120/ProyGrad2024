import unittest
from unittest.mock import patch
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.OpenAIEmbedding import OpenAIEmbedding

# Load the API key from the .env file
load_dotenv()

class TestOpenAIEmbedding(unittest.TestCase):

    def setUp(self):
        # Read the API key from the environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        # Initialize the OpenAIEmbedding class with the actual API key
        self.embedder = OpenAIEmbedding(api_key=self.api_key)

    def test_single_embedding(self):
        # Test single embedding generation with the actual API
        sentence = "Hello, world!"
        embedding = self.embedder.calculate_embeddings(sentence)

        # Check that a response is returned
        self.assertIsNotNone(embedding)
        # Check that the length of the embedding is 1536 (based on model)
        self.assertEqual(len(embedding), 1536)

    def test_batch_embeddings(self):
        # Test batch embedding generation with the actual API
        sentences = ["Hello, world!", "This is another test.", "AI is transforming the world."]
        embeddings = self.embedder.batch_calculate_embeddings(sentences)

        # Check that a response is returned
        self.assertIsNotNone(embeddings)
        # Check that the number of embeddings matches the number of sentences
        self.assertEqual(len(embeddings), len(sentences))
        # Check that the length of each embedding is 1536
        for embedding in embeddings:
            self.assertEqual(len(embedding), 1536)

if __name__ == "__main__":
    unittest.main()
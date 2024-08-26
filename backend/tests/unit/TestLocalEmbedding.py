import unittest
import sys
import os

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.LocalEmbedding import BertEmbedding  # Assuming this class is implemented in LocalEmbedding.py

class TestLocalBertEmbedding(unittest.TestCase):

    def setUp(self):
        # Initialize the BertEmbedding class
        self.embedder = BertEmbedding()

    def test_single_embedding(self):
        # Test single embedding generation with local BERT model
        sentence = "Hello, world!"
        embedding = self.embedder.calculate_embeddings(sentence)

        # Check that a response is returned
        self.assertIsNotNone(embedding)
        # Check that the length of the embedding is 768 (standard dimension for BERT)
        self.assertEqual(len(embedding), 768)

    def test_batch_embeddings(self):
        # Test batch embedding generation with local BERT model
        sentences = ["Hello, world!", "This is another test.", "AI is transforming the world."]
        embeddings = self.embedder.batch_calculate_embeddings(sentences)

        # Check that a response is returned
        self.assertIsNotNone(embeddings)
        # Check that the number of embeddings matches the number of sentences
        self.assertEqual(len(embeddings), len(sentences))
        # Check that the length of each embedding is 768
        for embedding in embeddings:
            self.assertEqual(len(embedding), 768)

if __name__ == "__main__":
    unittest.main()

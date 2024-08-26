from abc import ABC, abstractmethod

class Embedding(ABC):
    @abstractmethod
    def calculate_embeddings(self, sentence):
        """Calculate the embedding for a single sentence."""
        pass

    @abstractmethod
    def batch_calculate_embeddings(self, sentences):
        """Calculate embeddings for a batch of sentences."""
        pass
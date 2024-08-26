from sentence_transformers import SentenceTransformer
from Embedding import Embedding

class BertEmbedding(Embedding):
    def __init__(self, model_name='bert-base-nli-mean-tokens'):
        print(f"Loading local BERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"Successfully loaded local BERT model: {model_name}")
    
    def calculate_embeddings(self, sentence):
        return self.model.encode([sentence])[0]  # Return single embedding
    
    def batch_calculate_embeddings(self, sentences):
        return self.model.encode(sentences).tolist()  # Return list of embeddings
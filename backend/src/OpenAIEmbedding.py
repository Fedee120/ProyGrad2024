from openai import OpenAI
from Embedding import Embedding
from dotenv import load_dotenv
import os
load_dotenv()

class OpenAIEmbedding(Embedding):
    def __init__(self, api_key = None, model_name='text-embedding-3-small'):   # 1536 dimensions
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key = self.api_key)
        self.model_name = model_name
        print(f"Using OpenAI model: {model_name}")
    
    def calculate_embeddings(self, sentence):
        response = self.client.embeddings.create(
            model=self.model_name,
            input=sentence
        )
        return response.data[0].embedding  # Extract the embedding
    
    def batch_calculate_embeddings(self, sentences):
        response = self.client.embeddings.create(
            model=self.model_name,
            input=sentences
        )
        return [embedding.embedding for embedding in response.data]  # Extract the embeddings
    
if __name__ == "__main__":
    # Initialize the embedder; API key will be read from the .env file
    openai_embedder = OpenAIEmbedding()

    # Test single sentence embedding
    sentence = "Hello, world!"
    embedding = openai_embedder.calculate_embeddings(sentence)
    print(f"Single embedding for '{sentence}':\n{embedding}\n")

    # Test batch embeddings
    sentences = ["Hello, world!", "This is another test sentence.", "AI is transforming the world."]
    batch_embeddings = openai_embedder.batch_calculate_embeddings(sentences)
    print("Batch embeddings:")
    for i, emb in enumerate(batch_embeddings):
        print(f"Embedding for '{sentences[i]}':\n{emb}\n")

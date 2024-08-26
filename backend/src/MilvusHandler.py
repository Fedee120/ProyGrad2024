# This class provides the interface to interact with Milvus server.
# It includes methods to connect to the server, create a collection, insert data into the collection, and query the collection.

from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection, Index, utility
from OpenAIEmbedding import OpenAIEmbedding

class MilvusHandler:
    def __init__(self, embedding_calculator, host="127.0.0.1", port="19530", collection_name="embeddings_collection"):
        self.collection_name = collection_name
        self.embedding_calculator = embedding_calculator
        self.connect_to_milvus(host, port)
        self.create_collection()

    def connect_to_milvus(self, host, port):
        connections.connect("default", host=host, port=port)
        print(f"Connected to Milvus at {host}:{port}")

    def create_collection(self):
        # Define the schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="sentence", dtype=DataType.VARCHAR, max_length=8192),  # Field for sentence
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)  # Embedding size for OpenAI's embeddings
        ]
        schema = CollectionSchema(fields, "Embeddings collection schema")
        
        # Check if the collection already exists
        if not utility.has_collection(self.collection_name):
            self.collection = Collection(name=self.collection_name, schema=schema)
            print(f"Collection '{self.collection_name}' created.")
        else:
            self.collection = Collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")

    def insert_data(self, sentences):
        # Use the embedding calculator (OpenAI) to get embeddings
        embeddings = self.embedding_calculator.batch_calculate_embeddings(sentences)

        # Insert data into collection
        insert_result = self.collection.insert([sentences, embeddings])
        print(f"Inserted {len(sentences)} records into the collection.")
        return insert_result
    
    def create_index(self, nlist=128):
        index_params = {
            "index_type": "IVF_FLAT",  # You can also use IVF_SQ8, IVF_PQ, etc.
            "params": {"nlist": nlist},
            "metric_type": "L2"  # Euclidean distance
        }
        index = Index(self.collection, "embedding", index_params)
        print(f"Index created with parameters: {index_params}")
    
    def load_collection(self):
        self.collection.load()
        print(f"Collection '{self.collection_name}' loaded for search.")

    def search(self, query_sentence, top_k=3, nprobe=10):
        # Use the embedding calculator to get the query embedding
        query_embedding = self.embedding_calculator.calculate_embeddings(query_sentence)
        query_embedding = [query_embedding]  # Convert to list of lists

        # Define search parameters
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": nprobe}
        }

        # Perform the search
        results = self.collection.search(query_embedding, "embedding", search_params, limit=top_k, output_fields=["id", "sentence"])
        print(f"Search results for query: '{query_sentence}'")
        
        # Return search results
        return results

    def drop_collection(self):
        if self.collection_name in utility.list_collections():
            self.collection.drop()
            print(f"Collection '{self.collection_name}' dropped.")
        else:
            print(f"Collection '{self.collection_name}' does not exist.")
    
    def reindex(self, nlist=128):
        # Drop the existing index and recreate it
        self.collection.drop_index()
        self.create_index(nlist)
        print(f"Reindexed collection '{self.collection_name}'.")
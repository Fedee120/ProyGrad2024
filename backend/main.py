from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection, Index
from sentence_transformers import SentenceTransformer
from typing import List
import uvicorn

app = FastAPI()

# Connect to Milvus
connections.connect("default", host="standalone", port="19530")  # use the service name 'milvus' if running in Docker

# Define the collection schema
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)  # Assuming 768 dimensions for BERT
]

schema = CollectionSchema(fields, "Embeddings collection schema")
collection = Collection(name="embeddings_collection", schema=schema)

# Create an index for the collection
index_params = {
    "index_type": "IVF_FLAT",  # You can use other types like "IVF_SQ8", "IVF_PQ", etc.
    "params": {"nlist": 128},  # Index parameters
    "metric_type": "L2"  # Euclidean distance (you can use "IP" for Inner Product)
}
index = Index(collection, "embedding", index_params)

# Load the collection for searching
collection.load()

# Initialize the sentence transformer model
model = SentenceTransformer('bert-base-nli-mean-tokens')

# Pydantic models for request bodies
class EmbeddingRequest(BaseModel):
    sentences: List[str]

class QueryRequest(BaseModel):
    query_sentence: str

@app.post("/add-embeddings")
async def add_embeddings(request: EmbeddingRequest):
    try:
        embeddings = model.encode(request.sentences)
        embeddings = embeddings.tolist()

        # Insert embeddings into Milvus
        insert_result = collection.insert([embeddings])
        collection.load()  # Ensure the collection is loaded before searching

        return {"status": "success", "inserted_ids": insert_result.primary_keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-embedding")
async def query_embedding(request: QueryRequest):
    try:
        query_embedding = model.encode([request.query_sentence]).tolist()

        # Define search parameters
        search_params = {
            "metric_type": "L2",  # Or "IP" for Inner Product
            "params": {"nprobe": 10}
        }

        # Perform the search
        results = collection.search(query_embedding, "embedding", search_params, limit=3, output_fields=["id", "embedding"])

        # Prepare the response
        response = []
        for result in results[0]:
            response.append({
                "ID": result.id,
                "Distance": result.distance,
                "Embedding": result.entity.get('embedding')
            })

        return {"status": "success", "results": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

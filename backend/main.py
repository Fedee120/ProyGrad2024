from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, Index
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Connect to Milvus
try:        
    connections.connect("default", host="localhost", port="19530")
    print("Connected to Milvus!")
except Exception as e:
    print(f"Failed to connect to Milvus: {e}")
    exit(1)

# Define the schema for the collection, including a field for the sentence
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="sentence", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]

schema = CollectionSchema(fields, "Embeddings collection schema")
collection = Collection(name="embeddings_collection", schema=schema)

# Create an index for the collection
index_params = {
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128},
    "metric_type": "L2"
}

index = Index(collection, "embedding", index_params)
collection.load()

# Load the model
model = SentenceTransformer('bert-base-nli-mean-tokens')

class SentenceRequest(BaseModel):
    sentence: str

@app.post("/add")
def add_sentence(request: SentenceRequest):
    sentence = request.sentence
    embedding = model.encode([sentence]).tolist()[0]
    insert_result = collection.insert([[sentence], [embedding]])
    return {"status": "success", "insert_count": len(insert_result.primary_keys)}

@app.post("/query")
def query_similar(request: SentenceRequest):
    sentence = request.sentence
    query_embedding = model.encode([sentence]).tolist()
    
    # Make sure the query_embedding is a list of lists
    query_embedding = [query_embedding[0]]  # If the model returns a list of lists, use it directly
    
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10}
    }
    
    try:
        results = collection.search(query_embedding, "embedding", search_params, limit=3, output_fields=["id", "sentence", "embedding"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    response = []
    for result in results[0]:
        response.append({
            "id": result.id,
            "sentence": result.entity.get("sentence"),
            "distance": result.distance,
            "embedding": result.entity.get("embedding")
        })
    
    return {"results": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

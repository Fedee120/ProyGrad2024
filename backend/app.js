const express = require('express');
const bodyParser = require('body-parser');
const { OpenAI } = require('openai');
const { MilvusClient } = require("@zilliz/milvus2-sdk-node");

const app = express();
app.use(bodyParser.json());

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const milvusClient = new MilvusClient({address: '127.0.0.1:19530'});

// Collection and embedding dimensions (should match your schema)
const COLLECTION_NAME = 'embeddings_collection';
const EMBEDDING_DIM = 768;

// Define collection schema if not already created (equivalent to Python's FieldSchema and CollectionSchema)
async function createCollectionIfNotExists() {
  const collectionExists = await milvusClient.hasCollection({
    collection_name: COLLECTION_NAME,
  });

  if (!collectionExists) {
    await milvusClient.createCollection({
      collection_name: COLLECTION_NAME,
      fields: [
        { name: 'id', type: 'INT64', is_primary_key: true, auto_id: true },
        { name: 'embedding', type: 'FLOAT_VECTOR', dim: EMBEDDING_DIM },
        { name: 'original_text', type: 'VARCHAR', max_length: 512 },
      ],
    });

    // Create an index (equivalent to the Python Index object)
    await milvusClient.createIndex({
      collection_name: COLLECTION_NAME,
      field_name: 'embedding',
      index_type: 'IVF_FLAT',
      metric_type: 'L2',
      params: { nlist: 128 },
    });
  }
}

// Call this function to ensure the collection is set up
createCollectionIfNotExists();

async function getEmbedding(text) {
  const { data } = await openai.embeddings.create({
    model: process.env.EMBEDDINGS_MODEL,
    input: text,
    encoding_format: "float",
  });
  return data[0].embedding;
}

app.post('/add-embedding', async (req, res) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const embedding = await getEmbedding(text);
    // Insert embedding into Milvus (equivalent to collection.insert)
    const insertResult = await milvusClient.insert({
      collection_name: COLLECTION_NAME,
      fields_data: [
        {
          name: 'embedding',
          type: 'FLOAT_VECTOR',
          values: [embedding],
        },
        {
          name: 'original_text',
          type: 'VARCHAR',
          values: [text],
        },
      ],
    });
    res.status(200).json({ message: 'Document added successfully', text, embedding });
  } catch (error) {
    console.error('Error adding embedding:', error);
    res.status(500).json({ error: 'Failed to add embedding' });
  }
});

app.post('/query-embedding', async (req, res) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const queryEmbedding = await getEmbedding(text);
    // Search for the most similar embedding (equivalent to collection.search in Python)
    const searchResult = await milvusClient.search({
      collection_name: COLLECTION_NAME,
      vectors: [queryEmbedding],
      search_params: {
        anns_field: 'embedding',
        topk: 1,
        metric_type: 'L2',
        params: JSON.stringify({ nprobe: 10 }),
      },
      output_fields: ['id', 'original_text', 'embedding'],
    });

    const results = searchResult.results.map(result => ({
      id: result.id,
      distance: result.distance,
      text: result.original_text,
      embedding: result.embedding,
    }));

    res.status(200).json({ query: text, results });
  } catch (error) {
    console.error('Error querying embedding:', error);
    res.status(500).json({ error: 'Failed to query embedding' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

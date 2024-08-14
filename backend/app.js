const express = require('express');
const bodyParser = require('body-parser');
const { OpenAI } = require('openai');
const { norm, dot } = require('mathjs');

const app = express();
app.use(bodyParser.json());

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

let vectors = [];
let documents = [];

async function getEmbedding(text) {
  const { data } = await openai.embeddings.create({
    model: process.env.EMBEDDINGS_MODEL,
    input: text,
    encoding_format: "float",
  });
  return data[0].embedding;
}

function addDocument(text, embedding) {
  documents.push(text);
  vectors.push(embedding);
}

function findMostSimilar(embedding) {
  let maxSim = -Infinity;
  let bestMatch = null;
  vectors.forEach((vector, idx) => {
    const similarity = cosineSimilarity(embedding, vector);
    if (similarity > maxSim) {
      maxSim = similarity;
      bestMatch = documents[idx];
    }
  });
  return bestMatch;
}

function cosineSimilarity(array1, array2) {
  const dotProduct = dot(array1, array2);
  const normA = norm(array1);
  const normB = norm(array2);
  const cosineSimilarity = dotProduct / (normA * normB);

  return cosineSimilarity;
}



app.post('/add-embedding', async (req, res) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const embedding = await getEmbedding(text);
    addDocument(text, embedding);
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
    const bestMatch = findMostSimilar(queryEmbedding);
    res.status(200).json({ query: text, bestMatch });
  } catch (error) {
    console.error('Error querying embedding:', error);
    res.status(500).json({ error: 'Failed to query embedding' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

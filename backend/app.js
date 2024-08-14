const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
// const { MilvusClient } = require('milvus-node-sdk');

const app = express();
app.use(bodyParser.json());

// // Initialize Milvus client
// const milvusClient = new MilvusClient({ address: 'localhost:19530' });

// Sample endpoint to test if the server is running
app.get('/', (req, res) => {
  res.send('Hello, Milvus!');
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const mongoose = require('mongoose');

const app = express();
app.use(cors());
app.use(express.json());

const NGROK_URL = 'https://overplay-sixteen-snowfield.ngrok-free.dev';

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('Connected to MongoDB Atlas'))
  .catch(err => console.error('MongoDB connection error:', err));

// Define Schema for UX Friction (Where user gets stuck)
const frictionSchema = new mongoose.Schema({
  app: String,
  screen: String,
  avgHesitation: Number,
  oscillationRate: Number
});

const Friction = mongoose.model('Friction', frictionSchema);

// Proxy endpoints for the Guidance Agent API
app.post('/api/guidance', async (req, res) => {
  try {
    const response = await axios.post(`${NGROK_URL}/api/v1/guidance`, req.body, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Internal Server Error' });
  }
});

app.post('/api/fraud/scam', async (req, res) => {
  try {
    const response = await axios.post(`${NGROK_URL}/api/v1/fraud/scam`, req.body, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Internal Server Error' });
  }
});

app.post('/api/knowledge', async (req, res) => {
  try {
    const response = await axios.post(`${NGROK_URL}/api/v1/knowledge`, req.body, {
      headers: { 'ngrok-skip-browser-warning': 'true' }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { error: 'Internal Server Error' });
  }
});

// MongoDB API Endpoints
app.get('/api/friction', async (req, res) => {
  try {
    const data = await Friction.find({});
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch friction data' });
  }
});

// Helper endpoint to quickly seed the database with initial data
app.post('/api/friction/seed', async (req, res) => {
  try {
    await Friction.deleteMany({});
    const seedData = [
      { app: 'Banking App X', screen: 'Beneficiary Add', avgHesitation: 12.4, oscillationRate: 45 },
      { app: 'Tax Portal', screen: 'Deductions Form', avgHesitation: 18.2, oscillationRate: 62 },
      { app: 'E-Commerce Z', screen: 'Checkout Payment', avgHesitation: 8.1, oscillationRate: 28 },
    ];
    await Friction.insertMany(seedData);
    res.json({ message: 'Database successfully seeded!', data: seedData });
  } catch (error) {
    res.status(500).json({ error: 'Failed to seed data' });
  }
});

// Empty endpoints for completely removed pages just in case
app.get('/api/threats', (req, res) => res.json([]));
app.get('/api/xai-logs', (req, res) => res.json([]));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

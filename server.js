const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());

app.get('/', (req, res) => {
    res.render('index');
});

app.get('/quiz', (req, res) => {
    const username = 'Player' + Math.floor(Math.random() * 10000);
    res.render('quiz', { username });
});

app.get('/slot', (req, res) => {
    const username = 'Player' + Math.floor(Math.random() * 10000);
    res.render('slot', { username });
});

app.get('/scratch', (req, res) => {
    const username = 'Player' + Math.floor(Math.random() * 10000);
    res.render('scratch', { username });
});

app.get('/spin', (req, res) => {
    const username = 'Player' + Math.floor(Math.random() * 10000);
    res.render('spin', { username });
});

app.get('/api/user-info', (req, res) => {
    const username = 'Player' + Math.floor(Math.random() * 10000);
    res.json({ username });
});

app.post('/api/spin', async (req, res) => {
    try {
        const response = await axios.post('https://secure-spin-server.onrender.com/spin', {
            username: req.body.username,
            nonce: req.body.nonce
        });
        res.json(response.data);
    } catch (error) {
        console.error('Spin error:', error.message);
        res.status(500).json({ error: 'Spin failed' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
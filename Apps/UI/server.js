// Apps/ui/server.js

const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000; // A porta que o seu ui.yml e Dockerfile esperam

// Serve ficheiros estáticos (como o seu index.html, css, js)
app.use(express.static(path.join(__dirname, 'Public')));

// Rota principal que serve o seu HTML
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'Public', 'home.html'));
});

app.listen(PORT, () => {
  console.log(`Servidor UI a correr em http://localhost:${PORT}`);
});
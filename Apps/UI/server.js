// Apps/ui/server.js

const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000; // A porta que o seu ui.yml e Dockerfile esperam

// Serve ficheiros estáticos (como o seu index.html, css, js)
app.use(express.static(path.join(__dirname, 'Public')));

// Proxy para a API (resolve o problema de CORS e comunicação entre pods)
app.get(/^\/api\/.*/, async (req, res) => {
  // Constrói a URL real da API removendo o prefixo /api
  const apiUrl = `http://api-service:8000${req.originalUrl.replace(/^\/api/, '')}`;

  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(apiUrl);

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      return res.status(response.status).json({
        erro: `Falha ao chamar a API (${response.status})`,
        detalhe: text
      });
    }

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Erro ao chamar a API:', error);
    res.status(500).json({ erro: 'Erro ao comunicar com a API' });
  }
});

// Rota principal que serve o seu HTML
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'Public', 'home.html'));
});

app.listen(PORT, () => {
  console.log(`Servidor UI a correr em http://localhost:${PORT}`);
});
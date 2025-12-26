// Apps/ui/server.js

const express = require('express');
const path = require('path');
const app = express();
const { register, HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS } = require('./metrics');

const PORT = 3000; // A porta que o seu ui.yml e Dockerfile esperam

// Serve ficheiros estáticos (como o seu index.html, css, js)
app.use(express.static(path.join(__dirname, 'Public')));

// Middleware para recolha de métricas (intercepta todos os pedidos)
app.use((req, res, next) => {
  const start = process.hrtime();

  res.on('finish', () => {
    const duration = process.hrtime(start);
    const durationSeconds = duration[0] + duration[1] / 1e9;
    
    // Usa req.path como rota (simplificação para evitar alta cardinalidade)
    const route = req.path;

    HTTP_REQUESTS_TOTAL.inc({
      method: req.method,
      route: route,
      status_code: res.statusCode
    });

    HTTP_REQUEST_DURATION_SECONDS.observe({
      method: req.method,
      route: route,
      status_code: res.statusCode
    }, durationSeconds);
  });

  next();
});

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

// --- Servidor de Métricas (Porta 8001) ---
const metricsApp = express();

metricsApp.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (ex) {
    res.status(500).send(ex.message);
  }
});

metricsApp.listen(8001, () => {
  console.log('Servidor de métricas UI iniciado na porta 8001');
});

app.listen(PORT, () => {
  console.log(`Servidor UI a correr em http://localhost:${PORT}`);
});
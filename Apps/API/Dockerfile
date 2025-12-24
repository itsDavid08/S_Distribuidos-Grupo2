FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY metrics.py .

# faz expose 2 vezes porque temos 2 servidores, um para a API e outro para as metricas
EXPOSE 8000
EXPOSE 8001

RUN addgroup --system appuser && adduser --system --group appuser
USER appuser

# CORRECCIÓN: Ejecuta main:app (no src.main:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
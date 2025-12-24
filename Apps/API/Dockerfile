FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CORRECCIÓN: Copia main.py directamente
COPY main.py .
COPY metrics.py .

EXPOSE 8000
EXPOSE 8001

RUN addgroup --system appuser && adduser --system --group appuser
USER appuser

# CORRECCIÓN: Ejecuta main:app (no src.main:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
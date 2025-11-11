# # Use uma imagem base oficial do Python.
# # python:3.10-slim é uma boa escolha por ser leve.
# FROM python:3.10-slim

# # Define o diretório de trabalho no contêiner
# WORKDIR /app

# # Copia o arquivo de dependências primeiro para aproveitar o cache do Docker.
# # Se o requirements.txt não mudar, o Docker não reinstalará as dependências.
# COPY requirements.txt .

# # Instala as dependências
# RUN pip install --no-cache-dir -r requirements.txt

# # Copia o código da aplicação para o diretório de trabalho
# COPY . /app

# # Expõe a porta em que o app será executado
# EXPOSE 8000

# # Comando para iniciar a aplicação usando Uvicorn.
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

#___ TEMPORAL___#
FROM python:3.10-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia o código da aplicação (opcional, solo si quieres tenerlo disponible)
COPY . /app

# Instala as dependências (opcional para tests)
RUN pip install pika

# Mantém o container rodando indefinidamente
CMD ["sleep", "infinity"]

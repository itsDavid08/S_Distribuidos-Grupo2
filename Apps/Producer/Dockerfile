
# FROM python:3.10-slim

# # Define o diretório de trabalho no contêiner
# WORKDIR /app


# COPY producer.py .

# # Instala as dependências
# RUN pip install pika

# # Copia o código da aplicação para o diretório de trabalho
# COPY . /app


# EXPOSE 30300


# CMD ["python", "producer.py"]


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

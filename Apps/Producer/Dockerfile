
FROM python:3.10-slim
# Define o diretório de trabalho no contêiner
WORKDIR /app
COPY producer.py .
# Instala as dependências
RUN pip install pika
# Copia o código da aplicação para o diretório de trabalho
COPY . /app
EXPOSE 30300
CMD ["python", "producer.py"]
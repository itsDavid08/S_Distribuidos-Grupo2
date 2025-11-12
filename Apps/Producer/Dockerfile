# FROM python:3.10-slim
# # Define o diretório de trabalho no contêiner
# WORKDIR /app

# # Copia o ficheiro de dependências
# COPY requirements.txt .

# # Instala as dependências
# RUN pip install --no-cache-dir -r requirements.txt

# # Copia o código da aplicação
# COPY Producer.py .

# EXPOSE 30300

# # Comando para correr a aplicação
# CMD ["python", "Producer.py"]

#___
FROM python:3.10-slim

# Mantener el contenedor vivo sin hacer nada
ENTRYPOINT ["python", "-c", "import time; time.sleep(10**9)"]

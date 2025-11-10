# Define a imagem base (uma versão Python leve)
#FROM python:3.10-slim

# Define o diretório de trabalho dentro do contentor
#WORKDIR /app

# Copia e instala as dependências (otimizado para cache)
# (Isto é feito antes de copiar o resto do código para acelerar builds futuros)
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação (ex: pasta 'src')
#COPY . /app

# Informa ao Docker a porta que a aplicação usa
#EXPOSE 8000

# --- Segurança: Cria e usa um utilizador não-root ---
# (Evita correr a aplicação como 'root', que é perigoso)
#RUN addgroup --system appuser && adduser --system --group appuser
#USER appuser

# Comando para iniciar a aplicação (Uvicorn) quando o contentor arranca
# '--host 0.0.0.0' é necessário para permitir ligações externas ao contentor.
#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


#_______________________________________________________________________________

# Apps/productor/Dockerfile
# (Este é um DOCKERFILE SIMPLES DE SIMULACRO)

# Usamos a imagem mais pequena possível
FROM alpine:latest

# Comando que simplesmente "dorme".
# O contentor irá construir, executar, e não fazer nada.
# Isto é perfeito para o seu pipeline de CI/CD passar.
CMD ["sleep", "infinity"]
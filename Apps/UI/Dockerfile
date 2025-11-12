# FROM node:alpine
# WORKDIR /app
# COPY ["package.json", "package-lock.json*", "./"]

# # Instala apenas dependências de produção
# RUN npm ci --omit=dev

# COPY . .

# # Corre como um utilizador não-root
# USER node
# CMD [ "node", "server.js" ]

FROM alpine:3.20

# Mantener el contenedor en ejecución sin hacer nada
ENTRYPOINT ["sh", "-c", "tail -f /dev/null"]
# Consumidor RabbitMQ (Python)

Este microserviço é um consumidor RabbitMQ em Python (FastAPI). O foco é o deploy em Kubernetes e a Gestão de Sistemas Distribuídos.

## ⚙️ Pré-requisitos Essenciais

Verifique se você tem instalado:

1. **Python 3.10+** e **pip**
2. **Docker** e **Docker Compose**

## 🐇 Executando o RabbitMQ com Docker

Para o microserviço funcionar, é necessário ter uma instância do RabbitMQ em execução. Utilize o Docker para iniciar um container RabbitMQ de forma rápida.

Com o RabbitMQ em execução, você pode iniciar o serviço de consumidor.

## 🛠️ Guia Rápido de Instalação e Execução

Siga os comandos abaixo na pasta raiz do serviço.

### 1. Preparação do Ambiente Python

Este passo cria e ativa um ambiente virtual e instala as dependências.

```bash
# 1. Criar e ativar o ambiente virtual (Linux/Mac)
python -m venv venv
source venv/bin/activate 

# No Windows, use: 
.\venv\Scripts\activate

# 2. Instalar as dependências do ficheiro requirements.txt
pip install -r requirements.txt

# 3. Executar o serviço
uvicorn src.main:app --reload
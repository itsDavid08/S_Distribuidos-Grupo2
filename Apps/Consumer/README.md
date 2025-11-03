# Consumidor Redpanda (Python)

Este microserviço é um consumidor Redpanda (Kafka-compatible) em Python (FastAPI). O foco é o deploy em Kubernetes e a Gestão de Sistemas Distribuídos.

## ⚙️ Pré-requisitos Essenciais

Verifique se você tem instalado:

1. **Python 3.10+** e **pip**
2. **Docker** e **Docker Compose**

### 📌 Nota (Mac ARM / Apple Silicon)

O Redpanda funciona nativamente em Macs M1/M2/M3. Use os comandos abaixo normalmente.

## 🛠️ Guia Rápido de Instalação e Execução

Siga os comandos abaixo na pasta raiz do projeto (`redpanda-consumer-ms`).

### 1. Preparação do Ambiente Python

Este passo cria e ativa um ambiente virtual e instala as dependências.

```bash
# 1. Criar e ativar o ambiente virtual (Linux/Mac)
python -m venv venv
source venv/bin/activate 

# No Windows, use: .\venv\Scripts\activate

# 2. Instalar as dependências do ficheiro requirements.txt
pip install -r requirements.txt
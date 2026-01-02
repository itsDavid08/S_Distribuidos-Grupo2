# Repositório do Projeto de Sistemas Distribuídos

## Objetivos

O objetivo principal deste projeto é desenhar e implementar um sistema distribuído robusto, focado no processamento e visualização de dados em tempo real.

O projeto assenta em três pilares essenciais:

1. **Arquitetura de Microsserviços**
   Implementar um sistema distribuído baseado numa arquitetura de microsserviços, orquestrado com Kubernetes.

2. **Pipeline CI/CD (GitOps)**
   Construir um fluxo de trabalho automatizado de integração contínua e entrega contínua (CI/CD) usando GitHub Actions e ArgoCD, seguindo o modelo GitOps.

3. **Monitorização**
   Implementar monitorização dos microsserviços (requisito da Fase 2), com métricas enviadas para o Prometheus.

O sistema utiliza:

* **Aplicações:** UI (Node.js), Produtor (Python), Consumidor (Python)
* **Infraestrutura:** RabbitMQ (Broker) e MongoDB (Base de Dados)
* **CI (Integração):** GitHub Actions
* **CD (Entrega):** Argo CD
* **Orquestração:** Kubernetes (via Docker Desktop)
* **Monitorização:** Prometheus e Grafana

---

## Recomendações de Uso

* Trabalhe sempre numa branch própria antes de fazer um pull request.

  * Isto reduz conflitos e facilita a revisão.

---

## 🚀 Como Executar o Projeto (Primeira Entrega)

Siga estes 6 passos para configurar o ambiente e fazer o deploy automático do sistema.

---

## 1. Pré-requisitos (Software)

Certifique-se de que tem instalado:

1. **Git**
2. **Docker Desktop**
3. **kubectl**

---

## 2. Configuração do Ambiente

### 2.1. Clonar o Repositório

```bash
git clone https://github.com/itsDavid08/S_Distribuidos-Grupo2.git
cd S_Distribuidos-Grupo2
```

### 2.2. Ativar o Kubernetes (Docker Desktop)

1. Abra **Settings** no Docker Desktop
2. Aceda ao menu **Kubernetes**
3. Ative **Enable Kubernetes**
4. Aguarde até o ícone ficar verde

### 2.3. Configurar Segredos do GitHub (CI)

O pipeline de CI precisa de enviar imagens Docker para o Docker Hub.

1. Vá ao repositório → **Settings**
2. **Secrets and variables → Actions**
3. Crie os seguintes segredos:

| Nome                 | Descrição                                                |
| -------------------- | -------------------------------------------------------- |
| `DOCKERHUB_USERNAME` | O seu username (ex.: `itsDavid08`)                       |
| `DOCKERHUB_TOKEN`    | Token criado em Docker Hub → Security → New Access Token |

---

## 3. Acionar o Pipeline de CI (GitHub Actions)

1. Verifique se os YAMLs em `K8s-Config/Apps/` apontam para imagens no formato:

   ```
   image: itsDavid08/ui:1
   ```
2. Faça merge da sua branch para **main**
3. O GitHub Actions irá construir e enviar as imagens:

   * UI
   * Produtor
   * Consumidor
4. Acompanhe o progresso em **Actions**

---

## 4. Instalar e Configurar o Argo CD (CD)

### 4.1. Instalar o Argo CD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 4.2. Aceder à UI do Argo CD

```bash
# Expor a UI localmente no porto 8080
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Obter a password inicial:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o yaml
```

Decodificar a password:

```bash
echo 'PASSWORD_BASE64_AQUI' | base64 --decode
```

```bash
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("A_SUA_STRING_LONGA_EM_BASE64"))
```

Aceder:

* **URL:** [https://localhost:8080](https://localhost:8080)
* **Utilizador:** `admin`
* **Password:** (a que decodificou)

---

## 5. Ligar o Argo CD ao Repositório (Deploy Final)

Aplicar o ficheiro `argo-application.yml`:

```bash
kubectl apply -f argo-application.yml
```

O Argo CD irá agora monitorizar automaticamente o repositório e aplicar qualquer alteração feita na pasta `K8s-Config/`.

---

## 6. 🔍 Aceder aos Serviços e Pods (Fácil com Port-Forward)

### Método Rápido: Port-Forward

Use este método para aceder a qualquer serviço localmente:

```bash
# Grafana (Monitorização)
kubectl port-forward -n monitoring svc/grafana-service 3000:3000

# RabbitMQ Management
kubectl port-forward -n default svc/rabbit-dashboard-service 15672:15672

# Mongo Express (BD)
kubectl port-forward -n default svc/mongo-express-service 8081:8081

# Prometheus
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090

# UI (Node.js)
kubectl port-forward -n grupo2 svc/ui-service 3000:3000

# API (FastAPI)
kubectl port-forward -n grupo2 svc/api-service 8000:8000
```

Depois acede aos URLs abaixo.

---

## ✅ Acesso aos Serviços (Demo)

| Serviço           | URL (NodePort)                                   | Como Aceder (Port-Forward)                     |
| ----------------- | ------------------------------------------------ | ---------------------------------------------- |
| **UI**            | [http://localhost:30102](http://localhost:30102) | `kubectl port-forward -n grupo2 svc/ui-service 3000:3000` |
| **Argo CD**       | [https://localhost:8080](https://localhost:8080) | `kubectl port-forward -n argocd svc/argocd-server 8080:443` |
| **Grafana**       | [http://localhost:30202](http://localhost:30202) | `kubectl port-forward -n monitoring svc/grafana-service 3000:3000` |
| **Prometheus**    | [http://localhost:30902](http://localhost:30902) | `kubectl port-forward -n monitoring svc/prometheus-service 9090:9090` |
| **RabbitMQ**      | [http://localhost:30302](http://localhost:30302) | `kubectl port-forward -n default svc/rabbit-dashboard-service 15672:15672` |
| **Mongo Express** | [http://localhost:30402](http://localhost:30402) | `kubectl port-forward -n default svc/mongo-express-service 8081:8081` |

**Credenciais Padrão:**
* **Grafana:** admin / admin
* **RabbitMQ:** SD_RabbitMQ_Admin / SD_RabbitMQ_Admin123_PWD
* **Mongo Express:** admin / pass

---

## 📊 Comandos Úteis para Verificar Pods

### Ver todos os Pods

```bash
# Todos os Pods (todos os namespaces)
kubectl get pods -A

# Pods do Grupo 2
kubectl get pods -n grupo2

# Pods de Monitorização
kubectl get pods -n monitoring

# Pods do Argo CD
kubectl get pods -n argocd
```

### Ver Logs de um Pod

```bash
# Ver logs em tempo real
kubectl logs -f <nome-do-pod> -n <namespace>

# Exemplo: Logs do Grafana
kubectl logs -f grafana-deployment-58b6b588bd-lwq7j -n monitoring
```

### Descrever um Pod (ver detalhes)

```bash
kubectl describe pod <nome-do-pod> -n <namespace>
```

### Executar comandos dentro de um Pod

```bash
# Entrar numa shell do Pod
kubectl exec -it <nome-do-pod> -n <namespace> -- /bin/sh

# Exemplo: Verificar estado do RabbitMQ
kubectl exec -it rabbitmq-0 -n default -- rabbitmqctl status
```

---

## 📊 Métricas Disponíveis no Prometheus

### Aceder ao Prometheus

Abra o browser em: **http://localhost:30902**

Ou use port-forward:

```bash
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090
```

### Ver Targets Ativos

Vá a **Status** → **Targets** para ver todos os pods monitorizados.

### Consultas de Métricas

#### **API (FastAPI)**

```promql
# Total de pedidos recebidos
api_requests_total

# Duração dos pedidos (histograma)
api_request_duration_seconds_bucket

# Estado da conexão à base de dados (1 = conectado, 0 = desconectado)
api_db_connection_status
```

#### **Consumer (RabbitMQ)**

```promql
# Total de mensagens processadas
consumer_messages_processed_total

# Tempo de processamento de mensagens
consumer_message_processing_duration_seconds

# Timestamp da última mensagem processada
consumer_last_message_processed_timestamp_seconds
```

#### **Producer (Gerador de Dados)**

```promql
# Total de mensagens criadas
producer_messages_created_total

# Duração da criação de mensagens
total_message_creation_duration_seconds

# Timestamp da última mensagem gerada
producer_last_message_created_timestamp_seconds
```

#### **RabbitMQ (Message Broker)**

```promql
# Mensagens na fila
rabbitmq_queue_messages

# Consumidores ativos
rabbitmq_queue_consumers

# Taxa de publicação de mensagens
rate(rabbitmq_queue_messages_published_total[5m])
```

#### **MongoDB (Base de Dados)**

```promql
# Estado do MongoDB (1 = UP, 0 = DOWN)
mongodb_up

# Conexões ativas
mongodb_connections

# Operações por segundo
rate(mongodb_op_counters_total[5m])
```

#### **UI (Interface Web)**

```promql
# Total de pedidos HTTP
ui_http_requests_total

# Duração dos pedidos HTTP
ui_http_request_duration_seconds
```

### Exemplos de Consultas Avançadas

```promql
# Taxa de pedidos à API nos últimos 5 minutos
rate(api_requests_total[5m])

# Pedidos filtrados por endpoint
api_requests_total{endpoint="/dados"}

# Percentil 95 da latência da API
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Mensagens processadas por minuto
rate(consumer_messages_processed_total[1m]) * 60
```

---

## 🧹 Limpeza

### Eliminar o Argo CD

```bash
kubectl delete namespace argocd
```

### Eliminar a Aplicação

```bash
kubectl delete -f argo-application.yml
```

### Eliminar o Cluster Kind

```bash
kind delete cluster --name sd-cluster
```

---

## ❓ Troubleshooting

### Problema: "Não consigo aceder a localhost:30200"

**Solução:** Use `port-forward` em vez de NodePort:

```bash
kubectl port-forward -n monitoring svc/grafana-service 3000:3000
```

Depois acede a `http://localhost:3000`.

### Problema: Pod está em estado "Pending"

```bash
# Ver detalhes do Pod
kubectl describe pod <nome-do-pod> -n <namespace>

# Verificar recursos disponíveis
kubectl top nodes
```

### Problema: Argo CD não sincroniza

1. Verificar que o repositório é público
2. Verificar que o `targetRevision` é `main`
3. Forçar sincronização na UI do Argo CD



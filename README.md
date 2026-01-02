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
* **Infraestrutura:** MongoDB (Base de Dados), RabbitMQ compartilhado (rabbitmq-system)
* **CI (Integração):** GitHub Actions
* **CD (Entrega):** Argo CD
* **Orquestração:** Kubernetes (Cluster Remoto)
* **Monitorização:** Prometheus e Grafana compartilhados (namespace monitoring)

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

## 6. 🔍 Aceder aos Serviços e Pods

### Acesso aos Serviços do Cluster Remoto (Grupo 2)

| Serviço           | URL                                              | Namespace      |
| ----------------- | ------------------------------------------------ | -------------- |
| **UI**            | [http://10.2.15.161:30102](http://10.2.15.161:30102) | grupo2 |
| **Argo CD**       | [https://argocd.10.2.15.161.nip.io](https://argocd.10.2.15.161.nip.io) | argocd |
| **Grafana**       | [https://grafana.10.2.15.161.nip.io](https://grafana.10.2.15.161.nip.io) | monitoring (compartido) |
| **RabbitMQ**      | [https://rabbitmq.10.2.15.161.nip.io](https://rabbitmq.10.2.15.161.nip.io) | rabbitmq-system (compartido) |
| **Mongo Express** | [http://10.2.15.161:30402](http://10.2.15.161:30402) | grupo2 |

**Nota:** Los servicios de monitorización (Prometheus/Grafana) y RabbitMQ son compartidos por todos los grupos en el cluster.

---

## 📊 Comandos Útiles para Verificar Pods

### Ver todos los Pods del Grupo 2

```bash
# Pods del Grupo 2
kubectl get pods -n grupo2

# Todos los Pods (todos los namespaces)
kubectl get pods -A
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

## 📊 Métricas en Prometheus

Las métricas de las aplicaciones del Grupo 2 están disponibles en el Prometheus compartido.

Acceder a Grafana: [https://grafana.10.2.15.161.nip.io](https://grafana.10.2.15.161.nip.io)

### Consultas de Métricas del Grupo 2

#### **API (FastAPI)**

```promql
# Total de pedidos recebidos
api_requests_total

# Duração dos pedidos (histograma)
api_request_duration_seconds_bucket

# Estado da conexão à base de dados
api_db_connection_status
```

#### **Consumer (RabbitMQ)**

```promql
# Total de mensagens processadas
consumer_messages_processed_total

# Tempo de processamento
consumer_message_processing_duration_seconds
```

#### **Producer (Gerador de Dados)**

```promql
# Total de mensagens criadas
producer_messages_created_total

# Duração da criação de mensagens
total_message_creation_duration_seconds
```

---

## 🧹 Comandos Útiles

### Ver estado de los deployments

```bash
kubectl get deployments -n grupo2
kubectl get pods -n grupo2
kubectl get svc -n grupo2
```

### Ver logs

```bash
kubectl logs -f <pod-name> -n grupo2
```

---

## ❓ Troubleshooting

### Problema: Pod en estado "Pending"

```bash
kubectl describe pod <nome-do-pod> -n grupo2
```

### Problema: Argo CD no sincroniza

1. Verificar que el repositorio es público
2. Verificar que el `targetRevision` es `main`
3. Forzar sincronización en la UI de Argo CD



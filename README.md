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

## 6. 🔍 Aceder aos Serviços e Interfaces Web

### Serviços do Grupo 2 no Cluster Remoto

Seguem-se os URLs para aceder às interfaces web do sistema.

#### **Aplicações do Grupo 2**

| Serviço           | URL                                              | Descrição | Credenciais |
| ----------------- | ------------------------------------------------ | ----------- | ------------ |
| **🎯 UI Principal** | [http://10.2.15.161:30102](http://10.2.15.161:30102) | Interface web do sistema (mapa em tempo real) | - |
| **📊 Mongo Express** | [http://10.2.15.161:30402](http://10.2.15.161:30402) | Administração de MongoDB | utilizador: `SD_Mongo_Admin`<br>password: `SD_Mongo_Admin123_PWD` |

#### **Serviços Partilhados do Cluster (Infraestrutura)**

| Serviço           | URL                                              | Descrição | Credenciais |
| ----------------- | ------------------------------------------------ | ----------- | ------------ |
| **🚀 Argo CD**       | [https://argocd.10.2.15.161.nip.io](https://argocd.10.2.15.161.nip.io) | CI/CD e sincronização GitOps | utilizador: `admin`<br>password: (ver secção 4.2) |
| **📈 Grafana**       | [https://grafana.10.2.15.161.nip.io](https://grafana.10.2.15.161.nip.io) | Dashboards de métricas e monitorização | utilizador: `admin`<br>password: (configurado no cluster) |
| **🐰 RabbitMQ**      | [https://rabbitmq.10.2.15.161.nip.io](https://rabbitmq.10.2.15.161.nip.io) | Gestão de filas de mensagens | utilizador: `grupo2`<br>password: `s2d3f4g5h6j7` |

**Nota Importante:** 
- Os serviços de **Grafana**, **Prometheus** e **RabbitMQ** são **partilhados** por todos os grupos do cluster.
- Apenas a **UI Principal** e o **Mongo Express** são exclusivos do Grupo 2.

### ⚠️ Problemas de Acesso

Se não conseguir aceder aos URLs:
1. Verifique que está ligado à rede do laboratório
2. Confirme que os pods estão em execução: `kubectl get pods -n grupo2`
3. Para RabbitMQ/Grafana/Argo CD, use os URLs com **https://** (certificados auto-assinados, aceite o aviso do navegador)
4. Para UI e Mongo Express, use **http://** (sem SSL)

---

## 📊 Comandos Úteis para Verificar o Sistema

### Ver Estado Geral do Grupo 2

```bash
# Ver todos os Pods do Grupo 2
kubectl get pods -n grupo2

# Ver os Deployments
kubectl get deployments -n grupo2

# Ver os Serviços expostos
kubectl get svc -n grupo2

# Ver tudo de uma vez (pods, deployments, services, HPAs)
kubectl get all -n grupo2
```

### Verificar Logs em Tempo Real

```bash
# Logs do Produtor
kubectl logs -f -l app=produtor -n grupo2

# Logs do Consumidor
kubectl logs -f -l app=consumidor -n grupo2

# Logs da API
kubectl logs -f -l app=api -n grupo2

# Logs da UI
kubectl logs -f -l app=ui -n grupo2
```

### Diagnosticar Problemas

```bash
# Descrever um Pod (ver eventos e erros)
kubectl describe pod <nome-do-pod> -n grupo2

# Ver eventos recentes do namespace
kubectl get events -n grupo2 --sort-by='.lastTimestamp'

# Verificar estado dos HPA (auto-scaling)
kubectl get hpa -n grupo2
```

### Aceder ao Interior de um Pod

```bash
# Abrir uma shell dentro de um Pod
kubectl exec -it <nome-do-pod> -n grupo2 -- /bin/sh

# Exemplo: Verificar variáveis de ambiente no Consumidor
kubectl exec -it <consumidor-pod> -n grupo2 -- env | grep RABBITMQ
```

### Reiniciar Pods

```bash
# Eliminar pod para forçar recriação com nova imagem
kubectl delete pod -l app=consumidor -n grupo2

# Reiniciar um deployment completo
kubectl rollout restart deployment/consumidor-deployment -n grupo2
```

---

## 📊 Métricas Disponíveis no Prometheus

As métricas das aplicações do Grupo 2 estão disponíveis no Prometheus partilhado.

Aceder ao Grafana: [https://grafana.10.2.15.161.nip.io](https://grafana.10.2.15.161.nip.io)

### Consultas de Métricas do Grupo 2

#### **API (FastAPI)**

```promql
# Total de pedidos recebidos
api_requests_total

# Duração dos pedidos (histograma)
api_request_duration_seconds_bucket

# Estado da ligação à base de dados
api_db_connection_status
```

#### **Consumidor (RabbitMQ)**

```promql
# Total de mensagens processadas
consumer_messages_processed_total

# Tempo de processamento
consumer_message_processing_duration_seconds
```

#### **Produtor (Gerador de Dados)**

```promql
# Total de mensagens criadas
producer_messages_created_total

# Duração da criação de mensagens
total_message_creation_duration_seconds
```

---

## 🧹 Comandos Úteis Adicionais

### Ver estado dos deployments

```bash
kubectl get deployments -n grupo2
kubectl get pods -n grupo2
kubectl get svc -n grupo2
```

### Ver logs

```bash
kubectl logs -f <nome-do-pod> -n grupo2
```

---

## ❓ Resolução de Problemas

### Problema: Pod em estado "Pending"

```bash
kubectl describe pod <nome-do-pod> -n grupo2
```

Verifique se há problemas de recursos (CPU/memória) ou problemas de agendamento de nós.

### Problema: Argo CD não sincroniza

1. Verificar que o repositório é público
2. Verificar que o `targetRevision` é `main`
3. Forçar sincronização na UI do Argo CD

### Problema: Pods em CrashLoopBackOff

```bash
# Ver logs do pod com erro
kubectl logs <nome-do-pod> -n grupo2

# Ver logs anteriores (antes do crash)
kubectl logs <nome-do-pod> -n grupo2 --previous
```

Causas comuns:
- Credenciais erradas (MongoDB, RabbitMQ)
- Serviços de dependência não disponíveis
- Erro no código da aplicação

### Problema: Não consigo aceder à UI

1. Verificar que o serviço está a correr:
   ```bash
   kubectl get pods -n grupo2 -l app=ui
   ```

2. Verificar que o NodePort está correto:
   ```bash
   kubectl get svc -n grupo2 ui-service
   ```

3. Confirmar que está a usar o IP correto do cluster: `10.2.15.161`

4. Testar conectividade de rede:
   ```bash
   curl http://10.2.15.161:30102
   ```



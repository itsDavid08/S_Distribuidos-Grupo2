
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

* **Aplicações:** UI (Node.js), Produtor (Java), Consumidor (Python)
* **Infraestrutura:** RabbitMQ (Broker) e MongoDB (Base de Dados)
* **CI (Integração):** GitHub Actions
* **CD (Entrega):** Argo CD
* **Orquestração:** Kubernetes (via Docker Desktop)

---

## Recomendações de Uso

* Trabalhe sempre numa branch própria antes de fazer um pull request.

  * Isto reduz conflitos e facilita a revisão.

---

## 🚀 Como Executar o Projeto (Primeira Entrega)

Siga estes 5 passos para configurar o ambiente e fazer o deploy automático do sistema.

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

1. Verifique se os YAMLs em `k8s-config/Apps/` apontam para imagens no formato:

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

* **URL:** [http://localhost:8080](http://localhost:8080)
* **Utilizador:** `admin`
* **Password:** (a que decodificou)

---

## 5. Ligar o Argo CD ao Repositório (Deploy Final)

Crie o ficheiro `argo-application.yml` na raiz do projeto:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: projeto-streaming
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/itsDavid08/S_Distribuidos-Grupo2.git
    targetRevision: main
    path: k8s-config/
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
    syncOptions:
      - CreateNamespace=true
```

Aplicar o ficheiro ao cluster:

```bash
kubectl apply -f argo-application.yml
```

O Argo CD irá agora monitorizar automaticamente o repositório e aplicar qualquer alteração feita na pasta `k8s-config/`.

---

## ✅ Acesso aos Serviços (Demo)

| Serviço           | URL                                              | Ficheiro de Configuração                 |
| ----------------- | ------------------------------------------------ | ---------------------------------------- |
| **UI**            | [http://localhost:30100](http://localhost:30100) | `Apps/ui.yml`                            |
| **Argo CD**       | [http://localhost:8080](http://localhost:8080)   | via port-forward                         |
| **RabbitMQ**      | [http://localhost:30300](http://localhost:30300) | `Infraestrutura/RabbitMQ/rabbit.yml`     |
| **Mongo Express** | [http://localhost:30400](http://localhost:30400) | `Infraestrutura/Mongo/mongo-express.yml` |



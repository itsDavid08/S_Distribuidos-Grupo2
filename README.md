# Repositorio do Projeto de Sistemas Distribuidos

## Objetivos

O objetivo principal deste projeto é desenhar e implementar um sistema distribuído robusto, focado no processamento e visualização de dados em tempo real.

Para tal, o projeto foca-se em três pilares essenciais:

1.  **Arquitetura de Microsserviços:**
    -  Desenhar e implementar um sistema distribuído baseado numa arquitetura de microsserviços, orquestrado através de Kubernetes.
    -   O sistema deverá ser capaz de suportar o processamento e a visualização de dados (como a localização de participantes numa corrida) em tempo real.

2.  **Pipeline CI/CD (GitOps):**
    - Construir um fluxo de trabalho automatizado de integração contínua e entrega contínua (CI/CD).
    - Este pipeline utilizará Github Actions para a integração (testes e construção de imagens) e ArgoCD para a entrega contínua (deployment) no cluster, seguindo os princípios GitOps.

3.  **Monitorização:**
    - Implementar a monitorização completa dos serviços.
    - As métricas relevantes de cada microsserviço serão recolhidas e enviadas para o Prometheus, permitindo a observabilidade do sistema.

O sistema utiliza:
* **Aplicações:** UI (Node.js), Produtor (Java), Consumidor (Python)
* **Infraestrutura:** RabbitMQ (Broker) e MongoDB (Base de Dados)
* **CI (Integração):** GitHub Actions (para testes e construção de imagens)
* **CD (Entrega):** Argo CD (para deployment GitOps)
* **Orquestração:** Kubernetes (através do Docker Desktop)

## Recomendações de usos
- Trabalhar numa branch propia para fazer as alterações e seguidamente fazer um pull request
    - Isto para evitar conflitos de commits



## 🚀 Como Executar o Projeto (Primeira Entrega)

Siga estes 5 passos para configurar o ambiente e fazer o deploy automático da aplicação.

### 1. Pré-requisitos (Software)

Antes de começar, certifique-se de que tem o seguinte software instalado:
1.  **Git:** Para clonar o repositório.
2.  **Docker Desktop:** A forma mais fácil de correr um cluster Kubernetes local.
3.  **kubectl:** A ferramenta de linha de comandos do Kubernetes.

### 2. Configuração do Ambiente

#### 2.1. Clonar o Repositório

- ``git clone https://github.com/kingdavid08/S_Distribuidos-Grupo2.git``
- ``cd S_Distribuidos-Grupo2``


#### 2.2. Ativar o Kubernetes

1. Abra as **Definições (Settings)** do Docker Desktop.
    
2. Vá a **Kubernetes**.
    
3. Marque a caixa **Enable Kubernetes**.
    
4. Aguarde até que o Kubernetes esteja a funcionar (o ícone do Docker Desktop ficará verde).
    

#### 2.3. Configurar Segredos do GitHub (CI)

O nosso pipeline de CI (GitHub Actions) precisa de enviar as imagens para o Docker Hub.

1. Vá às **Definições (Settings)** do seu repositório no GitHub.
    
2. Vá a **Secrets and variables** > **Actions**.
    
3. Crie os seguintes segredos de repositório:
    
    - `DOCKERHUB_USERNAME`: O seu username (ex: `kingdavid08`).
        
    - `DOCKERHUB_TOKEN`: Um Token de Acesso (Access Token) que pode gerar nas definições da sua conta do Docker Hub (Security > New Access Token).
        

### 3. Acionar o Pipeline de CI (GitHub Actions)

O pipeline de CI (Passo 3 do nosso plano) constrói as suas imagens.

1. Verifique se os seus YAMLs em `k8s-config/Apps/` estão a apontar para as imagens corretas (ex: `image: kingdavid08/ui:1`).
    
2. Faça **Merge** da sua _branch_ de trabalho para a _branch_ `main`.
    
3. Ao fazer `push` (ou _Merge_) para a `main`, o GitHub Actions (definido em `.github/workflows/ci-pipeline.yml`) será acionado.
    
4. Vá ao separador **Actions** do seu repositório no GitHub e veja o _workflow_ a construir e a enviar as suas 3 imagens (UI, Produtor, Consumidor) para o Docker Hub com a _tag_ `:1`.
    

### 4. Instalar e Configurar o Argo CD (CD)

Agora que as imagens existem, vamos configurar o Argo CD para as implementar (Passo 4 do nosso plano).

#### 4.1. Instalar o Argo CD

Execute estes comandos no seu terminal para instalar o Argo CD no seu cluster Kubernetes.


1. Criar o namespace para o Argo CD
    - kubectl create namespace argocd

2. Aplicar o manifesto de instalação oficial
    - ``kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml``


#### 4.2. Aceder à UI do Argo CD

Para obter a password e aceder à interface web do Argo CD.


3. Expor a UI no seu localhost:8080 (deixe este comando a correr)
    - ``kubectl port-forward svc/argocd-server -n argocd 8080:443``

4. Obter a password (que é auto-gerada)
    - ``kubectl get secret argocd-initial-admin-secret -n argocd -o yaml
``
5. Copie o valor de 'data.password:' (ex: NjgzeEItUXVUcGhaNUNZNw==)
6. Decodifique a password:
    - ``echo 'PASSWORD_BASE64_AQUI' | base64 --decode``

    ou em Windows PowerShell
    - ``[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("PASSWORD_BASE64"))``


- **URL:** `http://localhost:8080`
    
- **Utilizador:** `admin`
    
- **Password:** A password que acabou de decodificar.
    

### 5. Ligar o Argo CD ao seu Repositório (O Deploy Final)

O último passo é dizer ao Argo CD para monitorizar o seu projeto.

1. Certifique-se de que o seu ficheiro `argo-application.yml` (que criámos no Passo 4 do nosso plano) está na raiz do seu projeto.
    
2. Aplique este ficheiro ao seu cluster:
    
- Este comando diz ao Argo CD: "Começa a monitorizar o meu repositório"
    - ``kubectl apply -f argo-application.yml``

    
3. Abra a UI do Argo CD (`http://localhost:8080`).
    
4. Verá uma nova aplicação chamada `projeto-streaming`. Clique nela.
    
5. O Argo CD irá automaticamente sincronizar-se com a sua pasta `k8s-config/` no Git e implementar **todos** os seus serviços (RabbitMQ, MongoDB, UI, Produtor, Consumidor).
    
6. Em poucos minutos, todos os serviços estarão a funcionar.
    

---

## ✅ Acesso aos Serviços (Demo)

Após o Argo CD terminar a sincronização, pode aceder a todas as interfaces do seu sistema:

- **UI (A sua Aplicação):**
    
    - URL: `http://localhost:30100`
        
    - (Definido no `k8s-config/Apps/ui.yml`)
        
- **Argo CD (Gestão de Deployments):**
    
    - URL: `http://localhost:8080`
        
    - (Definido pelo `kubectl port-forward`)
        
- **RabbitMQ (Dashboard do Broker):**
    
    - URL: `http://localhost:30300`
        
    - (Login: `guest` / `guest` ou as credenciais que definiu)
        
    - (Definido no `k8s-config/Infraestrutura/rabbit.yml`)
        
- **Mongo Express (Dashboard da Base de Dados):**
    
    - URL: `http://localhost:30400`
        
    - (Login: as credenciais que definiu no `mongo-secret.yml`)
        
    - (Definido no `k8s-config/Infraestrutura/mongo-express.yml`)
      
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

## Recomendações de usos
- Trabalhar numa branch propia para fazer as alterações e seguidamente fazer um pull request
    - Isto para evitar conflitos de commits

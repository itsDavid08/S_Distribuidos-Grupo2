"""
Configurações centrais da aplicação.

Este módulo contém as variáveis de configuração estáticas, como os endereços
dos brokers Redpanda, o nome do tópico e o ID do grupo de consumidores.
"""

REDPANDA_BROKERS = ['localhost:9092']
TOPIC_NAME = 'real_time_data'
GROUP_ID = 'consumer'
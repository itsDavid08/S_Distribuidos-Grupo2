from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore'  # Ignora campos extras no .env se houver
    )

    # RabbitMQ
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    QUEUE_NAME: str = 'real_time_data'

    # MongoDB
    MONGO_URL: str
    MONGO_USER: str
    MONGO_PASS: str
    DB_NAME: str = 'projeto_sd'
    COLLECTION_NAME: str = 'dados_corrida' 

settings = Settings()
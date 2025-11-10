from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_HOST: str = 'localhost'
    QUEUE_NAME: str = 'real_time_data'
    GROUP_ID: str = 'my-group'


settings = Settings()
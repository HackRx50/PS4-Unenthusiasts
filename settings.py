from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str
    db_api_key: str
    openai_api_key: str
    mongo_uri: str
    mongo_db_name: str = "default_db_name"  
    llama_cloud_api_key: str
    jwt_secret_key:str
    jwt_refresh_secret:str

    class Config:
        env_file = ".env" 


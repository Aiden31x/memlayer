from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = 'gemini-3-flash-preview'
    embedding_model: str = 'all-MiniLM-L6-v2'
    database_url: str
   
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "memories"
    embedding_dimension: int = 384
   
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')




settings = Settings()
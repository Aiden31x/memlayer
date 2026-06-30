from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    model_name: str = 'gemini-3-flash-preview'
    embedding_model: str = 'all-MiniLM-L6-v2'
    database_url: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')




settings = Settings()
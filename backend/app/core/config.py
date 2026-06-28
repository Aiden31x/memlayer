from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    google_api_key: str
    model_name: str= 'gemini-2.5-flash'
    database_url: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
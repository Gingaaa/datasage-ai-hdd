from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    project_name: str = "Intelligent Data Dictionary Agent"
    version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # Ollama Local Configuration
    ollama_base_url: str = Field(default="http://localhost:11434/api")
    ollama_model: str = Field(default="llama3:8b")

    class Config:
        env_file = ".env"

settings = Settings()

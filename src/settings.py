from pydantic import Field
from pydantic_settings import SettingsConfigDict,BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Basic API Users"
    version: str = "1.0.0"
    author: str = "Roni Hernandez"
    PROFILE_IMAGE_URL: str = "https://avatars.githubusercontent.com/u/40522363?v=4"
    environment: str = Field(..., env="ENVIRONMENT")
    PRIVATE_KEY: str = Field(..., env="PRIVATE_KEY")
    PUBLIC_KEY: str = Field(..., env="PUBLIC_KEY")
    jwt_algorithm: str = "RS256"
    jwt_expiration_minutes: int = 10
    DATABASE_URL: str
    DOMAIN: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
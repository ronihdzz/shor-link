from pydantic import Field
from pydantic_settings import SettingsConfigDict,BaseSettings

class Settings(BaseSettings):
    project_name: str = "Basic API Users"
    version: str = "1.0.0"
    author: str = "Roni Hernandez"
    profile_image_url: str = "https://davidronihdz99.pythonanywhere.com/media/fotosPerfil/roni_3dqmEf6.jpg"
    environment: str = Field(..., env="ENVIRONMENT")
    private_key: str = Field(..., env="PRIVATE_KEY")
    public_key: str = Field(..., env="PUBLIC_KEY")
    jwt_algorithm: str = "RS256"
    jwt_expiration_minutes: int = 10
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
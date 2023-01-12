from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    DB_NAME: str = Field(default="database", description="Name of the database", env="DB_NAME")
    DB_USER: str = Field(default="db_admin", description="User of the database", env="DB_USER")
    DB_HOST: str = Field(default="localhost", description="Host of the database", env="DB_HOST")
    DB_PORT: str = Field(default="5431", description="Port of the database", env="DB_PORT")
    DB_PASSWORD: str = Field(default="db_password", description="Password of the database", env="DB_PASSWORD")


DatabaseConfig = DatabaseConfig()


class ServerConfig(BaseSettings):
    HOST: str = Field(default="0.0.0.0", description="Host of the application", env="SERVER_HOST")
    PORT: int = Field(default=8080, description="Port of the application", env="SERVER_PORT")


ServerConfig = ServerConfig()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    database_url: str = "sqlite:///./finance_tracker.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:80"
    gemini_model: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

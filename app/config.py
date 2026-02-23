from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Railway даст DATABASE_URL автоматически, если подключишь Postgres plugin
    DATABASE_URL: str

    # Green API
    GREEN_API_ID_INSTANCE: str
    GREEN_API_TOKEN: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"  # можно поменять в Railway Variables

    # Таймзона (ты писал Asia/Qyzylorda)
    TIMEZONE: str = "Asia/Qyzylorda"

    # Безопасность вебхука (необязательно, но лучше иметь)
    WEBHOOK_SECRET: str = ""  # если оставишь пустым — проверка выключена

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
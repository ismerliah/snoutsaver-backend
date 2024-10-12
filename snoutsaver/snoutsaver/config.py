from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLDB_URL: str
    SECRET_KEY: str = "secret"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5 * 60 # 1 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60 # 7 days
    # test
    # REFRESH_TOKEN_EXPIRE_MINUTES: int = 1 # 1 minute

    model_config = SettingsConfigDict(
        env_file=".env", validate_assignment=True, extra="allow"
    )


def get_settings():
    return Settings()


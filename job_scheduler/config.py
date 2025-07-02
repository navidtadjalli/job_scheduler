from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from job_scheduler.constants import Phase


class Settings(BaseSettings):
    phase: str = Field(default=Phase.Production)
    redis_url: str = Field(..., description="Redis connection URI")
    db_url: str = Field(..., description="PostgreSQL connection URI")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        print("Invalid configuration:")
        print(e)
        raise


settings = get_settings()

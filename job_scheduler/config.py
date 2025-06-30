import logging

from pydantic import Field
from pydantic_settings import BaseSettings

from job_scheduler.constants import PastTaskPolicy


class Settings(BaseSettings):
    redis_url: str = Field(default="redis://localhost:6379/0")
    db_url: str = Field(default="sqlite:///./tasks.db")
    recover_past_tasks: PastTaskPolicy = Field(default=PastTaskPolicy.FAIL)
    log_level: int = Field(default=logging.DEBUG)

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()

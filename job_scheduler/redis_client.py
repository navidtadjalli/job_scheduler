import redis

from job_scheduler.config import settings

redis_client = redis.Redis.from_url(settings.redis_url)

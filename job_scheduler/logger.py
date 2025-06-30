import logging

from job_scheduler.config import settings

# Create a custom logger
logger = logging.getLogger("job_scheduler")
logger.setLevel(settings.log_level)  # Change to INFO in prod

# Console handler
ch = logging.StreamHandler()
ch.setLevel(settings.log_level)

# Formatter
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)

# Attach handler (only once)
if not logger.hasHandlers():
    logger.addHandler(ch)

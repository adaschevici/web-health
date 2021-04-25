import logging
import sys

from loguru import logger
from starlette.config import Config
from app.core.logging import InterceptHandler

config = Config(".env")


PROJECT_NAME: str = config("PROJECT_NAME", default="web-health-check-producer")
ONCE_EVERY: int = config("ONCE_EVERY", default=5, cast=int)
URLS_FILE: str = config("URLS_FILE")
TOPIC_NAME: str = config("TOPIC_NAME", default="sitehealth")
KAFKA_URI: str = config("KAFKA_URI")
KAFKA_PORT: str = config("KAFKA_PORT")
KAFKA_INSTANCE = f"{KAFKA_URI}:{KAFKA_PORT}"
DEBUG: bool = config("DEBUG", cast=bool, default=False)

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

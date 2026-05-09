import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class ConfigError(RuntimeError):
    """Raised when required environment variables are missing."""


@dataclass(frozen=True)
class Config:
    bot_token: str
    bot_username: str
    db_path: Path
    connect_banner_path: Path
    log_level: str


def _clean_username(value: str | None) -> str:
    return (value or "").strip().lstrip("@")


def setup_logging(log_level: str) -> None:
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def load_config() -> Config:
    load_dotenv()

    bot_token = (os.getenv("BOT_TOKEN") or "").strip()
    bot_username = _clean_username(os.getenv("BOT_USERNAME"))
    db_path = Path(os.getenv("DB_PATH", "storage/bot.sqlite3"))
    connect_banner_path = Path(
        os.getenv("CONNECT_BANNER_PATH", "assets/connect_banner.png")
    )
    log_level = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()

    if not bot_token:
        logger.error("Configuration error: BOT_TOKEN is required")
        raise ConfigError("BOT_TOKEN is required")

    if not bot_username:
        logger.error("Configuration error: BOT_USERNAME is required")
        raise ConfigError("BOT_USERNAME is required")

    return Config(
        bot_token=bot_token,
        bot_username=bot_username,
        db_path=db_path,
        connect_banner_path=connect_banner_path,
        log_level=log_level,
    )

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.config import ConfigError, load_config, setup_logging
from app.database import Database
from app.handlers_business import router as business_router
from app.handlers_start import router as start_router


logger = logging.getLogger(__name__)

ALLOWED_UPDATES = [
    "message",
    "callback_query",
    "business_connection",
    "business_message",
    "edited_business_message",
    "deleted_business_messages",
]


async def main() -> None:
    load_dotenv()
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))
    logger.info("Starting bot")

    try:
        config = load_config()
    except ConfigError:
        return

    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    config.connect_banner_path.parent.mkdir(parents=True, exist_ok=True)

    db = Database(config.db_path)
    await db.init()

    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher(db=db, config=config)
    dispatcher.include_router(start_router)
    dispatcher.include_router(business_router)

    logger.info("Polling started with allowed_updates=%s", ALLOWED_UPDATES)
    try:
        await dispatcher.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

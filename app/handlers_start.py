import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.config import Config
from app.keyboards import DEMO_CALLBACK_DATA, build_start_keyboard


logger = logging.getLogger(__name__)
router = Router(name="start")


def _start_text(bot_username: str) -> str:
    return (
        "Добро пожаловать! 🕵️\n"
        "Этот бот создан, чтобы помогать вам в переписке.\n\n"
        "Возможности бота:\n"
        "• Моментально пришлёт уведомление, если ваш собеседник изменит "
        "или удалит сообщение 🔔\n\n"
        "❓ Подключить бот:\n"
        "1. Нажмите кнопку “🟢 Подключить”\n"
        "2. В открывшихся настройках нажмите “Редактировать профиль”\n"
        "3. Откройте “Автоматизация чатов” и добавьте бота: "
        f"@{bot_username}"
    )


def _demo_text(bot_username: str) -> str:
    return (
        "Демонстрация работы бота.\n\n"
        "Собеседник изменяет сообщение — бот присылает старый и новый текст.\n\n"
        "Пример:\n"
        "Иван (@ivan123) изменил(а) сообщение:\n\n"
        "Старое сообщение:\n\n"
        "Привет\n\n"
        "Новое сообщение:\n\n"
        "Привет)\n\n"
        f"@{bot_username}\n\n"
        "Собеседник удаляет сообщение — бот присылает сохранённый текст "
        "удалённого сообщения.\n\n"
        "Пример:\n"
        "Иван (@ivan123) удалил(а) сообщение:\n\n"
        "Как дела?\n\n"
        f"@{bot_username}\n\n"
        "Бот работает даже когда вы оффлайн"
    )


@router.message(CommandStart())
async def handle_start(message: Message, config: Config) -> None:
    if config.connect_banner_path.is_file():
        try:
            await message.answer_photo(FSInputFile(config.connect_banner_path))
        except Exception:
            logger.exception("Failed to send connect banner")

    await message.answer(
        _start_text(config.bot_username),
        reply_markup=build_start_keyboard(),
    )


@router.callback_query(F.data == DEMO_CALLBACK_DATA)
async def handle_demo_callback(callback: CallbackQuery, config: Config) -> None:
    await callback.answer()
    if callback.message is None:
        return
    await callback.message.answer(_demo_text(config.bot_username))

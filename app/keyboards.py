from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


DEMO_CALLBACK_DATA = "demo_business_tracking"


def build_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Подключить",
                    url="tg://settings",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🕵️ Демонстрация работы бота",
                    callback_data=DEMO_CALLBACK_DATA,
                )
            ],
        ]
    )

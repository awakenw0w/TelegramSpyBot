import logging
from datetime import datetime
from typing import Any

from aiogram import Bot, Router
from aiogram.types import BusinessConnection, BusinessMessagesDeleted, Message

from app.config import Config
from app.database import Database
from app.formatters import (
    build_sender_display_name,
    build_sender_label,
    format_delete_notification,
    format_edit_notification,
    get_message_text_or_caption,
)


logger = logging.getLogger(__name__)
router = Router(name="business")


@router.business_connection()
async def handle_business_connection(
    business_connection: BusinessConnection,
    bot: Bot,
    db: Database,
) -> None:
    try:
        connection_id = business_connection.id
        owner_user_id = int(
            getattr(business_connection, "user_chat_id", None)
            or business_connection.user.id
        )
        is_enabled = bool(business_connection.is_enabled)
        can_reply = bool(business_connection.can_reply)

        logger.info(
            "Received business_connection id=%s owner_user_id=%s is_enabled=%s can_reply=%s",
            connection_id,
            owner_user_id,
            is_enabled,
            can_reply,
        )

        await db.upsert_business_connection(
            business_connection_id=connection_id,
            owner_user_id=owner_user_id,
            is_enabled=is_enabled,
            can_reply=can_reply,
        )

        if is_enabled:
            await _send_owner_notification(
                bot,
                owner_user_id,
                "✅ Бот подключён. Теперь я буду уведомлять вас, если "
                "собеседник изменит или удалит сообщение",
            )
        else:
            await _send_owner_notification(
                bot,
                owner_user_id,
                "⚠️ Бот отключён от автоматизации чатов",
            )
    except Exception:
        logger.exception("Failed to handle business_connection")


@router.business_message()
async def handle_business_message(message: Message, db: Database) -> None:
    try:
        connection_id = message.business_connection_id
        if not connection_id:
            logger.warning("business_message without business_connection_id")
            return

        owner_user_id = await db.get_owner_user_id(connection_id)
        if owner_user_id is None:
            logger.warning(
                "Owner not found for business_message business_connection_id=%s",
                connection_id,
            )

        logger.info(
            "Received business_message business_connection_id=%s chat_id=%s message_id=%s",
            connection_id,
            message.chat.id,
            message.message_id,
        )

        await db.save_message(_message_to_db_data(message, connection_id))
    except Exception:
        logger.exception("Failed to handle business_message")


@router.edited_business_message()
async def handle_edited_business_message(
    message: Message,
    bot: Bot,
    db: Database,
    config: Config,
) -> None:
    try:
        connection_id = message.business_connection_id
        if not connection_id:
            logger.warning("edited_business_message without business_connection_id")
            return

        chat_id = message.chat.id
        message_id = message.message_id
        owner_user_id = await db.get_owner_user_id(connection_id)
        old_message = await db.get_message(connection_id, chat_id, message_id)
        new_text = get_message_text_or_caption(
            message.text,
            message.caption,
            limit=1600,
        )

        logger.info(
            "Received edited_business_message business_connection_id=%s chat_id=%s message_id=%s",
            connection_id,
            chat_id,
            message_id,
        )

        if old_message is None:
            await db.save_message(
                _message_to_db_data(
                    message,
                    connection_id,
                    fallback_message=old_message,
                )
            )
            notification = format_edit_notification(
                "Пользователь",
                "Не удалось найти старую версию сообщения",
                new_text,
                config.bot_username,
            )
        else:
            sender_label = build_sender_label(
                old_message.get("sender_display_name"),
                old_message.get("sender_username"),
            )
            old_text = get_message_text_or_caption(
                old_message.get("text"),
                old_message.get("caption"),
                limit=1600,
            )
            notification = format_edit_notification(
                sender_label,
                old_text,
                new_text,
                config.bot_username,
            )
            await db.save_message(
                _message_to_db_data(
                    message,
                    connection_id,
                    fallback_message=old_message,
                )
            )

        if owner_user_id is None:
            logger.warning(
                "Owner not found for edited_business_message business_connection_id=%s",
                connection_id,
            )
            return

        await _send_owner_notification(bot, owner_user_id, notification)
    except Exception:
        logger.exception("Failed to handle edited_business_message")


@router.deleted_business_messages()
async def handle_deleted_business_messages(
    deleted: BusinessMessagesDeleted,
    bot: Bot,
    db: Database,
    config: Config,
) -> None:
    try:
        connection_id = deleted.business_connection_id
        chat_id = deleted.chat.id
        owner_user_id = await db.get_owner_user_id(connection_id)

        logger.info(
            "Received deleted_business_messages business_connection_id=%s chat_id=%s message_ids=%s",
            connection_id,
            chat_id,
            deleted.message_ids,
        )

        if owner_user_id is None:
            logger.warning(
                "Owner not found for deleted_business_messages business_connection_id=%s",
                connection_id,
            )
            return

        for message_id in deleted.message_ids:
            try:
                saved_message = await db.get_message(connection_id, chat_id, message_id)

                if saved_message is None:
                    notification = format_delete_notification(
                        "Пользователь",
                        "Не удалось найти текст сообщения в базе",
                        config.bot_username,
                    )
                else:
                    sender_label = build_sender_label(
                        saved_message.get("sender_display_name"),
                        saved_message.get("sender_username"),
                    )
                    text = get_message_text_or_caption(
                        saved_message.get("text"),
                        saved_message.get("caption"),
                        limit=3500,
                    )
                    notification = format_delete_notification(
                        sender_label,
                        text,
                        config.bot_username,
                    )
                    await db.mark_message_deleted(connection_id, chat_id, message_id)

                await _send_owner_notification(bot, owner_user_id, notification)
            except Exception:
                logger.exception(
                    "Failed to process deleted message business_connection_id=%s chat_id=%s message_id=%s",
                    connection_id,
                    chat_id,
                    message_id,
                )
    except Exception:
        logger.exception("Failed to handle deleted_business_messages")


def _message_to_db_data(
    message: Message,
    business_connection_id: str,
    fallback_message: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sender = message.from_user
    if sender:
        sender_first_name = sender.first_name
        sender_last_name = sender.last_name
        sender_username = sender.username
        sender_display_name = build_sender_display_name(
            sender_first_name,
            sender_last_name,
            sender_username,
        )
        sender_id = sender.id
    elif fallback_message:
        sender_first_name = fallback_message.get("sender_first_name")
        sender_last_name = fallback_message.get("sender_last_name")
        sender_username = fallback_message.get("sender_username")
        sender_display_name = fallback_message.get("sender_display_name")
        sender_id = fallback_message.get("sender_id")
    else:
        sender_first_name = None
        sender_last_name = None
        sender_username = None
        sender_display_name = build_sender_display_name(None, None, None)
        sender_id = None

    return {
        "business_connection_id": business_connection_id,
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "sender_id": sender_id,
        "sender_first_name": sender_first_name,
        "sender_last_name": sender_last_name,
        "sender_username": sender_username,
        "sender_display_name": sender_display_name,
        "chat_name": _get_chat_name(message),
        "message_type": _get_message_type(message),
        "text": message.text,
        "caption": message.caption,
        "is_deleted": 0,
        "message_date": _to_iso(message.date),
    }


def _get_chat_name(message: Message) -> str | None:
    chat = message.chat
    title = getattr(chat, "title", None)
    full_name = getattr(chat, "full_name", None)
    username = getattr(chat, "username", None)

    if title:
        return title
    if full_name:
        return full_name
    if username:
        return f"@{username}"
    return None


def _get_message_type(message: Message) -> str:
    if message.text is not None:
        return "text"
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.document:
        return "document"
    if message.voice:
        return "voice"
    if message.audio:
        return "audio"
    if message.animation:
        return "animation"
    if message.video_note:
        return "video_note"
    if message.sticker:
        return "sticker"
    return "unknown"


def _to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


async def _send_owner_notification(bot: Bot, owner_user_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id=owner_user_id, text=text)
    except Exception:
        logger.exception("Failed to send notification to owner_user_id=%s", owner_user_id)

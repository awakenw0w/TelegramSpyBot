import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def init(self) -> None:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS business_connections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        business_connection_id TEXT UNIQUE NOT NULL,
                        owner_user_id INTEGER NOT NULL,
                        is_enabled INTEGER DEFAULT 1,
                        can_reply INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        business_connection_id TEXT NOT NULL,
                        chat_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        sender_id INTEGER,
                        sender_first_name TEXT,
                        sender_last_name TEXT,
                        sender_username TEXT,
                        sender_display_name TEXT,
                        chat_name TEXT,
                        message_type TEXT,
                        text TEXT,
                        caption TEXT,
                        is_deleted INTEGER DEFAULT 0,
                        message_date TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(business_connection_id, chat_id, message_id)
                    )
                    """
                )
                await db.commit()
            logger.info("SQLite database is ready: %s", self.db_path)
        except Exception:
            logger.exception("Database initialization error")
            raise

    async def upsert_business_connection(
        self,
        business_connection_id: str,
        owner_user_id: int,
        is_enabled: bool,
        can_reply: bool,
    ) -> None:
        now = _utc_now()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO business_connections (
                        business_connection_id,
                        owner_user_id,
                        is_enabled,
                        can_reply,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(business_connection_id) DO UPDATE SET
                        owner_user_id = excluded.owner_user_id,
                        is_enabled = excluded.is_enabled,
                        can_reply = excluded.can_reply,
                        updated_at = excluded.updated_at
                    """,
                    (
                        business_connection_id,
                        owner_user_id,
                        int(is_enabled),
                        int(can_reply),
                        now,
                        now,
                    ),
                )
                await db.commit()
        except Exception:
            logger.exception(
                "Database error while saving business_connection_id=%s",
                business_connection_id,
            )
            raise

    async def get_owner_user_id(self, business_connection_id: str) -> int | None:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    """
                    SELECT owner_user_id
                    FROM business_connections
                    WHERE business_connection_id = ?
                    """,
                    (business_connection_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        return None
                    return int(row["owner_user_id"])
        except Exception:
            logger.exception(
                "Database error while reading owner for business_connection_id=%s",
                business_connection_id,
            )
            raise

    async def save_message(self, data: dict[str, Any]) -> None:
        now = _utc_now()
        created_at = data.get("created_at") or now
        updated_at = data.get("updated_at") or now

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO messages (
                        business_connection_id,
                        chat_id,
                        message_id,
                        sender_id,
                        sender_first_name,
                        sender_last_name,
                        sender_username,
                        sender_display_name,
                        chat_name,
                        message_type,
                        text,
                        caption,
                        is_deleted,
                        message_date,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(business_connection_id, chat_id, message_id)
                    DO UPDATE SET
                        sender_id = excluded.sender_id,
                        sender_first_name = excluded.sender_first_name,
                        sender_last_name = excluded.sender_last_name,
                        sender_username = excluded.sender_username,
                        sender_display_name = excluded.sender_display_name,
                        chat_name = excluded.chat_name,
                        message_type = excluded.message_type,
                        text = excluded.text,
                        caption = excluded.caption,
                        is_deleted = excluded.is_deleted,
                        message_date = excluded.message_date,
                        updated_at = excluded.updated_at
                    """,
                    (
                        data["business_connection_id"],
                        data["chat_id"],
                        data["message_id"],
                        data.get("sender_id"),
                        data.get("sender_first_name"),
                        data.get("sender_last_name"),
                        data.get("sender_username"),
                        data.get("sender_display_name"),
                        data.get("chat_name"),
                        data.get("message_type"),
                        data.get("text"),
                        data.get("caption"),
                        int(data.get("is_deleted", 0)),
                        data.get("message_date"),
                        created_at,
                        updated_at,
                    ),
                )
                await db.commit()
        except Exception:
            logger.exception(
                "Database error while saving message business_connection_id=%s chat_id=%s message_id=%s",
                data.get("business_connection_id"),
                data.get("chat_id"),
                data.get("message_id"),
            )
            raise

    async def get_message(
        self,
        business_connection_id: str,
        chat_id: int,
        message_id: int,
    ) -> dict[str, Any] | None:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    """
                    SELECT *
                    FROM messages
                    WHERE business_connection_id = ?
                      AND chat_id = ?
                      AND message_id = ?
                    """,
                    (business_connection_id, chat_id, message_id),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        return None
                    return dict(row)
        except Exception:
            logger.exception(
                "Database error while reading message business_connection_id=%s chat_id=%s message_id=%s",
                business_connection_id,
                chat_id,
                message_id,
            )
            raise

    async def mark_message_deleted(
        self,
        business_connection_id: str,
        chat_id: int,
        message_id: int,
    ) -> None:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    UPDATE messages
                    SET is_deleted = 1,
                        updated_at = ?
                    WHERE business_connection_id = ?
                      AND chat_id = ?
                      AND message_id = ?
                    """,
                    (_utc_now(), business_connection_id, chat_id, message_id),
                )
                await db.commit()
        except Exception:
            logger.exception(
                "Database error while marking deleted business_connection_id=%s chat_id=%s message_id=%s",
                business_connection_id,
                chat_id,
                message_id,
            )
            raise


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

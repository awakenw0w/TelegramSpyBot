NO_TEXT = "[нет текста]"


def _clean(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_username(username: object | None) -> str:
    return _clean(username).lstrip("@")


def safe_cut_text(value: object | None, limit: int = 1800) -> str:
    text = _clean(value)
    if not text:
        return NO_TEXT
    if limit < 4:
        limit = 4
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def build_sender_display_name(
    first_name: object | None,
    last_name: object | None,
    username: object | None,
) -> str:
    first = _clean(first_name)
    last = _clean(last_name)
    clean_username = _clean_username(username)

    if first and last:
        return f"{first} {last}"
    if first:
        return first
    if clean_username:
        return f"@{clean_username}"
    return "Пользователь"


def build_sender_label(
    sender_display_name: object | None = None,
    sender_username: object | None = None,
) -> str:
    name = _clean(sender_display_name)
    username = _clean_username(sender_username)

    if name == "Пользователь":
        name = ""

    if username and name == f"@{username}":
        return f"@{username}"
    if name and username:
        return f"{name} (@{username})"
    if name:
        return name
    if username:
        return f"@{username}"
    return "Пользователь"


def get_message_text_or_caption(
    text: object | None,
    caption: object | None,
    limit: int = 1800,
) -> str:
    if _clean(text):
        return safe_cut_text(text, limit=limit)
    if _clean(caption):
        return safe_cut_text(caption, limit=limit)
    return NO_TEXT


def format_edit_notification(
    sender_label: object | None,
    old_text_or_caption: object | None,
    new_text_or_caption: object | None,
    bot_username: str,
) -> str:
    old_text = safe_cut_text(old_text_or_caption, limit=1600)
    new_text = safe_cut_text(new_text_or_caption, limit=1600)
    username = _clean_username(bot_username)
    return (
        f"{build_sender_label(sender_label)} изменил(а) сообщение:\n"
        "Старое сообщение:\n"
        f"{old_text}\n\n"
        "Новое сообщение:\n"
        f"{new_text}\n\n"
        f"@{username}"
    )


def format_delete_notification(
    sender_label: object | None,
    text_or_caption: object | None,
    bot_username: str,
) -> str:
    text = safe_cut_text(text_or_caption, limit=3500)
    username = _clean_username(bot_username)
    return (
        f"{build_sender_label(sender_label)} удалил(а) сообщение:\n"
        f"{text}\n\n"
        f"@{username}"
    )

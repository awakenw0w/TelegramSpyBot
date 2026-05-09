# Minimal Telegram Business Bot API tracker

Минимальный бот на Python, который работает только через официальный Telegram Bot API и функцию Telegram «Автоматизация чатов».

Бот сохраняет входящие `business_message` в SQLite, а затем уведомляет владельца, если сообщение было изменено через `edited_business_message` или удалено через `deleted_business_messages`.

## Что входит

- Python 3.12+
- aiogram 3.x
- SQLite + aiosqlite
- python-dotenv
- logging
- команда `/start`
- стартовый экран с двумя inline-кнопками
- сохранение текстов и captions входящих business-сообщений
- уведомления об изменённых и удалённых сообщениях
- попытка сохранить фото/видео из ответа на медиа с таймером и отправить его владельцу

## Что не входит

Бот не скачивает обычные медиа автоматически, не имеет архива, настроек, статуса, помощи, статистики, админ-панели, веб-панели, оплаты, аналитики, Telethon, Pyrogram и userbot.

Для фото/видео с таймером бот использует только официальный Bot API: если владелец отвечает текстом на такое медиа, бот смотрит на `reply_to_message`, пытается скачать доступный `file_id` в `storage/timer_media` и отправить файл владельцу в личку. Telegram Bot API не отдаёт отдельный флаг «медиа с таймером», поэтому если Telegram не отдаст файл в ответе, бот просто запишет ошибку в лог.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

Создайте `.env` по примеру `.env.example`:

```env
BOT_TOKEN=123456:token
BOT_USERNAME=YourBotUsername
DB_PATH=storage/bot.sqlite3
CONNECT_BANNER_PATH=assets/connect_banner.png
LOG_LEVEL=INFO
```

`BOT_USERNAME` — username самого бота без `@`.

Кнопка «🟢 Подключить» открывает настройки Telegram через `tg://settings`, чтобы каждый пользователь подключал бота в своём аккаунте.

Если хотите картинку на стартовом экране, положите файл сюда:

```text
assets/connect_banner.png
```

Если файла нет, бот просто отправит текст и не упадёт.

## Запуск

```bash
python -m app.main
```

При запуске бот создаёт папки `storage` и `assets`, SQLite-базу и таблицы, если их ещё нет, после чего запускает polling.

## Подключение через «Автоматизация чатов»

1. Откройте бота и нажмите `/start`.
2. Нажмите кнопку «🟢 Подключить».
3. В открывшихся настройках нажмите «Редактировать профиль».
4. Откройте «Автоматизация чатов».
5. Добавьте бота по username: `@BOT_USERNAME`.

После подключения бот получает `business_connection`, сохраняет подключение и начинает обрабатывать `business_message`, `edited_business_message` и `deleted_business_messages`.

## Структура

```text
app/
  __init__.py
  main.py
  config.py
  database.py
  keyboards.py
  handlers_start.py
  handlers_business.py
  formatters.py
storage/
assets/
.env.example
requirements.txt
README.md
```

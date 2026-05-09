# ChatFlow — бот для уведомлений об изменённых и удалённых сообщениях

ChatFlow помогает следить за важными изменениями в Telegram-переписке через официальную функцию Telegram «Автоматизация чатов».

После подключения бот сохраняет входящие сообщения в SQLite. Если собеседник изменит или удалит сообщение, ChatFlow отправит владельцу уведомление с сохранённым текстом.

Готовая версия уже работает на сервере, её можно открыть и протестировать в Telegram: [@mychatflowbot](https://t.me/mychatflowbot).

## Возможности

- сохраняет текст входящих `business_message`;
- сохраняет подписи к сообщениям, если текста нет;
- уведомляет об изменённых сообщениях через `edited_business_message`;
- уведомляет об удалённых сообщениях через `deleted_business_messages`;
- показывает имя и username отправителя из сохранённого сообщения;
- работает на официальном Telegram Bot API;
- запускается одной командой: `python -m app.main`.

## Технологии

- Python 3.12+
- aiogram 3.x
- SQLite
- aiosqlite
- python-dotenv
- logging

## Подготовка

Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env` и заполните переменные:

```env
BOT_TOKEN=123456:token
BOT_USERNAME=YourBotUsername
DB_PATH=storage/bot.sqlite3
CONNECT_BANNER_PATH=assets/connect_banner.png
LOG_LEVEL=INFO
```

`BOT_TOKEN` — токен бота от BotFather.

`BOT_USERNAME` — username бота без `@`.

`DB_PATH` — путь к SQLite-базе.

`CONNECT_BANNER_PATH` — путь к картинке для стартового экрана. Если файла нет, бот просто отправит текст.

## Запуск

```bash
python -m app.main
```

При запуске ChatFlow создаёт папки `storage` и `assets`, подготавливает SQLite-базу и запускает polling.

## Подключение в Telegram

1. Откройте бота в Telegram.
2. Отправьте `/start`.
3. Нажмите кнопку «🟢 Подключить».
4. В настройках профиля откройте «Автоматизация чатов».
5. Добавьте бота по username из `.env`.

После подключения бот начнёт получать события `business_message`, `edited_business_message` и `deleted_business_messages`.

## Что важно знать

ChatFlow не использует Telethon, Pyrogram и userbot. В проекте нет веб-панели, оплаты, аналитики и админ-панели.

Секреты и локальные файлы не должны попадать в GitHub. Файл `.env`, SQLite-база, виртуальное окружение, логи и `__pycache__` добавлены в `.gitignore`.

## Структура проекта

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
assets/
storage/
.env.example
.gitignore
requirements.txt
README.md
```

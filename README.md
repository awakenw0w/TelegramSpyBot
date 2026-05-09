# ChatFlow — бот для уведомлений об изменённых и удалённых сообщениях.

Актуальная версия бота — https://t.me/mychatflowbot

ChatFlow помогает не потерять важные сообщения в Telegram. Если собеседник изменит или удалит сообщение, бот пришлёт уведомление и покажет сохранённый текст.

Бот работает через функцию Telegram «Автоматизация чатов». После подключения он сохраняет входящие сообщения в локальную SQLite-базу и использует эти записи для уведомлений.

Готовая версия уже работает на сервере. Её можно открыть и протестировать в Telegram: [@mychatflowbot](https://t.me/mychatflowbot).

## Возможности

- присылает уведомление, когда сообщение изменили;
- присылает уведомление, когда сообщение удалили;
- показывает имя и username отправителя.

## Что внутри

- Python 3.12+
- aiogram 3.x
- SQLite
- aiosqlite
- python-dotenv
- logging

## Установка

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его и установите зависимости.

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

Скопируйте `.env.example` в `.env` и заполните данные бота:

```env
BOT_TOKEN=123456:token
BOT_USERNAME=YourBotUsername
DB_PATH=storage/bot.sqlite3
LOG_LEVEL=INFO
```

`BOT_TOKEN` — токен от BotFather.

`BOT_USERNAME` — username вашего бота без `@`.

`DB_PATH` — файл, где бот будет хранить сообщения.

## Запуск

```bash
python -m app.main
```

После запуска бот сам создаст папку `storage`, подготовит базу данных и начнёт принимать события от Telegram.

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
storage/
.env.example
.gitignore
requirements.txt
README.md
```

""" 
Simple Bot to reply to Telegram messages. 
First, a few handler functions are defined. Then, those functions are passed to 
the Application and registered at their respective places. 
Then, the bot is started and runs until we press Ctrl-C on the command line. 
Usage: 
Basic Echobot example, repeats messages. 
Press Ctrl-C on the command line or send a signal to the process to stop the 
bot. 
"""

import json
import requests
import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from cmp.crypto_utils import decrypt_string, hash_string

# Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = 4025
URL = os.getenv("ADDR") or "localhost"
url = f"http://{URL}:{PORT}"

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def load_users():
    with open("users.json", "r", encoding="utf-8") as file:
        return json.load(file)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при использовании команды /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрашивает у пользователя ввод пароля."""
    await update.message.reply_text(
        "Пожалуйста, введите ваш пароль следующим сообщением."
    )


async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает введенный пользователем пароль."""
    password = update.message.text

    # Отправка POST запроса на сервер для проверки пароля
    try:
        validation_response = url + "/login"
        response = requests.post(validation_response, json={"password": password})
        if response.status_code == 200:
            logger.info("Success:", response.text)
            await update.message.reply_text(
                f"Здравствуйте, Ваши данные: \n{response.text}"
            )
        else:
            logger.warning("Failed:", response.status_code)
            await update.message.reply_text(
                f"Неверный пароль. Пожалуйста, попробуйте еще раз."
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        await update.message.reply_text(
            f"Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз. Ошибка: {e}"
        )


def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("authorize", authorize))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

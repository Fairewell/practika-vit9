import os
import logging
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(os.getcwd()), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = 4025
URL = os.getenv("ADDR") or "localhost"
SERVER_URL = f"http://{URL}:{PORT}/login"

# Включение логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AUTH_PASSWORD, WORK_START, WORK_END, LUNCH_START, LUNCH_END, VIEW_TIMES = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Добро пожаловать! Для начала авторизуйтесь. Введите ваш пароль:"
    )
    return AUTH_PASSWORD


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Получен пароль от пользователя {user_id}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(SERVER_URL, json={"password": password}) as resp:
                status = resp.status
                text = await resp.json()

        if status == 200:
            logger.info(f"Успех для пользователя {user_id}: {text}")

            # Получаем данные о времени
            working_hours = text["working_hours"]
            context.user_data.update(
                {
                    "user_id": text["_id"],
                    "working_hours": working_hours,
                    "start_time": datetime.now(),
                }
            )

            # Кнопки для регистрации времени
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Я пришел на работу", callback_data="work_start"
                    ),
                    InlineKeyboardButton("Я ушел с работы", callback_data="work_end"),
                ],
                [
                    InlineKeyboardButton("Начало обеда", callback_data="lunch_start"),
                    InlineKeyboardButton("Конец обеда", callback_data="lunch_end"),
                ],
                [InlineKeyboardButton("Посмотреть время", callback_data="view_times")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Здравствуйте! Ваши данные:\n\n"
                f"ID: {text['_id']}\n"
                f"Объект: {text['object']}\n"
                f"Команда: {text['team']}\n"
                f"Супервизор: {text['supervisor']}\n"
                f"Часы работы:\n"
                f"  Начало: {working_hours['monday']['start']}\n"
                f"  Конец: {working_hours['monday']['end']}\n"
                f"  Обед: {working_hours['monday']['lunch']['start']} - {working_hours['monday']['lunch']['end']}\n",
                reply_markup=reply_markup,
            )
            return WORK_START
        else:
            logger.warning(f"Неудача для пользователя {user_id}: {status} - {text}")
            await update.message.reply_text(
                "Неверный пароль. Пожалуйста, попробуйте еще раз."
            )
            return AUTH_PASSWORD
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса для пользователя {user_id}: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END


async def register_work_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data.get("user_id")
    start_time = datetime.now()
    context.user_data["work_start_time"] = start_time

    logger.info(
        f"Пользователь {user_id} пришел на работу в {start_time.strftime('%H:%M')}"
    )
    await update.callback_query.answer()

    # Добавляем инлайн-кнопки для проверки времени
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть время", callback_data="view_times"),
            InlineKeyboardButton("Зарегистрировать выход", callback_data="work_end"),
        ],
        [
            InlineKeyboardButton("Начало обеда", callback_data="lunch_start"),
            InlineKeyboardButton("Конец обеда", callback_data="lunch_end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        f"Вы зарегистрировали вход на работу в {start_time.strftime('%H:%M')}.\n",
        reply_markup=reply_markup,
    )
    return WORK_START


async def register_work_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("user_id")
    end_time = datetime.now()
    context.user_data["work_end_time"] = end_time

    logger.info(f"Пользователь {user_id} ушел с работы в {end_time.strftime('%H:%M')}")
    await update.callback_query.answer()

    # Добавляем инлайн-кнопки для проверки времени
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть время", callback_data="view_times"),
            InlineKeyboardButton("Я пришел на работу", callback_data="work_start"),
        ],
        [
            InlineKeyboardButton("Начало обеда", callback_data="lunch_start"),
            InlineKeyboardButton("Конец обеда", callback_data="lunch_end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        f"Вы зарегистрировали выход с работы в {end_time.strftime('%H:%M')}.\n",
        reply_markup=reply_markup,
    )
    return WORK_START


async def register_lunch_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data.get("user_id")
    lunch_start = datetime.now()
    context.user_data["lunch_start_time"] = lunch_start

    logger.info(f"Пользователь {user_id} начал обед в {lunch_start.strftime('%H:%M')}")
    await update.callback_query.answer()

    # Добавляем инлайн-кнопки для проверки времени
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть время", callback_data="view_times"),
            InlineKeyboardButton("Завершить обед", callback_data="lunch_end"),
        ],
        [
            InlineKeyboardButton("Я пришел на работу", callback_data="work_start"),
            InlineKeyboardButton("Я ушел с работы", callback_data="work_end"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        f"Вы начали обед в {lunch_start.strftime('%H:%M')}.\n",
        reply_markup=reply_markup,
    )
    return WORK_START


async def register_lunch_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("user_id")
    lunch_end = datetime.now()
    context.user_data["lunch_end_time"] = lunch_end

    logger.info(f"Пользователь {user_id} закончил обед в {lunch_end.strftime('%H:%M')}")
    await update.callback_query.answer()

    # Добавляем инлайн-кнопки для проверки времени
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть время", callback_data="view_times"),
            InlineKeyboardButton("Я пришел на работу", callback_data="work_start"),
        ],
        [InlineKeyboardButton("Я ушел с работы", callback_data="work_end")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        f"Вы закончили обед в {lunch_end.strftime('%H:%M')}.\n",
        reply_markup=reply_markup,
    )
    return WORK_START


async def view_times(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("user_id")
    work_start_time = context.user_data.get("work_start_time", "Не зарегистрировано")
    work_end_time = context.user_data.get("work_end_time", "Не зарегистрировано")
    lunch_start_time = context.user_data.get("lunch_start_time", "Не зарегистрировано")
    lunch_end_time = context.user_data.get("lunch_end_time", "Не зарегистрировано")

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Ваши зарегистрированные времена:\n"
        f"Вход на работу: {work_start_time.strftime('%H:%M') if isinstance(work_start_time, datetime) else work_start_time}\n"
        f"Выход с работы: {work_end_time.strftime('%H:%M') if isinstance(work_end_time, datetime) else work_end_time}\n"
        f"Начало обеда: {lunch_start_time.strftime('%H:%M') if isinstance(lunch_start_time, datetime) else lunch_start_time}\n"
        f"Конец обеда: {lunch_end_time.strftime('%H:%M') if isinstance(lunch_end_time, datetime) else lunch_end_time}\n"
    )
    return WORK_START


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, authorize)],
            WORK_START: [
                CallbackQueryHandler(register_work_start, pattern="work_start"),
                CallbackQueryHandler(register_work_end, pattern="work_end"),
                CallbackQueryHandler(register_lunch_start, pattern="lunch_start"),
                CallbackQueryHandler(register_lunch_end, pattern="lunch_end"),
                CallbackQueryHandler(view_times, pattern="view_times"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

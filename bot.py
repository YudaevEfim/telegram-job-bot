import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

saved_jobs = []
search_state = {}


def get_saved_jobs_text():
    if not saved_jobs:
        return "Список вакансий пока пуст."

    response = "Сохранённые вакансии:\n\n"
    for i, job in enumerate(saved_jobs, start=1):
        response += f"{i}. {job}\n"
    return response


def get_search_results_text(keyword, distance_km):
    return (
        "Поисковый запрос готов.\n\n"
        f"Что искать: {keyword}\n"
        f"Расстояние от קצרין: до {distance_km} км\n\n"
        "Ищи по этим вариантам:\n\n"
        f"AllJobs: {keyword} קצרין\n"
        f"דרושים: {keyword} קצרין\n"
        f"JobMaster: {keyword} קצרין\n"
        f"Facebook: {keyword} קצרין\n\n"
        "Это пока диалоговая версия поиска.\n"
        "Следующим шагом можно сделать, чтобы бот сам находил вакансии и фильтровал их по расстоянию."
    )


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет, Ефим. Я твой бот для поиска работы.\n\n"
        "Можно писать так:\n"
        "вакансии\n"
        "список\n"
        "добавить https://example.com/job\n"
        "найди\n\n"
        "Также работают команды:\n"
        "/jobs\n"
        "/list\n"
        "/add https://example.com/job"
    )


@bot.message_handler(commands=['jobs'])
def jobs_command(message):
    bot.send_message(message.chat.id, "Пока вакансий нет. Скоро начну искать.")


@bot.message_handler(commands=['list'])
def list_command(message):
    bot.send_message(message.chat.id, get_saved_jobs_text())


@bot.message_handler(commands=['add'])
def add_command(message):
    text = message.text.strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Пришли команду так:\n/add https://example.com/job"
        )
        return

    link = parts[1].strip()
    saved_jobs.append(link)

    bot.send_message(
        message.chat.id,
        f"Вакансия сохранена:\n{link}"
    )


@bot.message_handler(func=lambda message: message.text is not None)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    lower_text = text.lower()

    if lower_text == "вакансии":
        bot.send_message(chat_id, "Пока вакансий нет. Скоро начну искать.")
        return

    if lower_text == "список":
        bot.send_message(chat_id, get_saved_jobs_text())
        return

    if lower_text.startswith("добавить "):
        link = text[9:].strip()

        if not link:
            bot.send_message(
                chat_id,
                "Пришли так:\nдобавить https://example.com/job"
            )
            return

        saved_jobs.append(link)
        bot.send_message(
            chat_id,
            f"Вакансия сохранена:\n{link}"
        )
        return

    if lower_text == "найди":
        search_state[chat_id] = {"step": "keyword"}
        bot.send_message(
            chat_id,
            "Какие вакансии искать?\n\n"
            "Например:\n"
            "אחראי משמרת\n"
            "ביטחון\n"
            "מוקד\n"
            "מנהל"
        )
        return

    if chat_id in search_state:
        current_step = search_state[chat_id].get("step")

        if current_step == "keyword":
            search_state[chat_id]["keyword"] = text
            search_state[chat_id]["step"] = "distance"

            bot.send_message(
                chat_id,
                "Какое расстояние от קצרין искать?\n\n"
                "Напиши только число в километрах.\n"
                "Например: 30, 50, 70"
            )
            return

        if current_step == "distance":
            if not text.isdigit():
                bot.send_message(
                    chat_id,
                    "Напиши только число.\n"
                    "Например: 30 или 50"
                )
                return

            distance_km = int(text)

            if distance_km <= 0:
                bot.send_message(
                    chat_id,
                    "Расстояние должно быть больше 0."
                )
                return

            keyword = search_state[chat_id]["keyword"]
            result_text = get_search_results_text(keyword, distance_km)

            del search_state[chat_id]
            bot.send_message(chat_id, result_text)
            return


bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

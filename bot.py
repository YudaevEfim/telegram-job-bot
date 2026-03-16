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

def get_search_results_text(keyword, radius_choice):
    radius_text = ""
    if radius_choice == "1":
        radius_text = "קצרין + 50 ק\"מ"
    elif radius_choice == "2":
        radius_text = "קצרין + до 1 часа езды"
    else:
        radius_text = "краткий поиск от קצרין"

    return (
        "Поисковый запрос готов.\n\n"
        f"Что искать: {keyword}\n"
        f"Радиус: {radius_text}\n\n"
        "Ищи по этим вариантам:\n\n"
        f"AllJobs: {keyword} קצרין\n"
        f"דרושים: {keyword} קצרין\n"
        f"JobMaster: {keyword} קצרין\n"
        f"Facebook: {keyword} קצרין\n\n"
        "Это первая версия поиска. "
        "Следующим шагом можно сделать, чтобы бот сам находил и присылал вакансии."
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
        "поиск\n\n"
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

    if lower_text == "поиск":
        search_state[chat_id] = {"step": "keyword"}
        bot.send_message(
            chat_id,
            "Что искать?\n\n"
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
            search_state[chat_id]["step"] = "radius"

            bot.send_message(
                chat_id,
                "Выбери радиус поиска:\n"
                "1 - קצרין + 50 ק\"מ\n"
                "2 - קצרין + до 1 часа езды\n\n"
                "Пришли просто цифру: 1 или 2"
            )
            return

        if current_step == "radius":
            if text not in ["1", "2"]:
                bot.send_message(
                    chat_id,
                    "Пришли только:\n"
                    "1 - קצרין + 50 ק\"מ\n"
                    "или\n"
                    "2 - קצרין + до 1 часа езды"
                )
                return

            keyword = search_state[chat_id]["keyword"]
            result_text = get_search_results_text(keyword, text)

            del search_state[chat_id]
            bot.send_message(chat_id, result_text)
            return

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

saved_jobs = []

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет, Ефим. Я твой бот для поиска работы.\n\n"
        "Команды:\n"
        "/jobs - статус\n"
        "/add <ссылка> - добавить вакансию\n"
        "/list - показать сохранённые вакансии"
    )

@bot.message_handler(commands=['jobs'])
def jobs(message):
    bot.send_message(message.chat.id, "Пока вакансий нет. Скоро начну искать.")

@bot.message_handler(commands=['add'])
def add_job(message):
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

@bot.message_handler(commands=['list'])
def list_jobs(message):
    if not saved_jobs:
        bot.send_message(message.chat.id, "Список вакансий пока пуст.")
        return

    response = "Сохранённые вакансии:\n\n"
    for i, job in enumerate(saved_jobs, start=1):
        response += f"{i}. {job}\n"

    bot.send_message(message.chat.id, response)

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

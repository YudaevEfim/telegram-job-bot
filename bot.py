import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, Ефим. Я твой бот для поиска работы.")

@bot.message_handler(commands=['jobs'])
def jobs(message):
    bot.send_message(message.chat.id, "Пока вакансий нет. Скоро начну искать.")

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

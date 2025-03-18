import telebot

BOT_TOKEN = '7811445071:AAH0uxDst4U_COQ4GSGk81UjV3JKQM7Imn4'

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я простой Telegram-бот.")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# Запуск бота
bot.infinity_polling()
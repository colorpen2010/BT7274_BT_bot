import telebot
import os
import random
import string
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    print('Token not found!')
    exit()

bot = telebot.TeleBot(TOKEN)

magic_answers = [
    "Да", "Нет", "Скорее да", "Скорее нет",
    "Возможно", "Спроси позже",
    "Определённо да", "Определённо нет"
]


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message,
        'Привет! 🖐\n'
        'Я BT-7274:\n'
        '❓ Впиши вопрос со знаком "?" — и я дам ответ\n'
        '🔐 введи число от 4 до 64 — и я сгенерирую пароль\n'
        '📢 Впиши что угодно — и я это повторю! (только не ставь знак вопрос в конце)\n'
        '😀 Введи /info — и я поприветствую тебя и отправлю твои данные мне в личку\n'
        '(не волнуйся, все твои данные будут в безопасности и пойдут в сервер Ополчения Фронтира)\n'
        'pts. если вы не поняли я и последняя фраза это отсылка к игре Titanfall 2'
    )


@bot.message_handler(func=lambda m: '?' in m.text)
def magic_ball(message):
    bot.reply_to(message, random.choice(magic_answers))


@bot.message_handler(func=lambda m: m.text.isdigit())
def password(message):
    length = int(message.text)

    if 4 <= length <= 64:
        symbols = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(random.choice(symbols) for _ in range(length))
        bot.reply_to(message, f"🔐 Пароль:\n{pwd}")
    else:
        bot.reply_to(message, "Число должно быть от 4 до 64")


@bot.message_handler(commands=['info'])
def info(message):
    u = message.from_user
    bot.send_message(message.chat.id, f'Привет, {u.first_name}')
    bot.send_message(374467027, f'{u.id} {u.first_name} {u.last_name} {u.username}')


@bot.message_handler(func=lambda m: m.text.startswith('hello'))
def hello(message):
    bot.reply_to(message, 'Привет!')


@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, message.text)


print('Bot is running...')
bot.infinity_polling()
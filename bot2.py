import telebot
import os
import re
from dotenv import load_dotenv
from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from telebot.states import State, StatesGroup

load_dotenv()

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    print('Token not found!')
    exit()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

bot.add_custom_filter(custom_filter=custom_filters.StateFilter(bot))

class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_phone = State()

reg_kb = types.ReplyKeyboardMarkup()
reg_btn = types.KeyboardButton('Регистрация ✔')
reg_kb.add(reg_btn)

cancel_kb = types.InlineKeyboardMarkup()
cancel_btn = types.InlineKeyboardButton('Отмена', callback_data='cancel')
cancel_kb.add(cancel_btn)

remove_kb = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Привет! Нажми "Регистрация" чтобы получать спам на почту!',
        reply_markup=reg_kb
    )

@bot.message_handler(func=lambda message: message.text.startswith('Регистрация'))
def start_registration(message):
    temp_msg = bot.send_message(
        message.chat.id,
        '⌛ Обновляем интерфейс...',
        reply_markup=remove_kb
    )

    bot.delete_message(message.chat.id, temp_msg.id)

    bot.set_state(
        message.from_user.id,
        RegistrationStates.waiting_for_email,
        message.chat.id)

    bot.send_message(
        message.chat.id,
        'Отлично! теперь отправь мне свою почту чтобы получать спам!',
        reply_markup=cancel_kb
    )

@bot.message_handler(state=RegistrationStates.waiting_for_email)
def process_email(message):
    email = message.text
    email_pattern = r"^[\w\.-_]+@[\w\.-_]+\.\w+$"

    if re.match(email_pattern, email):
        bot.set_state(
            message.from_user.id,
            RegistrationStates.waiting_for_phone,
            message.chat.id
        )

        # сохраняем почту временно
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['email'] = email

        bot.send_message(
            message.chat.id,
            'Теперь отправь номер телефона 📱\nПример: +380XXXXXXXXX'
        )
    else:
        bot.send_message(
            message.chat.id,
            'Не похоже на электронную почту. Попробуй ещё раз'
        )

@bot.message_handler(state=RegistrationStates.waiting_for_phone)
def process_phone(message):
    raw_phone = message.text

    phone = re.sub(r"[ \-\(\)]", "", raw_phone)

    if not re.match(r"^\+?\d+$", phone):
        bot.send_message(
            message.chat.id,
            "Номер должен содержать только цифры (и + в начале)"
        )
        return

    if not (10 <= len(phone) <= 15):
        bot.send_message(
            message.chat.id,
            "Номер должен быть от 10 до 15 цифр"
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        email = data.get('email')

    with open('users.txt', 'a') as f:
            f.write(f'email: {email} | phone_number: {phone}\n')

    # (необязательно, но полезно)
    print(f'New user -> email: {email}, phone_number: {phone}')

    bot.delete_state(message.from_user.id, message.chat.id)

    bot.send_message(
        message.chat.id,
        'Спасибо! Регистрация завершена ✅',
        reply_markup=reg_kb
    )

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_handler(call):
    bot.delete_state(call.from_user.id, call.message.chat.id)
    bot.send_message(
        call.message.chat.id,
        'Если передумаете - нажмите "Регистрация" снова.',
        reply_markup=reg_kb
    )
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    print('Bot is running...')
    bot.infinity_polling()
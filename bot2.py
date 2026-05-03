import telebot
import os
import random
from dotenv import load_dotenv
from telebot import types

load_dotenv()

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    print('Token not found!')
    exit()

bot = telebot.TeleBot(TOKEN)

games = {}

# https://www.tiktok.com/@batya_razrulit/video/7281903798979759392
WIN_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет 👋\n\n"
        "Чтобы начать игру в крестики-нолики, напиши:\n"
        "/tictactoe 🎮"
    )
@bot.message_handler(commands=['tictactoe'])
def start_game(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("Играть за ❌", callback_data="start_X"),
        types.InlineKeyboardButton("Играть за ⭕", callback_data="start_O")
    )
    bot.send_message(message.chat.id, "Выбери сторону:", reply_markup=kb)


def board_markup(chat_id):
    board = games[chat_id]["board"]
    kb = types.InlineKeyboardMarkup(row_width=3)

    buttons = []
    for i in range(9):
        text = board[i] if board[i] != " " else "⬜"
        buttons.append(types.InlineKeyboardButton(text, callback_data=f"move_{i}"))

    kb.add(*buttons)
    return kb


def check_win(board, symbol):
    return any(all(board[i] == symbol for i in combo) for combo in WIN_COMBOS)


def is_draw(board):
    return " " not in board


@bot.callback_query_handler(func=lambda call: call.data.startswith("start_"))
def choose_side(call):
    symbol = call.data.split("_")[1]

    games[call.message.chat.id] = {
        "player": symbol,
        "bot": "O" if symbol == "X" else "X",
        "board": [" "] * 9,
        "active": True
    }

    bot.edit_message_text(
        "Игра началась!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=board_markup(call.message.chat.id)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("move_"))
def move(call):
    chat_id = call.message.chat.id

    if chat_id not in games:
        return

    game = games[chat_id]

    if not game["active"]:
        return

    idx = int(call.data.split("_")[1])
    board = game["board"]

    if board[idx] != " ":
        return

    board[idx] = game["player"]

    if check_win(board, game["player"]):
        game["active"] = False
        bot.edit_message_text(
            "🎉 Ты выиграл!",
            chat_id,
            call.message.message_id
        )
        return

    if is_draw(board):
        game["active"] = False
        bot.edit_message_text(
            "🤝 Ничья!",
            chat_id,
            call.message.message_id
        )
        return

    empty = [i for i, v in enumerate(board) if v == " "]
    bot_move = random.choice(empty)
    board[bot_move] = game["bot"]

    if check_win(board, game["bot"]):
        game["active"] = False
        bot.edit_message_text(
            "💀 Ты проиграл!",
            chat_id,
            call.message.message_id
        )
        return

    if is_draw(board):
        game["active"] = False
        bot.edit_message_text(
            "🤝 Ничья!",
            chat_id,
            call.message.message_id
        )
        return

    bot.edit_message_reply_markup(
        chat_id,
        call.message.message_id,
        reply_markup=board_markup(chat_id)
    )


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
import telebot
import json
from telebot import types
import environ

env = environ.Env()
environ.Env.read_env()
DEBUG = env('DEBUG')
TOKEN = env('SECRET_KEY')
bot = telebot.TeleBot(TOKEN)
file = {}
with open('questions.json', 'r', encoding='utf-8') as f:
    file = json.load(f)

ChatProgress = {}

def send_question_and_answers(flag):
    question = file[str(flag)]['question']
    keyboard = types.InlineKeyboardMarkup()
    for i in file[str(flag)]['answers']:
        if i[-1] == '*':
            keyboard.add(types.InlineKeyboardButton(text=str(i[:-1]), callback_data=f'True{flag}'))
        else: keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f'False{flag}'))
    return question, keyboard

def poll(chat_id, flag=1, grade=None):
    try:
        if grade == None:
            ChatProgress[chat_id] = 0
        if grade == True:
            ChatProgress[chat_id] = ChatProgress[chat_id] + 1
        question, keyboard = send_question_and_answers(flag)
        send = bot.send_message(chat_id, question, reply_markup=keyboard)
        bot.register_next_step_handler(send, process_question_step)
    except:
        send = bot.send_message(chat_id, f'Ты успешно завершил тест, твой результат {ChatProgress[chat_id]} поинт(а)!')
        ChatProgress.pop(chat_id)

@bot.message_handler(commands=['start'])
def start(message):
    poll(message.chat.id)

def process_question_step(message):
    if not message.text.startswith('/'):
        bot.send_message(message.chat.id, 'Варианты ответов принимаются только по кнопкам!')

@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    if call.data[:-1] == "True":
        bot.send_sticker(call.message.chat.id, "CAACAgIAAxkBAAEElrJia7mqOml2b5qFxvp4eiQcgf0-3AAC1EcAAuCjggcPdAZjWLI55iQE")
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.message_id, reply_markup='')
        poll(call.message.chat.id, int(call.data[-1]) + 1, True)

    if call.data[:-1] == "False":
        bot.send_sticker(call.message.chat.id, "CAACAgIAAxkBAAEElrRia7m5zjtAdPT3ll4GhGrx6LYD8wAC1UcAAuCjggcLaPnsUjIgAyQE")
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.message_id, reply_markup='')
        poll(call.message.chat.id, int(call.data[-1]) + 1, False)

bot.polling()

import telebot
from telebot import types
import sqlite3

# Bot Token (8346685112:AAEJcFNG6PcWTKYGTSm8mYPeQ2LTch4rYHc)
API_TOKEN = '8346685112:AAEJcFNG6PcWTKYGTSm8mYPeQ2LTch4rYHc'
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস ফাংশন
def init_db():
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance REAL)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?)", (user_id, 0.0))
        conn.commit()
    conn.close()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('👤 Profile', '💰 Balance', '💳 Withdraw', '🤝 Invite')
    bot.send_message(user_id, "Quick Cash বটে আপনাকে স্বাগতম!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if message.text == '💰 Balance':
        bot.reply_to(message, "আপনার ব্যালেন্স: ০.০০ টাকা")
    # এভাবে অন্য বাটনগুলোও সাজানো যাবে


bot.infinity_polling()

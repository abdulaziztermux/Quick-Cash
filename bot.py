import telebot
from telebot import types
import sqlite3

# আপনার নতুন এবং সক্রিয় টোকেন
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
bot = telebot.TeleBot('8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8')

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, 
                       balance REAL DEFAULT 0.0, 
                       refer_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # ডাটাবেসে ইউজার চেক
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "Quick Cash বটে স্বাগতম! আপনার প্রোফাইল চেক করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👤 Profile')
def show_profile(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "নেই"
    
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, ref_count = data if data else (0.0, 0)
    conn.close()

    profile_text = (f"👤 **ইউজার প্রোফাইল**\n\n"
                    f"📛 নাম: {user_name}\n"
                    f"🆔 UID: `{user_id}`\n"
                    f"📧 ইউজারনেম: {username}\n"
                    f"💰 ব্যালেন্স: {balance} টাকা\n"
                    f"👥 মোট রেফার: {ref_count} জন")

    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            bot.send_photo(user_id, photos.photos[0][0].file_id, caption=profile_text, parse_mode="Markdown")
        else:
            bot.send_message(user_id, profile_text, parse_mode="Markdown")
    except:
        bot.send_message(user_id, profile_text, parse_mode="Markdown")

bot.infinity_polling()


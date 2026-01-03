import telebot
from telebot import types
import sqlite3

# আপনার বর্তমান নিরাপদ টোকেনটি এখানে বসান
API_TOKEN = '8346685112:AAHWLw7SdyrfPGezYPN2Am6_uHmjqFnqAwk'
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, 
                       balance REAL DEFAULT 0.0, 
                       refer_count INTEGER DEFAULT 0,
                       referred_by INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    command_args = message.text.split()
    
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        referred_by = int(command_args[1]) if len(command_args) > 1 and command_args[1].isdigit() else None
        if referred_by and referred_by != user_id:
            cursor.execute("UPDATE users SET balance = balance + 50, refer_count = refer_count + 1 WHERE user_id = ?", (referred_by,))
            try:
                bot.send_message(referred_by, "🎉 নতুন রেফারেল! আপনি ৫০ টাকা বোনাস পেয়েছেন।")
            except: pass
        cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referred_by))
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "Quick Cash বটে স্বাগতম!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, ref_count = data if data else (0, 0)
    conn.close()

    if message.text == '👤 Profile':
        user_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "নেই"
        
        profile_msg = (f"👤 **ইউজার প্রোফাইল**\n\n"
                       f"📛 নাম: {user_name}\n"
                       f"🆔 UID: `{user_id}`\n"
                       f"📧 ইউজারনেম: {username}\n"
                       f"💰 ব্যালেন্স: {balance} টাকা\n"
                       f"👥 মোট রেফার: {ref_count} জন")

        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                bot.send_photo(user_id, photos.photos[0][0].file_id, caption=profile_msg, parse_mode="Markdown")
            else:
                bot.send_message(user_id, profile_msg, parse_mode="Markdown")
        except:
            bot.send_message(user_id, profile_msg, parse_mode="Markdown")

    elif message.text == '📺 Watch Ads':
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(user_id, "✅ বিজ্ঞাপন দেখা সফল! ১০ টাকা যোগ করা হয়েছে।")

    elif message.text == '🤝 Refer & Earn':
        bot_info = bot.get_me()
        refer_link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(user_id, f"🤝 **আপনার রেফারেল লিংক:**\n{refer_link}\n\n✅ প্রতি রেফারে ৫০ টাকা!")

    elif message.text == '💳 Withdraw':
        if balance < 2000 or ref_count < 20:
            bot.send_message(user_id, f"❌ শর্ত পূরণ হয়নি!\n💰 ব্যালেন্স: {balance}/2000\n👥 রেফার: {ref_count}/20")
        else:
            bot.send_message(user_id, "✅ আপনি উইথড্র রিকোয়েস্ট দিতে পারেন। এডমিনের সাথে যোগাযোগ করুন।")

bot.infinity_polling()

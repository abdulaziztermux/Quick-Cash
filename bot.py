import telebot
from telebot import types
import sqlite3

# আপনার টোকেনটি এখানে নিশ্চিত করুন
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
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
    existing_user = cursor.fetchone()

    if not existing_user:
        referred_by = None
        if len(command_args) > 1:
            try:
                referred_by = int(command_args[1])
                if referred_by != user_id:
                    cursor.execute("UPDATE users SET balance = balance + 50, refer_count = refer_count + 1 WHERE user_id = ?", (referred_by,))
                    bot.send_message(referred_by, "🎉 অভিনন্দন! নতুন রেফারেল জয়েন করেছে। ৫০ টাকা বোনাস যোগ হয়েছে।")
            except:
                referred_by = None
        cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referred_by))
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "Quick Cash বটে স্বাগতম! আপনার প্রোফাইল চেক করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "নেই"
    
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, ref_count = data if data else (0, 0)
    conn.close()

    if message.text == '👤 Profile':
        # প্রোফাইল পিকচার সংগ্রহের চেষ্টা
        photos = bot.get_user_profile_photos(user_id)
        profile_text = (f"👤 **ইউজার প্রোফাইল** 👤\n\n"
                        f"📛 নাম: {user_name}\n"
                        f"🆔 UID: `{user_id}`\n"
                        f"📧 ইউজারনেম: {username}\n"
                        f"💰 মোট ব্যালেন্স: {balance} টাকা\n"
                        f"👥 মোট রেফার: {ref_count} জন")
        
        if photos.total_count > 0:
            # যদি ছবি থাকে তবে ছবিসহ টেক্সট পাঠাবে
            bot.send_photo(user_id, photos.photos[0][0].file_id, caption=profile_text, parse_mode="Markdown")
        else:
            # ছবি না থাকলে শুধু টেক্সট পাঠাবে
            bot.send_message(user_id, profile_text, parse_mode="Markdown")

    elif message.text == '📺 Watch Ads':
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(user_id, "✅ বিজ্ঞাপন দেখা সফল! ১০ টাকা যোগ করা হয়েছে।")

    elif message.text == '🤝 Refer & Earn':
        bot_username = "quickcash007_bot" 
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_message(user_id, f"🔗 **আপনার রেফারেল লিংক:**\n{refer_link}\n\nপ্রতি রেফারে পাবেন ৫০ টাকা!")

    elif message.text == '💳 Withdraw':
        if balance < 2000 or ref_count < 20:
            bot.send_message(user_id, f"❌ উইথড্র শর্ত:\n১. ২০০০ টাকা ব্যালেন্স (বর্তমানে: {balance} টাকা)\n২. ২০ জন রেফার (বর্তমানে: {ref_count} জন)")
        else:
            bot.send_message(user_id, "✅ আপনি উইথড্র রিকোয়েস্ট করতে পারবেন। এডমিনের সাথে যোগাযোগ করুন।")

bot.infinity_polling()

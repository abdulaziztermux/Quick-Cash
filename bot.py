import telebot
from telebot import types
import sqlite3

# সেটআপ
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
CHANNEL_ID = '@quickcash007' 
ADMIN_ID = 5418600342 
bot = telebot.TeleBot(API_TOKEN)

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, 
                       balance REAL DEFAULT 0.0, 
                       refer_count INTEGER DEFAULT 0,
                       joined_bonus INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# চ্যানেল সাবস্ক্রিপশন চেক
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/quickcash007")
        check_btn = types.InlineKeyboardButton("✅ Joined (Get 30 TK)", callback_data="check_sub")
        markup.add(btn, check_btn)
        bot.send_message(user_id, "⚠️ কাজ শুরু করতে চ্যানেলে জয়েন করে ৩০ টাকা বোনাস নিন!", reply_markup=markup)
        return
    show_main_menu(user_id)

def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "নিচের মেনু থেকে কাজ শুরু করুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("SELECT joined_bonus FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (user_id, balance, joined_bonus) VALUES (?, ?, ?)", (user_id, 30.0, 1))
        elif row[0] == 0:
            cursor.execute("UPDATE users SET balance = balance + 30, joined_bonus = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "🎉 ৩০ টাকা বোনাস পেয়েছেন!", show_alert=True)
        show_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

# --- মূল বাটন হ্যান্ডলার (Ads, Profile, Refer) ---
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        bot.send_message(user_id, "⚠️ দয়া করে আগে চ্যানেলে জয়েন করুন।")
        return

    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, refs = data if data else (0.0, 0)

    if message.text == '👤 Profile':
        user_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "নেই"
        profile_msg = (f"👤 **ইউজার প্রোফাইল**\n\n"
                       f"📛 নাম: {user_name}\n"
                       f"🆔 UID: `{user_id}`\n"
                       f"📧 ইউজারনেম: {username}\n"
                       f"💰 ব্যালেন্স: {balance} টাকা\n"
                       f"👥 মোট রেফার: {refs} জন")
        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                bot.send_photo(user_id, photos.photos[0][0].file_id, caption=profile_msg, parse_mode="Markdown")
            else:
                bot.send_message(user_id, profile_msg, parse_mode="Markdown")
        except:
            bot.send_message(user_id, profile_msg, parse_mode="Markdown")

    elif message.text == '📺 Watch Ads':
        cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ একটি বিজ্ঞাপন দেখা সম্পন্ন হয়েছে!\n💰 ১০ টাকা আপনার ব্যালেন্সে যোগ করা হয়েছে।")

    elif message.text == '🤝 Refer & Earn':
        bot_info = bot.get_me()
        refer_link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(user_id, f"🤝 **আপনার রেফারেল লিংক:**\n\n`{refer_link}`\n\n✅ প্রতি সফল রেফারে পাবেন ৫০ টাকা!", parse_mode="Markdown")

    elif message.text == '💳 Withdraw':
        if balance < 2000:
            bot.send_message(user_id, f"❌ আপনার ব্যালেন্স পর্যাপ্ত নয়।\n💰 বর্তমান ব্যালেন্স: {balance} TK (প্রয়োজন ২০০০ TK)")
        else:
            bot.send_message(user_id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে। এডমিনের সাথে যোগাযোগ করুন।")

    conn.close()

bot.infinity_polling()

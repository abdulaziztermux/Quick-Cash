import telebot
from telebot import types
import sqlite3
from datetime import datetime

# ১. সঠিক তথ্য দিন
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
CHANNEL_ID = '@quickcash007' 
ADMIN_ID = 5418600342 
bot = telebot.TeleBot(API_TOKEN)

# ২. ডাটাবেস তৈরি
def init_db():
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, 
                       balance REAL DEFAULT 0.0, 
                       refer_count INTEGER DEFAULT 0,
                       joined_bonus INTEGER DEFAULT 0,
                       last_checkin TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ৩. জয়েন চেক ফাংশন
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# ৪. স্টার্ট কমান্ড
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/quickcash007")
        check_btn = types.InlineKeyboardButton("✅ Joined (Get 30 TK)", callback_data="check_sub")
        markup.add(btn)
        markup.add(check_btn)
        bot.send_message(user_id, "⚠️ কাজ শুরু করতে আগে চ্যানেলে জয়েন করে ৩০ টাকা বোনাস নিন!", reply_markup=markup)
        return
    show_main_menu(user_id)

# ৫. মেইন মেনু (সব বাটন এখানে)
def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 My Profile', '📅 Daily Bonus')
    markup.add('🤝 Refer & Earn', '💳 Withdraw Cash')
    bot.send_message(user_id, "নিচের বাটন থেকে কাজ শুরু করুন:", reply_markup=markup)

# ৬. জয়েন বোনাস হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance, joined_bonus) VALUES (?, 0, 0)", (user_id,))
        cursor.execute("SELECT joined_bonus FROM users WHERE user_id=?", (user_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("UPDATE users SET balance = balance + 30, joined_bonus = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.answer_callback_query(call.id, "🎉 ৩০ টাকা বোনাস পেয়েছেন!", show_alert=True)
        conn.close()
        show_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ আগে জয়েন করুন!", show_alert=True)

# ৭. বাটন কাজ করার ফাংশন
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count, last_checkin FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    if not data: return
    balance, refs, last_checkin = data

    if message.text == '👤 My Profile':
        bot.send_message(user_id, f"👤 **প্রোফাইল**\n\n📛 নাম: {user_name}\n🆔 আইডি: `{user_id}`\n💰 ব্যালেন্স: {balance} TK\n👥 রেফার: {refs} জন", parse_mode="Markdown")

    elif message.text == '📅 Daily Bonus':
        today = datetime.now().strftime("%Y-%m-%d")
        if last_checkin == today:
            bot.send_message(user_id, "❌ আজ অলরেডি নিয়েছেন!")
        else:
            cursor.execute("UPDATE users SET balance = balance + 20, last_checkin = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            bot.send_message(user_id, "✅ ২০ টাকা বোনাস পেয়েছেন!")

    elif message.text == '🤝 Refer & Earn':
        link = f"https://t.me/{(bot.get_me()).username}?start={user_id}"
        bot.send_message(user_id, f"🤝 রেফার লিংক:\n`{link}`", parse_mode="Markdown")

    elif message.text == '💳 Withdraw Cash':
        bot.send_message(user_id, f"💰 ব্যালেন্স: {balance} TK\n(২০০০ টাকা হলে উইথড্র করতে পারবেন)")

    conn.close()

bot.infinity_polling()

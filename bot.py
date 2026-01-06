import telebot
from telebot import types
import sqlite3
from datetime import datetime

# কনফিগারেশন
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
                       joined_bonus INTEGER DEFAULT 0,
                       last_checkin TEXT)''')
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
    markup.add('👤 My Profile', '📅 Daily Bonus', '🤝 Refer & Earn', '💳 Withdraw Cash')
    bot.send_message(user_id, "আপনার অ্যাকাউন্ট ড্যাশবোর্ডে স্বাগতম।", reply_markup=markup)

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
        bot.answer_callback_query(call.id, "🎉 ৩০ টাকা জয়েনিং বোনাস পেয়েছেন!", show_alert=True)
        show_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন করেননি!", show_alert=True)

# বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if not is_subscribed(user_id):
        bot.send_message(user_id, "⚠️ আগে চ্যানেলে জয়েন করুন।")
        return

    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count, last_checkin FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, refs, last_checkin = data if data else (0.0, 0, None)

    # ১. প্রোফাইল সেকশন (নাম ও আইডি সহ)
    if message.text == '👤 My Profile':
        profile_text = (f"👤 **ব্যবহারকারীর তথ্য**\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"📛 নাম: {user_name}\n"
                        f"🆔 ইউজার আইডি: `{user_id}`\n"
                        f"💰 বর্তমান ব্যালেন্স: {balance} TK\n"
                        f"👥 মোট রেফার: {refs} জন")
        bot.send_message(user_id, profile_text, parse_mode="Markdown")

    # ২. ডেইলি বোনাস (অ্যাডস এর বদলে নতুন অপশন)
    elif message.text == '📅 Daily Bonus':
        today = datetime.now().strftime("%Y-%m-%d")
        if last_checkin == today:
            bot.send_message(user_id, "❌ আপনি আজ ইতিমধ্যে বোনাস নিয়ে নিয়েছেন। কাল আবার চেষ্টা করুন।")
        else:
            cursor.execute("UPDATE users SET balance = balance + 20, last_checkin = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            bot.send_message(user_id, "✅ অভিনন্দন! আপনি আজকের ডেইলি বোনাস ২০ টাকা পেয়েছেন।")

    # ৩. রেফার লিংক
    elif message.text == '🤝 Refer & Earn':
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(user_id, f"🤝 **আপনার রেফারেল লিংক:**\n\n`{link}`\n\n✅ প্রতি সফল রেফারে পাবেন ৫০ টাকা!", parse_mode="Markdown")

    # ৪. উইথড্র সেকশন
    elif message.text == '💳 Withdraw Cash':
        if balance < 2000:
            bot.send_message(user_id, f"❌ দুঃখিত!\n\nআপনার ব্যালেন্স: {balance} TK\nমিনিমাম উইথড্র: ২০০০ TK\n\nটাকা উত্তোলনের জন্য আরও ইনকাম করুন।")
        else:
            bot.send_message(user_id, "✅ আপনার ব্যালেন্স ২০০০ টাকার বেশি আছে। টাকা উত্তোলনের জন্য এডমিনের কাছে আপনার বিকাশ/নগদ নাম্বারসহ মেসেজ দিন।")

    conn.close()

bot.infinity_polling()

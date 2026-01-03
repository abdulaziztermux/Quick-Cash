import telebot
from telebot import types
import sqlite3

# সেটআপ
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8' # আপনার টোকেন
CHANNEL_ID = '@quickcash007' # আপনার চ্যানেল ইউজারনেম
ADMIN_ID = 5418600342 # আপনার দেওয়া আইডিটি এডমিন হিসেবে সেট করা হলো
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

# --- এডমিন প্যানেল কমান্ড ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID: # শুধুমাত্র আপনার আইডি থেকে এটি কাজ করবে
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        conn.close()

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📊 Total Users", callback_data="total_users")
        btn2 = types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, f"🛠 **Admin Panel**\n\nTotal Users: {total_users}", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ আপনি এই বটের এডমিন নন!")

# এডমিন অ্যাকশন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data in ["total_users", "broadcast"])
def admin_callback(call):
    if call.from_user.id != ADMIN_ID: return

    if call.data == "total_users":
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        bot.answer_callback_query(call.id, f"মোট ইউজার: {count} জন", show_alert=True)
        
    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "সব ইউজারকে পাঠানোর জন্য মেসেজটি লিখুন:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success = 0
    for user in users:
        try:
            bot.send_message(user[0], message.text)
            success += 1
        except: pass
    bot.send_message(ADMIN_ID, f"📢 ব্রডকাস্ট সম্পন্ন!\n✅ সফল: {success} জন")

# --- ইউজার হ্যান্ডলার ---
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
            bot.answer_callback_query(call.id, "🎉 ৩০ টাকা বোনাস পেয়েছেন!", show_alert=True)
        conn.commit()
        conn.close()
        show_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "নিচের মেনু থেকে কাজ শুরু করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id): return

    conn = sqlite3.connect('quick_cash.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, refer_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    balance, refs = data if data else (0.0, 0)

    if message.text == '👤 Profile':
        bot.send_message(user_id, f"👤 **প্রোফাইল**\n💰 ব্যালেন্স: {balance} TK\n👥 রেফার: {refs}")
    elif message.text == '📺 Watch Ads':
        cursor.execute("UPDATE users SET balance = balance + 10 WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ ১০ টাকা যোগ হয়েছে!")
    # অন্যান্য বাটন একইভাবে...
    conn.close()

bot.infinity_polling()

import telebot
from telebot import types
import sqlite3

# আপনার টোকেন এবং চ্যানেলের তথ্য
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
CHANNEL_ID = '@quickcash007' # আপনার দেওয়া চ্যানেলের ইউজারনেম
bot = telebot.TeleBot(API_TOKEN)

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
        markup.add(btn)
        markup.add(check_btn)
        bot.send_message(user_id, "⚠️ কাজ শুরু করার আগে আমাদের চ্যানেলে জয়েন করুন এবং ৩০ টাকা বোনাস বুঝে নিন!", reply_markup=markup)
        return

    show_main_menu(user_id)

def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('👤 Profile', '📺 Watch Ads', '🤝 Refer & Earn', '💳 Withdraw')
    bot.send_message(user_id, "আপনার অ্যাকাউন্টটি সচল আছে। নিচের মেনু থেকে কাজ শুরু করুন।", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        conn = sqlite3.connect('quick_cash.db')
        cursor = conn.cursor()
        cursor.execute("SELECT joined_bonus FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        
        # যদি ইউজার নতুন হয় বা আগে বোনাস না পায়
        if not row:
            cursor.execute("INSERT INTO users (user_id, balance, joined_bonus) VALUES (?, ?, ?)", (user_id, 30.0, 1))
            conn.commit()
            bot.answer_callback_query(call.id, "🎉 অভিনন্দন! আপনি ৩০ টাকা জয়েনিং বোনাস পেয়েছেন।", show_alert=True)
        elif row[0] == 0:
            cursor.execute("UPDATE users SET balance = balance + 30, joined_bonus = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.answer_callback_query(call.id, "🎉 অভিনন্দন! আপনি ৩০ টাকা জয়েনিং বোনাস পেয়েছেন।", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "আপনি ইতিমধ্যে বোনাস নিয়ে নিয়েছেন।")
        
        conn.close()
        show_main_menu(user_id)
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

# অন্যান্য বাটন হ্যান্ডলার (Profile, Ads ইত্যাদি আগের মতো কাজ করবে)

bot.infinity_polling()

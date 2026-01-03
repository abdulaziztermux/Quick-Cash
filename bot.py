import telebot
from telebot import types

# আপনার দেওয়া নতুন টোকেন এখানে বসানো হয়েছে
API_TOKEN = '8346685112:AAHXjfFlyiB0zio_VLdEQzhrtmzZs9uhvp8'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("💰 Balance")
    item2 = types.KeyboardButton("🤝 Invite")
    markup.add(item1, item2)
    
    bot.send_message(message.chat.id, "স্বাগতম! আপনার কুইক ক্যাশ বটটি এখন সচল আছে।", reply_markup=markup)

print("Bot is running...")
bot.infinity_polling()

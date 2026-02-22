from keep_alive import keep_alive
import telebot
from telebot.types import Message
import os
import json
import datetime
import threading
import time

# টোকেন লোড করা হচ্ছে
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# movies.json ফাইল থেকে মুভির তালিকা লোড করা হচ্ছে
with open("movies.json", "r") as f:
    MOVIES = json.load(f)

# লগিং ফাংশন
def log_event(text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a") as f:
        f.write(f"{now} - {text}\n")

# রোবাস্ট মেসেজ ডিলিট ফাংশন (ফাইনাল: 1 ঘণ্টা)
def delete_message_later(chat_id, message_id, delay=3600, retry=3):
    for attempt in range(retry):
        time.sleep(delay if attempt == 0 else 10)  # প্রথমবার ১ ঘণ্টা, পরে ব্যর্থ হলে ১০ সেকেন্ড
        try:
            bot.delete_message(chat_id, message_id)
            log_event(f"✅ Deleted message {message_id} from chat {chat_id}")
            break
        except Exception as e:
            log_event(f"❌ Delete failed for {message_id} in chat {chat_id}, attempt {attempt+1}: {e}")
            continue

# /start কমান্ডের জন্য ফাংশন
@bot.message_handler(commands=['start'])
def send_movie(message: Message):
    parts = message.text.split()
    movie_code = parts[1] if len(parts) > 1 else "default"

    bot.send_message(message.chat.id, "🎬 Welcome to Sk Video Bot!\nPlease wait...")

    # ব্যবহারকারীর তথ্য লগ করা হচ্ছে
    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    log_event(f"{first_name} (@{username}) - ID: {user_id} - Movie: {movie_code}")

    # JSON থেকে মুভি পাঠানো হচ্ছে
    movie = MOVIES.get(movie_code, MOVIES["default"])
    try:
        sent_msg = bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=movie["chat_id"],
            message_id=movie["msg_id"]
        )
        # ব্যাকগ্রাউন্ড থ্রেডে ডিলিট টাইমার চালু
        threading.Thread(target=delete_message_later, args=(message.chat.id, sent_msg.message_id)).start()
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ভিডিও পাঠানো যায়নি। এরর: {e}")
        log_event(f"❌ Failed to send movie {movie_code} to {user_id}: {e}")

# keep_alive ফাংশনটি চালু করা হচ্ছে
keep_alive()

# বট সবসময় চালু রাখার জন্য
print("✅ Bot is running...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

from keep_alive import keep_alive
import telebot
from telebot.types import Message
import os
import json
import datetime
import threading
import time

# টোকেন
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# apk.json থেকে APK লোড করা হচ্ছে
with open("movies.json", "r") as f:
    APK = json.load(f)

# লগিং
def log_event(text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a") as f:
        f.write(f"{now} - {text}\n")

# 1 ঘণ্টা পরে ডিলিট
def delete_message_later(chat_id, message_id, delay=3600, retry=3):
    for attempt in range(retry):
        time.sleep(delay if attempt == 0 else 10)
        try:
            bot.delete_message(chat_id, message_id)
            log_event(f"Deleted message {message_id} from {chat_id}")
            break
        except Exception as e:
            log_event(f"Delete failed {message_id} in {chat_id}: {e}")
            continue

# /start
@bot.message_handler(commands=['start'])
def send_apk(message: Message):

    bot.send_message(message.chat.id, "📲 Welcome!\nPlease wait...")

    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    log_event(f"{first_name} (@{username}) - ID: {user_id} - APK Sent")

    apk = APK.get("default")

    try:
        sent_msg = bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=apk["chat_id"],
            message_id=apk["msg_id"]
        )

        threading.Thread(
            target=delete_message_later,
            args=(message.chat.id, sent_msg.message_id)
        ).start()

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ APK পাঠানো যায়নি: {e}")
        log_event(f"Failed to send APK to {user_id}: {e}")

keep_alive()

print("✅ APK Bot Running...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

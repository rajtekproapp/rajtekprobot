from keep_alive import keep_alive
import telebot
from telebot.types import Message
import os
import json
import datetime
import threading
import time

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

with open("movies.json", "r") as f:
    APK = json.load(f)

def log_event(text):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a") as f:
        f.write(f"{now} - {text}\n")

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

@bot.message_handler(commands=['start'])
def send_apk(message: Message):
    parts = message.text.split()
    apk_code = parts[1] if len(parts) > 1 else "default"

    if apk_code not in APK:
        bot.send_message(message.chat.id, f"❌ APK not found: {apk_code}")
        return

    bot.send_message(message.chat.id, "📲 Please wait...")

    user_id = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name
    log_event(f"{first_name} (@{username}) - ID: {user_id} - APK Sent: {apk_code}")

    apk = APK.get(apk_code)

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
        bot.send_message(message.chat.id, f"❌ Failed to send APK: {e}")
        log_event(f"Failed to send APK {apk_code} to {user_id}: {e}")

keep_alive()
print("✅ Multi-APK Bot Running...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

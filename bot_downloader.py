import os
import telebot
import yt_dlp
from flask import Flask
import threading
import time

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN manquant sur Render!")

bot = telebot.TeleBot(TOKEN)
# Cette ligne tue tous les anciens bots fantômes qui causent le 409
bot.delete_webhook(drop_pending_updates=True)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Junior est en ligne!"

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Yo boss! Envoie-moi un lien TikTok 🔥")

@bot.message_handler(func=lambda m: True)
def download(msg):
    url = msg.text
    if "tiktok.com" not in url and "vt.tiktok" not in url:
        bot.reply_to(msg, "Envoie un vrai lien TikTok boss")
        return

    bot.reply_to(msg, "Je télécharge boss, attends 10s ⏳")
    try:
        ydl_opts = {'format': 'mp4', 'outtmpl': 'video.mp4', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('video.mp4', 'rb') as v:
            bot.send_video(msg.chat.id, v)
        os.remove('video.mp4')
    except Exception as e:
        bot.reply_to(msg, f"Erreur boss: {e}")

def run_bot():
    # skip_pending=True évite le conflit 409
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)

def run_flask():
    # host 0.0.0.0 et port 10000 pour Render
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # On lance Flask dans un thread
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(3)
    # Et le bot dans le thread principal
    run_bot()

import os
import telebot
import yt_dlp
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# TUE LE 409
bot.delete_webhook(drop_pending_updates=True)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is live"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask).start()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Yo boss! Envoie-moi un lien TikTok")

@bot.message_handler(func=lambda m: True)
def download(msg):
    url = msg.text.strip()
    if "tiktok.com" not in url:
        return
    bot.reply_to(msg, "Je télécharge boss, attends 10s ⏳")
    try:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com', 'app_version': '34.1.2'}},
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            bot.send_video(msg.chat.id, video)
        os.remove(filename)
    except Exception as e:
        bot.reply_to(msg, f"Erreur boss: {e}")

bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)

import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
# Petit serveur web pour Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Junior est en ligne !"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salut boss ! Envoie-moi un lien TikTok et je te le télécharge.")
@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    if "tiktok.com" not in url and "vt.tiktok.com" not in url:
        return
    bot.reply_to(message, "Je télécharge ta vidéo, 10 sec boss...")
    ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, timeout=120)
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"Erreur boss: {e}")
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot téléchargeur lancé !")
    bot.polling(none_stop=True, timeout=120)

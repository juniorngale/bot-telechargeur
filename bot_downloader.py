import os
import telebot
import yt_dlp
from flask import Flask
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@jarvisdownloader237"
CHANNEL_LINK = "https://t.me/jarvisdownloader237"
bot = telebot.TeleBot(TOKEN)
bot.delete_webhook(drop_pending_updates=True)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is live - YouTube / TikTok / FB"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask).start()
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False
@bot.message_handler(commands=['start'])
def start(msg):
    if not check_sub(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ S'abonner au canal", url=CHANNEL_LINK))
        bot.send_message(msg.chat.id, f"⚠️ Pour utiliser Jarvis, abonne-toi d'abord 👇\n\n{CHANNEL_LINK}\n\nPuis reviens taper /start", reply_markup=markup)
        return
    bot.reply_to(msg, "Yo boss! 🚀\n\nEnvoie-moi un lien:\n• TikTok\n• YouTube\n• Facebook\n• Instagram\n\nJe télécharge sans logo 🔥")
@bot.message_handler(func=lambda m: True)
def download(msg):
    url = msg.text.strip()
    if not check_sub(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ S'abonner", url=CHANNEL_LINK))
        bot.send_message(msg.chat.id, f"Abonne-toi d'abord 👉 {CHANNEL_LINK}", reply_markup=markup)
        return
    # Vérifie que c'est un lien
    if "http" not in url:
        return bot.reply_to(msg, "Envoie un vrai lien boss 😅")
    bot.reply_to(msg, "Je télécharge boss, attends 10-15s ⏳")
    try:
        # OPTIONS QUI MARCHENT POUR TOUT
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}},
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Video')[:50]
        # Vérifie taille (Telegram limite 50Mo)
        if os.path.getsize(filename) > 49 * 1024 * 1024:
            os.remove(filename)
            return bot.reply_to(msg, "Oups boss vidéo trop lourde (>50Mo) pour Telegram 😥")
        with open(filename, 'rb') as video:
            bot.send_video(msg.chat.id, video, caption=f"Voilà boss 🔥\n{title}\n\nVia @Begedol_bot")    
        try:
            with open(filename, 'rb') as video2:
                bot.send_video(CHANNEL_USERNAME, video2, caption=f"Nouvelle vidéo 🔥\n{title}\n\nTélécharge avec 👉 @Begedol_bot")
        except Exception as e:
            print(f"Erreur canal: {e}")
        os.remove(filename)
    except Exception as e:
        print(e)
        bot.reply_to(msg, f"Erreur boss: lien non supporté ou vidéo privée.\n{e}")
bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)

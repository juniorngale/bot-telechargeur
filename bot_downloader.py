import os
import telebot
import yt_dlp

# On récupère le token caché sur Render
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salut boss ! Envoie-moi un lien TikTok et je te le télécharge.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    if "tiktok.com" not in url and "vt.tiktok.com" not in url:
        return

    bot.reply_to(message, "Je télécharge ta vidéo, 10 sec boss...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        size = os.path.getsize(filename) / (1024*1024)
        print(f"Taille: {size} Mo")

        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, timeout=120)
        
        os.remove(filename)
        
    except Exception as e:
        print(f"Erreur: {e}")
        bot.reply_to(message, f"Erreur boss: {e}")
        if os.path.exists(filename):
            os.remove(filename)

print("Bot téléchargeur lancé !")
bot.polling(none_stop=True, timeout=120)
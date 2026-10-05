import os, telebot, yt_dlp, json, datetime
from flask import Flask
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@jarvisdownloader237"
CHANNEL_LINK = "https://t.me/jarvisdownloader237"

# TOI = ADMIN, TU NE PAYES PAS
ADMIN_IDS = [8670512058]

bot = telebot.TeleBot(TOKEN)
bot.delete_webhook(drop_pending_updates=True)
app = Flask(__name__)

VIP_FILE = "vip.json"
LIMIT_FILE = "limits.json"

def load_vip():
    if os.path.exists(VIP_FILE):
        try: return json.load(open(VIP_FILE))
        except: return []
    return []

def save_vip(user_id):
    vips = load_vip()
    if user_id not in vips:
        vips.append(user_id)
        json.dump(vips, open(VIP_FILE, 'w'))

def is_vip_or_admin(user_id):
    if user_id in ADMIN_IDS: return True
    if user_id in load_vip(): return True
    return False

def load_limits():
    if os.path.exists(LIMIT_FILE):
        try: return json.load(open(LIMIT_FILE))
        except: return {}
    return {}

def can_download(user_id):
    if is_vip_or_admin(user_id): return True, 0
    data = load_limits()
    today = str(datetime.date.today())
    user_data = data.get(str(user_id), {"date": today, "count": 0})
    if user_data["date"]!= today: user_data = {"date": today, "count": 0}
    if user_data["count"] >= 3: return False, 3
    return True, user_data["count"]

def add_count(user_id):
    if is_vip_or_admin(user_id): return
    data = load_limits()
    today = str(datetime.date.today())
    uid = str(user_id)
    if uid not in data or data[uid]["date"]!= today:
        data[uid] = {"date": today, "count": 1}
    else:
        data[uid]["count"] += 1
    json.dump(data, open(LIMIT_FILE, 'w'))

@app.route('/')
def home(): return "Jarvis ADMIN + VIP live"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask).start()

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start', 'vip'])
def start_cmd(msg):
    if not check_sub(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ S'abonner au canal", url=CHANNEL_LINK))
        return bot.send_message(msg.chat.id, f"⚠️ Abonne-toi d'abord 👇\n{CHANNEL_LINK}\nPuis /start", reply_markup=markup)

    is_vip = is_vip_or_admin(msg.from_user.id)
    markup = InlineKeyboardMarkup()
    if not is_vip:
        markup.add(InlineKeyboardButton("⭐ Devenir VIP (15 Stars) - Illimité", callback_data="buy_vip"))

    if msg.from_user.id in ADMIN_IDS:
        statut = "👑 ADMIN ILLIMITÉ (Toi boss)"
    elif is_vip:
        statut = "⭐ VIP ILLIMITÉ"
    else:
        statut = "🆓 Gratuit - 3/jour"

    bot.send_message(msg.chat.id, f"Yo boss {msg.from_user.first_name}! 🚀\nStatut: {statut}\n\nEnvoie un lien TikTok / YouTube / FB", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "buy_vip")
def buy_vip(call):
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Jarvis VIP - Illimité",
        description="Téléchargements illimités, rapides, sans pub.",
        payload="vip_payload",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="VIP", amount=15)],
        start_parameter="vip_affiliate"
    )

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(pre): bot.answer_pre_checkout_query(pre.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(msg):
    save_vip(msg.from_user.id)
    bot.send_message(msg.chat.id, "BOOM! 🔥 Tu es ⭐ VIP ILLIMITÉ maintenant!")

@bot.message_handler(func=lambda m: True)
def download_handler(msg):
    url = msg.text.strip()
    if "http" not in url: return
    if not check_sub(msg.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ S'abonner", url=CHANNEL_LINK))
        return bot.send_message(msg.chat.id, f"Abonne-toi 👉 {CHANNEL_LINK}", reply_markup=markup)

    ok, count = can_download(msg.from_user.id)
    if not ok:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⭐ Passer VIP - 15 Stars", callback_data="buy_vip"))
        return bot.send_message(msg.chat.id, "⛔ Limite 3/3 atteinte aujourd'hui!\nPasse VIP pour illimité 👇", reply_markup=markup)

    info_msg = "⏳ Je télécharge boss..." if is_vip_or_admin(msg.from_user.id) else f"⏳ Je télécharge [{count+1}/3 gratuit]"
    bot.reply_to(msg, info_msg)
    try:
        ydl_opts = {'format': 'best[ext=mp4]/best','outtmpl': '%(id)s.%(ext)s','quiet': True,'no_warnings': True,'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title','Video')[:50]
        if os.path.getsize(filename) > 49*1024*1024:
            os.remove(filename)
            return bot.reply_to(msg, "Trop lourd >50Mo")
        with open(filename, 'rb') as v:
            bot.send_video(msg.chat.id, v, caption=f"{title}\nVia @Begedol_bot")
        try:
            with open(filename, 'rb') as v2:
                bot.send_video(CHANNEL_USERNAME, v2, caption=f"{title}\nVia @Begedol_bot")
        except: pass
        os.remove(filename)
        add_count(msg.from_user.id)
    except Exception as e:
        print(e)
        bot.reply_to(msg, "Lien invalide ou privé.")

bot.infinity_polling(skip_pending=True)

import logging
import os
import random
from datetime import time, datetime
import pytz
from collections import defaultdict

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

PUBLIC_CHANNEL = -1003915029881
PREMIUM_CHANNEL = -1003993028860

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Tu es JardinIA, expert français en jardinage et potager. Réponds de façon claire, pratique et encourageante."

user_limits = defaultdict(lambda: {"count": 0, "date": None})

# ================= DÉTECTION PREMIUM AMÉLIORÉE =================
async def is_premium_user(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=PREMIUM_CHANNEL, user_id=user_id)
        status = member.status
        print(f"DEBUG Premium - User {user_id} status: {status}")  # Pour voir dans les logs
        return status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"DEBUG Premium Error: {e}")
        return False

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Crée une astuce jardinage utile pour aujourd'hui."}],
            temperature=0.8,
            max_tokens=650
        )
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Premium → @JardinIAPremium"
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        await context.bot.send_message(chat_id=PREMIUM_CHANNEL, text=message, parse_mode='Markdown')
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_premium = await is_premium_user(user_id, context)
    status = "💎 **Premium - Illimité**" if is_premium else "🆓 Gratuit - 8 questions/jour"
    
    await update.message.reply_text(
        f"🌱 **Bienvenue sur JardinIA !**\n\n"
        f"Statut actuel : {status}\n\n"
        f"Pose-moi tes questions sur le jardin."
    )

async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Test auto-post...")
    await auto_post(context)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    today = datetime.now(pytz.timezone('Europe/Paris')).date()

    if user_id not in user_limits or user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"count": 0, "date": today}

    is_premium = await is_premium_user(user_id, context)

    if not is_premium and user_limits[user_id]["count"] >= 8:
        await update.message.reply_text(
            "🆓 Tu as atteint ta limite gratuite (8 questions/jour).\n\n"
            "💎 Passe en Premium pour un accès illimité → @JardinIAPremium"
        )
        return

    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": update.message.text}],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(resp.choices[0].message.content)
        
        if not is_premium:
            user_limits[user_id]["count"] += 1
    except Exception as e:
        await update.message.reply_text("🌿 Erreur, réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpost", testpost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA lancé avec détection Premium améliorée")
    app.run_polling()

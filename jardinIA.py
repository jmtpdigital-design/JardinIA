import logging
import os
import asyncio
import random
from datetime import time
import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG RAILWAY =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

PUBLIC_CHANNEL = "@JardinIA"
PREMIUM_CHANNEL = "@JardinIAPremium"

# Configuration Grok (xAI)
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

logging.basicConfig(level=logging.INFO)

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
Tu es JardinIA, un expert français en jardinage, potager et plantes.
Tu donnes des conseils pratiques, clairs, encourageants et réalistes.
Tu privilégies les méthodes naturelles et économiques.
Tu réponds toujours en français correct et accessible.
"""

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = client.chat.completions.create(
            model="grok-4.1-fast",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Crée une astuce jardinage utile et originale pour aujourd'hui."}
            ],
            temperature=0.82,
            max_tokens=650
        )
        
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Version Premium (9,99€) → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post envoyé")
    except Exception as e:
        print(f"Auto-post error: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **Bienvenue sur JardinIA !**\n\n"
        "Ton assistant expert en jardinage et potager (powered by Grok).\n\n"
        "Pose-moi toutes tes questions : semis, arrosage, maladies, etc.\n\n"
        "💎 Version Premium → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.1-fast",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=750
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print(f"Erreur Grok: {e}")
        await update.message.reply_text("🌿 Petite erreur technique, réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    if not TOKEN or not XAI_API_KEY:
        print("❌ ERREUR : TOKEN ou XAI_API_KEY manquant dans Railway Variables")
        exit(1)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA avec Grok API lancé avec succès !")
    app.run_polling()

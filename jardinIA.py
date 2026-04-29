import logging
import os
import random
from datetime import time
import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

PUBLIC_CHANNEL = "@JardinIA"
PREMIUM_CHANNEL = "@JardinIAPremium"

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """
Tu es JardinIA, un expert français en jardinage et potager.
Tu donnes des conseils pratiques, clairs, encourageants et réalistes.
Tu réponds toujours en français.
"""

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": random.choice([
                    "Crée une astuce jardinage utile pour aujourd'hui.",
                    "Crée un petit tutoriel simple.",
                    "Donne un conseil malin pour le potager."
                ])}
            ],
            temperature=0.8,
            max_tokens=650
        )
        
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Version Premium (9,99€/mois) → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post envoyé avec succès")
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **Bienvenue sur JardinIA !**\n\n"
        "Ton assistant expert en jardinage et potager.\n\n"
        "Je poste 3 astuces par jour automatiquement.\n"
        "Pose-moi toutes tes questions !\n\n"
        "💎 Premium → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print(f"Erreur: {e}")
        await update.message.reply_text("🌿 Erreur, réessaie dans 10 secondes...")

# ================= TEST AUTO-POST =================
async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Envoi d'un test auto-post...")
    await auto_post(context)

# ================= LANCEMENT =================
if __name__ == '__main__':
    if not TOKEN or not XAI_API_KEY:
        print("❌ Manque TOKEN ou XAI_API_KEY dans Railway")
        exit(1)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpost", testpost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA lancé avec auto-post (3/jour) + /testpost")
    app.run_polling()

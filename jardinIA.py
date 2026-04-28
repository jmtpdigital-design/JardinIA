import logging
import os
import asyncio
import random
from datetime import time
import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG (Railway) =================
TOKEN = os.getenv("7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PUBLIC_CHANNEL = "@JardinIA"
PREMIUM_CHANNEL = "@JardinIAPremium"

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
Tu es JardinIA, un expert français en jardinage, potager et plantes.
Tu donnes des conseils pratiques, clairs, encourageants et adaptés à la France.
Tu privilégies les méthodes naturelles et économiques.
Tu réponds toujours en français.
"""

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    prompts = [
        "Crée une astuce jardinage courte et utile.",
        "Crée un petit tutoriel étape par étape simple.",
        "Donne un conseil malin pour le jardin ou potager."
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": random.choice(prompts)}
            ],
            temperature=0.8,
            max_tokens=650
        )
        
        message = f"🌱 **JardinIA**\n\n{response.choices[0].message.content}\n\n💎 Premium → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post envoyé")
    except Exception as e:
        print(f"Auto-post error: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **Bienvenue sur JardinIA !**\n\n"
        "Ton assistant expert en jardinage et potager.\n\n"
        "Pose-moi toutes tes questions.\n"
        "Je poste 3 astuces par jour.\n\n"
        "💎 Version Premium (9,99€/mois) → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        print(f"Erreur OpenAI: {e}")
        await update.message.reply_text("🌿 Petite erreur, réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    if not TOKEN or not OPENAI_API_KEY:
        print("❌ ERREUR : TOKEN ou OPENAI_API_KEY manquant dans les variables Railway")
        exit(1)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA lancé avec succès !")
    app.run_polling()

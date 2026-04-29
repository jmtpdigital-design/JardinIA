import logging
import os
import asyncio
import random
from datetime import time
import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI")                    # Variable Railway
GROK_API_KEY = os.getenv("GROK_API_KEY")      # ← Nouvelle variable pour Grok

PUBLIC_CHANNEL = "@JardinIA"
PREMIUM_CHANNEL = "@JardinIAPremium"

# Configuration Grok API (compatible OpenAI)
client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

logging.basicConfig(level=logging.INFO)

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
Tu es JardinIA, un expert français passionné de jardinage et potager.
Tu donnes des conseils pratiques, clairs, encourageants et adaptés à la France.
Tu privilégies les méthodes naturelles et économiques.
"""

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    try:
        response = client.chat.completions.create(
            model="grok-4.1-fast",          # Bon rapport qualité/prix
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Crée une astuce jardinage utile pour aujourd'hui."}
            ],
            temperature=0.8,
            max_tokens=600
        )
        
        message = f"🌱 **JardinIA**\n\n{response.choices[0].message.content}\n\n💎 Premium → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post Grok envoyé")
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **JardinIA est en ligne !** (powered by Grok)\n\n"
        "Pose-moi tes questions sur le jardin et le potager.\n"
        "Je poste 3 astuces par jour."
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis avec Grok...")

    try:
        response = client.chat.completions.create(
            model="grok-4.1-fast",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        print(f"Erreur Grok: {e}")
        await update.message.reply_text("🌿 Petite erreur, réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    if not TOKEN or not GROK_API_KEY:
        print("❌ Manque TOKEN ou GROK_API_KEY dans les variables Railway")
        exit(1)
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA avec Grok API lancé !")
    app.run_polling()

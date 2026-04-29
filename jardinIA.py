import logging
import os
import asyncio
import random
from datetime import time
import pytz

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG (Railway Variables) =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")        # ← Important : nom de variable recommandé

PUBLIC_CHANNEL = "@JardinIA"
PREMIUM_CHANNEL = "@JardinIAPremium"

# Configuration Grok API
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

logging.basicConfig(level=logging.INFO)

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = "Tu es JardinIA, un expert français en jardinage et potager. Réponds de façon claire, pratique et encourageante."

# ================= AUTO-POST =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = client.chat.completions.create(
            model="grok-4.1-fast",   # ou "grok-4" si tu veux plus puissant
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Crée une astuce jardinage utile aujourd'hui."}
            ],
            temperature=0.8,
            max_tokens=600
        )
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Premium → {PREMIUM_CHANNEL}"
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post envoyé")
    except Exception as e:
        print(f"Auto-post error: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **JardinIA** (powered by Grok) est en ligne !\n\n"
        "Pose-moi toutes tes questions sur le jardin et le potager."
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis avec Grok...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.1-fast",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print(f"Erreur Grok: {e}")
        await update.message.reply_text("🌿 Erreur, réessaie dans 10 secondes...")

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
    
    print("🌱 JardinIA avec Grok API lancé !")
    app.run_polling()

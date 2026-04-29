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

PUBLIC_CHANNEL = "@JardinIA"           # ← Ton canal public
PREMIUM_CHANNEL = "@JardinIAPremium"   # ← Ton canal premium

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Tu es JardinIA, expert français en jardinage et potager. Réponds de façon claire, pratique et encourageante."

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
        
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Premium (9,99€/mois) → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Auto-post envoyé dans le canal")
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **JardinIA est en ligne !**\n\n"
        "Je poste 3 astuces par jour dans le canal.\n"
        "Pose-moi tes questions sur le jardin.\n\n"
        "💎 Version Premium → " + PREMIUM_CHANNEL
    )

async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Envoi d'un test auto-post dans le canal...")
    await auto_post(context)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
            temperature=0.75,
            max_tokens=700
        )
        await update.message.reply_text(resp.choices[0].message.content)
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
    
    print("🌱 JardinIA lancé avec auto-post")
    app.run_polling()

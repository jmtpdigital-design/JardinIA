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

PUBLIC_CHANNEL = -1003915029881      # ID de @JardinIA
PREMIUM_CHANNEL = -1003993028860     # ID de @JardinIAPremium

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Tu es JardinIA, expert français en jardinage et potager. Réponds de façon claire, pratique et encourageante."

# ================= AUTO-POST (dans les 2 canaux) =================
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
        
        message = f"🌱 **JardinIA**\n\n{resp.choices[0].message.content}\n\n💎 Premium → @JardinIAPremium"

        # Envoi dans le canal public
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        
        # Envoi dans le canal Premium
        await context.bot.send_message(chat_id=PREMIUM_CHANNEL, text=message, parse_mode='Markdown')
        
        print("✅ Auto-post envoyé dans les 2 canaux")
        
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **JardinIA est en ligne !**\n\n"
        "Je poste 3 astuces par jour dans les 2 canaux.\n"
        "Pose-moi tes questions.\n\n"
        "💎 Premium → @JardinIAPremium"
    )

async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Envoi d'un test dans les 2 canaux...")
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
    
    print("🌱 JardinIA lancé - Auto-post dans les 2 canaux")
    app.run_polling()

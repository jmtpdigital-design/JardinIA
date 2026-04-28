import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import random
from openai import OpenAI
from datetime import time
import pytz

# ================= CONFIG =================
TOKEN = "7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI"                    # ← Ton token BotFather
PUBLIC_CHANNEL = "@JardinIA"               # ← Ton canal public
PREMIUM_CHANNEL = "@JardinIAPremium"

client = OpenAI(api_key="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")

logging.basicConfig(level=logging.INFO)

# ================= AUTO-POST SIMPLE =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    prompts = [
        "Crée une astuce jardinage courte et utile pour aujourd'hui.",
        "Crée un petit tutoriel étape par étape simple.",
        "Donne un conseil malin et pratique pour le potager ou jardin."
    ]
    
    prompt = random.choice(prompts)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=600
        )
        
        message = "🌱 **JardinIA**\n\n" + response.choices[0].message.content + f"\n\n💎 Premium → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        print("✅ Post automatique envoyé")
        
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **JardinIA est en ligne !**\n\n"
        "Pose-moi toutes tes questions sur le jardin et le potager.\n"
        "Je poste 3 astuces par jour automatiquement.\n\n"
        "Version Premium (9,99€) → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await asyncio.sleep(1.2)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Réponds clairement et utilement en français : {text}"}],
            temperature=0.75
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        print(f"Erreur réponse: {e}")
        await update.message.reply_text("🌿 Réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    # Auto-post 3 fois par jour
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA lancé avec succès !")
    app.run_polling()

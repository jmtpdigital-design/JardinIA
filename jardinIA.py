import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import random
from openai import OpenAI
from datetime import time
import pytz

# ==================== CONFIG ====================
TOKEN = "7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI"                    # ← Colle ton token de @BotFather ici
PUBLIC_CHANNEL = "@JardinIA"               # ← Ton canal public
PREMIUM_CHANNEL = "@JardinIAPremium"       # ← Ton canal premium

client = OpenAI(api_key="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")   # ← Ta clé OpenAI

logging.basicConfig(level=logging.INFO)

# ================= AUTO-POST (3 fois par jour) =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    options = [
        ("🌱 Astuce du jour", "Crée une astuce jardinage pratique et utile."),
        ("📋 Mini Tuto", "Crée un petit tutoriel étape par étape clair."),
        ("💡 Conseil expert", "Donne un conseil malin pour le jardin ou potager.")
    ]
    
    title, prompt = random.choice(options)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.82,
            max_tokens=700
        )
        
        message = f"{title}\n\n{response.choices[0].message.content}\n\n"
        message += f"🔥 Accède à la version Premium (9,99€/mois) → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(
            chat_id=PUBLIC_CHANNEL, 
            text=message, 
            parse_mode='Markdown'
        )
    except Exception as e:
        print("Erreur auto-post:", e)

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **Bienvenue sur JardinIA !**\n\n"
        "Ton assistant IA spécialisé jardin & potager.\n\n"
        "Je poste 3 contenus par jour automatiquement.\n"
        "Tu peux me poser toutes tes questions.\n\n"
        "💎 Version Premium (9,99€/mois) → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await asyncio.sleep(random.uniform(1.0, 2.3))
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Réponds de façon claire, utile et détaillée : {text}"}],
            temperature=0.75
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except:
        await update.message.reply_text("🌿 Je prépare une bonne réponse... réessaie dans quelques secondes.")

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
    
    print("🌱 JardinIA est maintenant lancé !")
    app.run_polling()

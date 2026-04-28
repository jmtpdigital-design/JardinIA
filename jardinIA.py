import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import random
from openai import OpenAI
from datetime import time
import pytz

# ================= CONFIG =================
TOKEN = "7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI"                          # ← Ton token BotFather
PUBLIC_CHANNEL = "@JardinIA"                     # ← Ton canal public
PREMIUM_CHANNEL = "@JardinIAPremium"             # ← Ton canal premium

client = OpenAI(api_key="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")     # ← Ta clé OpenAI

logging.basicConfig(level=logging.INFO)

# ================= SYSTEM PROMPT (très important) =================
SYSTEM_PROMPT = """
Tu es JardinIA, un expert français passionné et pédagogue en jardinage, potager et plantes.
Tu donnes des conseils pratiques, réalistes et adaptés au climat français.
Tu privilégies les solutions naturelles, écologiques et peu coûteuses.
Tu réponds de façon claire, encourageante et structurée.
Tu termines souvent par une petite question pour engager l'utilisateur.
"""

# ================= AUTO-POST (3 fois par jour) =================
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    prompts = [
        "Crée une astuce jardinage courte, utile et originale pour aujourd'hui.",
        "Crée un petit tutoriel étape par étape simple et clair.",
        "Donne un conseil malin et écologique pour le potager ou le jardin."
    ]
    
    prompt = random.choice(prompts)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=650
        )
        
        message = f"🌱 **JardinIA**\n\n{response.choices[0].message.content}\n\n"
        message += f"💎 Version Premium (9,99€/mois) → {PREMIUM_CHANNEL}"
        
        await context.bot.send_message(
            chat_id=PUBLIC_CHANNEL, 
            text=message, 
            parse_mode='Markdown'
        )
        print("✅ Auto-post envoyé avec succès")
        
    except Exception as e:
        print(f"Erreur auto-post: {e}")

# ================= COMMANDES UTILISATEURS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌱 **Bienvenue sur JardinIA !**\n\n"
        "Ton expert IA en jardinage et potager.\n\n"
        "Je poste 3 conseils par jour automatiquement.\n"
        "Pose-moi toutes tes questions !\n\n"
        "💎 Accède à la version Premium → " + PREMIUM_CHANNEL
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis à la meilleure réponse...")

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.75,
            max_tokens=800
        )
        await update.message.reply_text(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Erreur OpenAI: {e}")
        await update.message.reply_text("🌿 Petite erreur technique, réessaie dans 10 secondes...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    # Auto-post 3 fois par jour (heures françaises)
    tz = pytz.timezone('Europe/Paris')
    app.job_queue.run_daily(auto_post, time(hour=8, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=14, minute=0, tzinfo=tz))
    app.job_queue.run_daily(auto_post, time(hour=20, minute=0, tzinfo=tz))
    
    print("🌱 JardinIA est lancé avec succès !")
    app.run_polling()

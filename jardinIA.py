import logging
import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

PUBLIC_CHANNEL = "@JardinIA"          # ← Ton canal public
PREMIUM_CHANNEL = "@JardinIAPremium"

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Tu es JardinIA, expert français en jardinage. Réponds clairement et utilement."

# ================= TEST AUTO-POST =================
async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Tentative d'envoi dans le canal...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Crée une astuce jardinage utile pour aujourd'hui."}
            ],
            temperature=0.8,
            max_tokens=600
        )
        
        message = f"🌱 **TEST AUTO-POST**\n\n{resp.choices[0].message.content}"
        
        # Envoi dans le canal
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL, text=message, parse_mode='Markdown')
        await update.message.reply_text("✅ Message envoyé dans le canal @JardinIA ! Vérifie.")
        print("✅ Test post envoyé dans le canal")
        
    except Exception as e:
        error = str(e)
        print(f"ERREUR ENVOI CANAL: {error}")
        await update.message.reply_text(f"❌ Erreur lors de l'envoi dans le canal :\n{error[:300]}")

# ================= COMMANDES =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 JardinIA est en ligne !\nUtilise /testpost pour tester l'auto-post.")

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
        await update.message.reply_text("🌿 Erreur, réessaie dans 10s...")

# ================= LANCEMENT =================
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpost", testpost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    print("🌱 Bot lancé - Utilise /testpost pour tester")
    app.run_polling()

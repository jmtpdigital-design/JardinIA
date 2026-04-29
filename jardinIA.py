import logging
import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Tu es JardinIA, expert français en jardinage. Réponds clairement et utilement."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 JardinIA est en ligne !\nEnvoie /testpost pour tester l'auto-post.")

async def testpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Génération du test auto-post...")

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
        await update.message.reply_text(message)   # Envoie dans la conversation privée
        print("✅ Test auto-post envoyé dans la conversation privée")
    except Exception as e:
        print(f"ERREUR TEST: {e}")
        await update.message.reply_text(f"❌ Erreur : {str(e)[:200]}")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")
    # (on garde la fonction generate pour les questions normales)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpost", testpost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    print("🌱 Version diagnostic lancée - Utilise /testpost")
    app.run_polling()

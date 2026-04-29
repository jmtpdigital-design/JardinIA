import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 JardinIA est en ligne !\nEnvoie une question.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")

    try:
        resp = client.chat.completions.create(
            model="grok-4.20",
            messages=[
                {"role": "system", "content": "Tu es JardinIA, expert en jardinage français."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=600
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print("ERREUR:", str(e))
        await update.message.reply_text("🌿 Erreur, réessaie dans 10s.")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    print("🌱 BOT MINIMAL LANCÉ")
    app.run_polling()

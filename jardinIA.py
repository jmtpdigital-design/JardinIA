import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TOKEN = "7966522581:AAGyVpPbz4if12pSIz7uFMzCvYNTtVFIljI"
client = OpenAI(api_key="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")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌱 JardinIA est en ligne !\nPose-moi une question sur le jardin.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🌱 Je réfléchis...")   # Pour voir si ça arrive ici
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Réponds en français : {text}"}],
            max_tokens=500
        )
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        print(f"ERREUR: {e}")
        await update.message.reply_text(f"Erreur : {str(e)[:150]}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    print("🌱 Version minimale lancée !")
    app.run_polling()

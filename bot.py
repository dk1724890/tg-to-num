import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== CONFIG =====
BOT_TOKEN = "YOUR_BOT_TOKEN"

API_KEY = "RACKSUN"
BASE_URL = "http://api.subhxcosmo.in/api?key=RACKSUN&type=tg&term=1234567890"

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello!\n\nSend me a Telegram username or number.\nExample:\n@username or 1234567890"
    )

# ===== MAIN HANDLER =====
async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    await update.message.reply_text("🔍 Searching...")

    try:
        params = {
            "key": API_KEY,
            "type": "tg",
            "term": user_input
        }

        res = requests.get(BASE_URL, params=params, timeout=10)
        data = res.json()

        # response handle (customize based on API response)
        if "result" in data:
            result = data["result"]
        else:
            result = data

        await update.message.reply_text(f"📱 Result:\n{result}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{str(e)}")

# ===== MAIN =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))

print("✅ Bot Running...")
app.run_polling()

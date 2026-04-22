import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 Railway ENV variable se token lega
BOT_TOKEN = os.getenv("8671824136:AAFKoEe6f8P2Jxrg6hBXt_hcsreX5oyOlnU")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Send UID / Username\nI will fetch info...")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    loading_msg = await update.message.reply_text("⚡ Fetching Data...")

    try:
        url = f"http://api.subhxcosmo.in/api?key=RACKSUN&type=tg&term={text}"
        response = requests.get(url, timeout=10)
        data = response.json()

        res = data.get("result", {})

        message = f"""
✨ <b>Details Found</b>

👤 <b>TG ID:</b> {res.get("tg_id", "N/A")}
🌍 <b>Country:</b> {res.get("country", "N/A")} ({res.get("country_code", "")})
📞 <b>Number:</b> {res.get("number", "N/A")}

✅ <b>Status:</b> {data.get("success", False)}
📩 <b>Message:</b> {data.get("msg", "")}
"""

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=loading_msg.message_id,
            text=message,
            parse_mode="HTML"
        )

    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=loading_msg.message_id,
            text="❌ Error fetching data"
        )

# 🚀 Run bot
if name == "main":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling()

import os
import requests
from flask import Flask
from threading import Thread
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    KeyboardButtonRequestChat,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ===== CONFIG =====
# Railway environment variables se token lega
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

# API Configuration
API_KEY = "RACKSUN"
BASE_URL = "http://api.subhxcosmo.in/api?key=RACKSUN&type=tg&term=1234567890"

# ===== FLASK KEEP-ALIVE (Railway/Render ke liye) =====
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "Bot is Alive!"

def run_flask():
    # Railway variable "PORT" use karega, agar nahi mila toh 8080 default
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn_user = KeyboardButton(
        text="👤 User",
        request_users=KeyboardButtonRequestUsers(request_id=1, max_quantity=1),
    )
    btn_group = KeyboardButton(
        text="👥 Group",
        request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
    )
    btn_channel = KeyboardButton(
        text="📢 Channel",
        request_chat=KeyboardButtonRequestChat(request_id=3, chat_is_channel=True),
    )

    markup = ReplyKeyboardMarkup(
        [[btn_user, btn_group, btn_channel]],
        resize_keyboard=True,
    )

    welcome_msg = (
        f"*Welcome To @num_info7_bot* 🖐️\n\n"
        f"*Your ID :* `{update.effective_user.id}`\n\n"
        f"Send me a Telegram username or number to look up.\n"
        f"Example: @username or 1234567890\n\n"
        f"Or use the buttons below to get User/Group/Channel ID:"
    )

    await update.message.reply_text(
        welcome_msg,
        reply_markup=markup,
        parse_mode="Markdown",
    )

# ===== USER ID HANDLER =====
async def handle_users_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.users_shared:
        for user in update.message.users_shared.users:
            await update.message.reply_text(
                f"👤 *User ID:* `{user.user_id}`",
                parse_mode="Markdown",
            )

# ===== CHAT ID HANDLER =====
async def handle_chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_shared:
        await update.message.reply_text(
            f"🆔 *Chat ID:* `{update.message.chat_shared.chat_id}`",
            parse_mode="Markdown",
        )

# ===== LOOKUP HANDLER =====
async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    status_msg = await update.message.reply_text("🔍 Searching...")

    try:
        params = {
            "key": API_KEY,
            "type": "tg",
            "term": user_input,
        }

        res = requests.get(BASE_URL, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()

        result = data.get("result", data)
        
        # Result display logic
        if isinstance(result, dict):
            if str(result.get("success", "")).lower() == "false":
                text = "❌ *Data Not Found!*"
            else:
                lines = ["📋 *Result:*\n"]
                for key, value in result.items():
                    if key not in ("success", "msg"):
                        label = key.replace("_", " ").title()
                        lines.append(f"*{label}:* `{value}`")
                text = "\n".join(lines) if len(lines) > 1 else "❌ *Data Not Found!*"
        else:
            text = f"📋 *Result:*\n`{result}`"

        await status_msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error:\n`{str(e)}`", parse_mode="Markdown")

# ===== MAIN (YAHAN FIX KIYA HAI) =====
if __name__ == "__main__":
    # 1. Flask server start karein
    keep_alive()
    print("✅ Flask Server Started!")

    # 2. Bot build karein
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 3. Handlers register karein
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.USERS_SHARED, handle_users_shared))
    app.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED, handle_chat_shared))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))

    # 4. Polling start karein
    print("✅ Bot is Online!")
    app.run_polling()

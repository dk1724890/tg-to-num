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
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    # Testing ke liye aap yahan apna token dal sakte hain
    # BOT_TOKEN = "YOUR_TOKEN_HERE"
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

API_KEY = "racksun"
BASE_URL = "http://api.subhxcosmo.in/api?key=RACKSUN&type=tg&term=1234567890"

# ===== FLASK KEEP-ALIVE =====
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "Bot is Alive!"

def run_flask():
    # Flask default 8000 port par deploy nahi hota aksar, 5000 ya 8080 use karein
    flask_app.run(host="0.0.0.0", port=8080)

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
        res.raise_for_status() # Check for HTTP errors
        data = res.json()

        result = data.get("result", data)
        not_found = False

        if isinstance(result, dict):
            if not result.get("success", True):
                not_found = True
            else:
                fields = {k: v for k, v in result.items() if k not in ("success", "msg")}
                if not fields:
                    not_found = True
                else:
                    lines = ["📋 *Result:*\n"]
                    for key, value in fields.items():
                        label = key.replace("_", " ").title()
                        lines.append(f"*{label}:* `{value}`")
                    text = "\n".join(lines)
        elif not result:
            not_found = True
        else:
            text = f"📋 *Result:*\n{result}"

        if not_found:
            text = "❌ *Data Not Found!*\n\nNo information found for this input."

        await status_msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error:\n`{str(e)}`", parse_mode="Markdown")

# ===== MAIN =====
if __name__ == "__main__":
    keep_alive()
    print("✅ Flask Server Started!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.USERS_SHARED, handle_users_shared))
    app.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED, handle_chat_shared))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))

    print("✅ Bot is Online!")
    app.run_polling()

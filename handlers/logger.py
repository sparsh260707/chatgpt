from telegram import Update
from telegram.ext import ContextTypes
from config import Config
import html


# =========================
# User Start Logger
# =========================

async def log_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        "🚀 <b>Bot Started</b>\n\n"
        f"👤 User: {html.escape(user.full_name)}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: @{user.username if user.username else 'None'}"
    )

    await context.bot.send_message(
        Config.LOG_GROUP_ID,
        text,
        parse_mode="HTML"
    )


# =========================
# Bot Added / Removed Logger
# =========================

async def log_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    left_member = update.message.left_chat_member

    bot_id = context.bot.id

    # Bot Added
    if new_members:
        for member in new_members:
            if member.id == bot_id:
                text = (
                    "➕ <b>Bot Added to Group</b>\n\n"
                    f"👥 Group: {html.escape(chat.title)}\n"
                    f"🆔 Group ID: <code>{chat.id}</code>"
                )

                await context.bot.send_message(
                    Config.LOG_GROUP_ID,
                    text,
                    parse_mode="HTML"
                )

    # Bot Removed
    if left_member and left_member.id == bot_id:
        text = (
            "❌ <b>Bot Removed from Group</b>\n\n"
            f"👥 Group: {html.escape(chat.title)}\n"
            f"🆔 Group ID: <code>{chat.id}</code>"
        )

        await context.bot.send_message(
            Config.LOG_GROUP_ID,
            text,
            parse_mode="HTML"
        )

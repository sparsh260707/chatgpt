from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from database import messages_col


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 🔐 Owner check
    if update.effective_user.id != Config.ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    sent = 0
    failed = 0

    # Determine broadcast content
    if update.message.reply_to_message:
        broadcast_message = update.message.reply_to_message
        mode = "reply"
    elif context.args:
        broadcast_text = " ".join(context.args)
        mode = "text"
    else:
        await update.message.reply_text(
            "Usage:\n"
            "Reply to a message with /broadcast\n"
            "OR\n"
            "/broadcast Your message"
        )
        return

    users = messages_col.distinct("user_id")
    groups = messages_col.distinct("group_id")

    targets = set(users + groups)

    for chat_id in targets:
        try:
            if mode == "reply":
                await broadcast_message.copy(chat_id)
            else:
                await context.bot.send_message(chat_id, broadcast_text)

            sent += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast Completed\n\n"
        f"✔ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )

import logging
import html
import uvloop

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import Config
from database import (
    increment_message,
    get_leaderboard,
    get_user_total_messages,
    get_total_group_messages,
    get_user_info
)

from handlers.topusers import topusers, global_buttons
from handlers.mytop import mytop, mytop_buttons
from handlers.topgroups import topgroups, topgroups_buttons
from handlers.broadcast import broadcast
from handlers.logger import log_start, log_bot_status
from handlers.events import auto_event, check_event_answer


# =========================
# PERFORMANCE BOOST
# =========================
uvloop.install()

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

Config.validate()

app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

START_IMAGE = "https://files.catbox.moe/sscl7n.jpg"
SUPPORT_LINK = Config.SUPPORT_GROUP


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_start(update, context)

    keyboard = [
        [InlineKeyboardButton(
            "Add me in a group",
            url=f"https://t.me/{context.bot.username}?startgroup=true"
        )],
        [
            InlineKeyboardButton("Settings", callback_data="settings"),
            InlineKeyboardButton("Stats", callback_data="rank_overall")
        ]
    ]

    await update.message.reply_photo(
        photo=START_IMAGE,
        caption="CHATFIGHT BOT\n\nCounts messages and shows rankings.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# SETTINGS
# =========================
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Support Channel", url=SUPPORT_LINK)],
        [InlineKeyboardButton("Back", callback_data="back_home")]
    ]

    await query.edit_message_caption(
        caption="SETTINGS\n\nSelect an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(
            "Add me in a group",
            url=f"https://t.me/{context.bot.username}?startgroup=true"
        )],
        [
            InlineKeyboardButton("Settings", callback_data="settings"),
            InlineKeyboardButton("Stats", callback_data="rank_overall")
        ]
    ]

    await query.edit_message_caption(
        caption="CHATFIGHT BOT\n\nCounts messages and shows rankings.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# PRIVATE TOTALS
# =========================
async def today_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    total = get_user_total_messages(update.effective_user.id, "today")
    await update.message.reply_text(f"Today Messages: {total:,}")


async def week_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    total = get_user_total_messages(update.effective_user.id, "week")
    await update.message.reply_text(f"Week Messages: {total:,}")


async def overall_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    total = get_user_total_messages(update.effective_user.id, "overall")
    await update.message.reply_text(f"Overall Messages: {total:,}")


# =========================
# MESSAGE COUNTER
# =========================
async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if message.chat.type not in ["group", "supergroup"]:
        return

    if message.sender_chat or not message.from_user or message.from_user.is_bot:
        return

    increment_message(message.from_user, message.chat)


# =========================
# LEADERBOARD
# =========================
async def rankings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Use this in a group.")
        return

    await send_leaderboard(update, context, "overall")


async def send_leaderboard(update, context, mode):
    group_id = update.effective_chat.id
    data = get_leaderboard(group_id, mode)
    total_messages = get_total_group_messages(group_id, mode)

    text = "LEADERBOARD\n\n"

    if not data:
        text += "No data yet.\n"
    else:
        for i, (user_id, count) in enumerate(data, start=1):
            user_doc = get_user_info(user_id)
            full_name = user_doc["full_name"] if user_doc and user_doc.get("full_name") else "User"
            safe_name = html.escape(full_name)
            name = f"<a href='tg://user?id={user_id}'>{safe_name}</a>"
            text += f"{i}. {name} - {count:,}\n"

    text += f"\nTotal messages: {total_messages:,}"

    keyboard = [[
        InlineKeyboardButton("Overall", callback_data="rank_overall"),
        InlineKeyboardButton("Today", callback_data="rank_today"),
        InlineKeyboardButton("Week", callback_data="rank_week"),
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, parse_mode="HTML", reply_markup=reply_markup)


async def ranking_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "rank_today":
        await send_leaderboard(update, context, "today")
    elif query.data == "rank_week":
        await send_leaderboard(update, context, "week")
    else:
        await send_leaderboard(update, context, "overall")


# =========================
# HANDLERS
# =========================
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rankings", rankings))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("mytop", mytop))
app.add_handler(CommandHandler("topusers", topusers))
app.add_handler(CommandHandler("topgroups", topgroups))

app.add_handler(CommandHandler("today", today_total))
app.add_handler(CommandHandler("week", week_total))
app.add_handler(CommandHandler("overall", overall_total))

app.add_handler(CallbackQueryHandler(settings_menu, pattern="^settings$"))
app.add_handler(CallbackQueryHandler(back_home, pattern="^back_home$"))
app.add_handler(CallbackQueryHandler(ranking_buttons, pattern="^rank_"))
app.add_handler(CallbackQueryHandler(global_buttons, pattern="^g_"))
app.add_handler(CallbackQueryHandler(mytop_buttons, pattern="^my_"))
app.add_handler(CallbackQueryHandler(topgroups_buttons, pattern="^tg_"))

app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, count_messages), group=0)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_event_answer), group=1)

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, log_bot_status))
app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, log_bot_status))


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run_polling(drop_pending_updates=True)

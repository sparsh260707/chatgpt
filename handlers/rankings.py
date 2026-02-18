import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from database import (
    get_leaderboard,
    get_total_group_messages,
    get_user_info
)


async def rankings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Use this in a group.")
        return

    await send_leaderboard(update, context, "overall")


async def send_leaderboard(update, context, mode):

    group_id = update.effective_chat.id
    data = get_leaderboard(group_id, mode)
    total_messages = get_total_group_messages(group_id, mode)

    text = "📈 <b>LEADERBOARD</b>\n\n"

    if not data:
        text += "No data yet.\n"
    else:
        medals = ["🥇", "🥈", "🥉"]

        for i, (user_id, count) in enumerate(data, start=1):

            user_doc = get_user_info(user_id)

            if user_doc and user_doc.get("full_name"):
                full_name = user_doc["full_name"]
            else:
                full_name = "User"

            safe_name = html.escape(full_name)
            name = f"<a href='tg://user?id={user_id}'>{safe_name}</a>"

            medal = medals[i - 1] if i <= 3 else f"{i}."
            text += f"{medal} {name} • {count:,}\n"

    text += f"\n📨 <b>Total messages:</b> {total_messages:,}"

    keyboard = [[
        InlineKeyboardButton(
            "Overall ✅" if mode == "overall" else "Overall",
            callback_data="rank_overall"
        ),
        InlineKeyboardButton(
            "Today ✅" if mode == "today" else "Today",
            callback_data="rank_today"
        ),
        InlineKeyboardButton(
            "Week ✅" if mode == "week" else "Week",
            callback_data="rank_week"
        ),
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except BadRequest as e:
            # Ignore harmless errors
            if "Message is not modified" not in str(e):
                raise
    else:
        await update.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )


async def ranking_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # ⚡ instant remove loading circle
    try:
        await query.answer(cache_time=0)
    except:
        pass

    if query.data == "rank_today":
        await send_leaderboard(update, context, "today")
    elif query.data == "rank_week":
        await send_leaderboard(update, context, "week")
    else:
        await send_leaderboard(update, context, "overall")

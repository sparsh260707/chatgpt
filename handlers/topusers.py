import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from database import (
    get_global_leaderboard,
    get_total_global_messages,
    get_user_info
)


# =========================
# COMMAND ENTRY
# =========================

async def topusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_global_leaderboard(update, context, "overall")


# =========================
# MAIN FUNCTION
# =========================

async def send_global_leaderboard(update, context, mode):

    data = get_global_leaderboard(mode)
    total_messages = get_total_global_messages(mode)

    text = "📈 <b>GLOBAL LEADERBOARD</b> 🌍\n\n"
    medals = ["🥇", "🥈", "🥉"]

    if not data:
        text += "No data yet."
    else:
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

    keyboard = [
        [
            InlineKeyboardButton(
                "Overall ✅" if mode == "overall" else "Overall",
                callback_data="g_overall"
            )
        ],
        [
            InlineKeyboardButton(
                "Today ✅" if mode == "today" else "Today",
                callback_data="g_today"
            ),
            InlineKeyboardButton(
                "Week ✅" if mode == "week" else "Week",
                callback_data="g_week"
            ),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # =========================
    # SAFE EDIT OR SEND
    # =========================

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except BadRequest as e:
            # Ignore if message not modified
            if "Message is not modified" not in str(e):
                raise
    else:
        await update.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )


# =========================
# BUTTON HANDLER
# =========================

async def global_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    try:
        await query.answer()
    except:
        pass

    mode = "overall"

    if query.data == "g_today":
        mode = "today"
    elif query.data == "g_week":
        mode = "week"
    elif query.data == "g_overall":
        mode = "overall"

    await send_global_leaderboard(update, context, mode)

import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import get_user_groups_stats, get_total_group_messages


async def mytop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_mytop(update, context, "overall")


async def send_mytop(update, context, mode):
    user_id = update.effective_user.id
    data = get_user_groups_stats(user_id, mode)

    text = "📈 <b>TOP GROUPS</b> | 🌍\n\n"

    if not data:
        text += "No activity yet."
    else:
        for i, (group_id, count) in enumerate(data, start=1):
            try:
                chat = await context.bot.get_chat(group_id)
                name = html.escape(chat.title or "Group")
            except:
                continue

            text += f"{i}. 👥 {name} • {count:,}\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "Overall ✅" if mode == "overall" else "Overall",
                callback_data="my_overall"
            )
        ],
        [
            InlineKeyboardButton(
                "Today ✅" if mode == "today" else "Today",
                callback_data="my_today"
            ),
            InlineKeyboardButton(
                "Week ✅" if mode == "week" else "Week",
                callback_data="my_week"
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )


async def mytop_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "my_today":
        await send_mytop(update, context, "today")
    elif query.data == "my_week":
        await send_mytop(update, context, "week")
    else:
        await send_mytop(update, context, "overall")

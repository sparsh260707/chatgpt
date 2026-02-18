from database import get_user_stats

async def stats(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    count = get_user_stats(user_id)

    await query.edit_message_text(
        f"📊 YOUR STATS\n\nMessages sent: {count}"
    )

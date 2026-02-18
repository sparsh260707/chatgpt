import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import add_bonus_points
from pymongo import MongoClient
from config import Config

# Mongo to get groups
client = MongoClient(Config.MONGO_URI)
db = client["chatfight"]
messages_col = db["messages"]

active_events = {}  # group_id: correct_answer


# =========================
# Send Event To All Groups
# =========================

async def auto_event(context: ContextTypes.DEFAULT_TYPE):

    groups = messages_col.distinct("group_id")

    for group_id in groups:

        a = random.randint(5, 20)
        b = random.randint(5, 20)
        answer = a + b

        question = (
            f"⚡ <b>QUICK EVENT</b>\n\n"
            f"Solve: <b>{a} + {b}</b>\n"
            f"🏆 Prize: +20 points\n"
            f"⏳ First correct answer wins!"
        )

        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=question,
                parse_mode="HTML"
            )

            active_events[group_id] = answer

        except:
            continue


# =========================
# Check Answers
# =========================

async def check_event_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    group_id = update.message.chat.id

    if group_id not in active_events:
        return

    try:
        user_answer = int(update.message.text.strip())
    except:
        return

    correct_answer = active_events[group_id]

    if user_answer == correct_answer:

        user = update.message.from_user
        add_bonus_points(user.id, group_id, 20)

        await update.message.reply_text(
            f"🎉 {user.mention_html()} won +20 points! 🥳",
            parse_mode="HTML"
        )

        try:
            await update.message.set_reaction("🎉")
        except:
            pass

        del active_events[group_id]

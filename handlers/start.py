from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

START_IMAGE = "https://files.catbox.moe/73mktq.jpg"

SUPPORT_GROUP = "https://t.me/Newchatfightsupport"


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    updates_channel = context.bot_data.get("updates_channel")

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add me in a group",
                url=f"https://t.me/{context.bot.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("📊 Your stats", callback_data="stats"),
        ],
    ]

    if updates_channel:
        keyboard.append(
            [InlineKeyboardButton("📢 Updates", url=updates_channel)]
        )

    text = (
        "🤖 <b>Welcome, this bot will count group messages, "
        "create rankings and give prizes to users!</b>\n\n"
        "📚 By using this bot, you consent to the processing of your data "
        "through the <a href='https://example.com/privacy'>Privacy Policy</a> "
        "and to compliance with the <a href='https://example.com/rules'>Rules</a>."
    )

    await update.message.reply_photo(
        photo=START_IMAGE,
        caption=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


# =========================
# SETTINGS CALLBACK
# =========================

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "💬 Support",
                url=SUPPORT_GROUP
            )
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="back_home")
        ]
    ]

    await query.edit_message_caption(
        caption="⚙️ <b>Settings</b>\n\nNeed help? Join our support group.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# BACK BUTTON
# =========================

async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

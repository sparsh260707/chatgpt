import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # =========================
    # Telegram
    # =========================
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL")

    # =========================
    # Admin
    # =========================
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

    # =========================
    # Support
    # =========================
    SUPPORT_GROUP = os.getenv("SUPPORT_GROUP")

    # =========================
    # Logger
    # =========================
    LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID"))

    # =========================
    # MongoDB
    # =========================
    MONGO_URI = os.getenv("MONGO_URI")

    # =========================
    # Validation
    # =========================
    @staticmethod
    def validate():
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN missing in .env")

        if not Config.MONGO_URI:
            raise ValueError("MONGO_URI missing in .env")

        if not Config.ADMIN_ID:
            raise ValueError("ADMIN_ID missing in .env")

        if not Config.LOG_GROUP_ID:
            raise ValueError("LOG_GROUP_ID missing in .env")

from pymongo import MongoClient, ASCENDING, DESCENDING
from config import Config
from datetime import datetime, timedelta
import pytz

# =========================
# Mongo Connection
# =========================

client = MongoClient(Config.MONGO_URI)
db = client["chatfight"]

messages_col = db["messages"]
users_col = db["users"]
groups_col = db["groups"]
events_col = db["events"]

# =========================
# Indexes (Optimized)
# =========================

messages_col.create_index(
    [("user_id", ASCENDING), ("group_id", ASCENDING), ("date", ASCENDING)],
    unique=True
)

# Performance index for leaderboard sorting
messages_col.create_index(
    [("group_id", ASCENDING), ("date", ASCENDING)]
)

users_col.create_index("user_id", unique=True)
groups_col.create_index("group_id", unique=True)

events_col.create_index(
    [("user_id", ASCENDING), ("group_id", ASCENDING)],
    unique=True
)

# =========================
# IST DATE SYSTEM
# =========================

def _get_today():
    india = pytz.timezone("Asia/Kolkata")
    return datetime.now(india).strftime("%Y-%m-%d")


def _build_date_filter(mode):

    today = _get_today()
    today_date = datetime.strptime(today, "%Y-%m-%d").date()
    week_ago = (today_date - timedelta(days=7)).strftime("%Y-%m-%d")

    if mode == "today":
        return {"date": today}

    if mode == "week":
        return {"date": {"$gte": week_ago}}

    return {}

# =========================
# MESSAGE COUNTER
# =========================

def increment_message(user, chat):

    today = _get_today()

    messages_col.update_one(
        {
            "user_id": user.id,
            "group_id": chat.id,
            "date": today
        },
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "user_id": user.id,
                "group_id": chat.id,
                "date": today
            }
        },
        upsert=True
    )

    users_col.update_one(
        {"user_id": user.id},
        {
            "$set": {
                "full_name": user.full_name or "User",
                "username": user.username or ""
            }
        },
        upsert=True
    )

    groups_col.update_one(
        {"group_id": chat.id},
        {
            "$set": {"title": chat.title or "Group"}
        },
        upsert=True
    )

# =========================
# USER / GROUP INFO
# =========================

def get_user_info(user_id: int):
    return users_col.find_one({"user_id": user_id})


def get_group_info(group_id: int):
    return groups_col.find_one({"group_id": group_id})

# =========================
# EVENT BONUS SYSTEM
# =========================

def add_bonus_points(user_id: int, group_id: int, points: int):

    events_col.update_one(
        {
            "user_id": user_id,
            "group_id": group_id
        },
        {
            "$inc": {"points": points}
        },
        upsert=True
    )


def get_event_points(user_id: int, group_id: int):

    data = events_col.find_one(
        {"user_id": user_id, "group_id": group_id}
    )
    return data["points"] if data and "points" in data else 0

# =========================
# GROUP LEADERBOARD
# =========================

def get_leaderboard(group_id: int, mode="overall"):

    match_stage = {"group_id": group_id}
    match_stage.update(_build_date_filter(mode))

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$user_id",
                "total": {"$sum": "$count"}
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]

    results = list(messages_col.aggregate(pipeline))
    return [(r["_id"], r["total"]) for r in results]

# =========================
# GLOBAL LEADERBOARD
# =========================

def get_global_leaderboard(mode="overall"):

    match_stage = _build_date_filter(mode)

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$user_id",
                "total": {"$sum": "$count"}
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]

    results = list(messages_col.aggregate(pipeline))
    return [(r["_id"], r["total"]) for r in results]

# =========================
# USER GROUP STATS
# =========================

def get_user_groups_stats(user_id: int, mode="overall"):

    match_stage = {"user_id": user_id}
    match_stage.update(_build_date_filter(mode))

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$group_id",
                "total": {"$sum": "$count"}
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]

    results = list(messages_col.aggregate(pipeline))
    return [(r["_id"], r["total"]) for r in results]

# =========================
# USER GLOBAL TOTALS (ALL GROUPS)
# =========================

def get_user_total_messages(user_id: int, mode="overall"):

    match_stage = {"user_id": user_id}
    match_stage.update(_build_date_filter(mode))

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$count"}
            }
        }
    ]

    result = list(messages_col.aggregate(pipeline))
    return result[0]["total"] if result else 0

# =========================
# TOP GROUPS
# =========================

def get_top_groups(mode="overall"):

    match_stage = _build_date_filter(mode)

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$group_id",
                "total": {"$sum": "$count"}
            }
        },
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]

    results = list(messages_col.aggregate(pipeline))
    return [(r["_id"], r["total"]) for r in results]

# =========================
# TOTAL GROUP MESSAGES
# =========================

def get_total_group_messages(group_id: int, mode="overall"):

    match_stage = {"group_id": group_id}
    match_stage.update(_build_date_filter(mode))

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$count"}
            }
        }
    ]

    result = list(messages_col.aggregate(pipeline))
    return result[0]["total"] if result else 0

# =========================
# TOTAL GLOBAL MESSAGES
# =========================

def get_total_global_messages(mode="overall"):

    match_stage = _build_date_filter(mode)

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$count"}
            }
        }
    ]

    result = list(messages_col.aggregate(pipeline))
    return result[0]["total"] if result else 0

# =========================
# GLOBAL USER COUNT
# =========================

def get_global_user_count():
    return users_col.count_documents({})
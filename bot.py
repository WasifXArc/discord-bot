import discord
from discord.ext import tasks, commands
import datetime
import random
import os

# ================= CONFIG =================

TOKEN = os.getenv("DISCORD_TOKEN")

USER_IDS = [
    1069095155275153459,
    1346102480785768620,
    954962586141597779,
]

PK_TZ = datetime.timezone(datetime.timedelta(hours=5))

# TODAY is rest day
LAST_REST_DATE = datetime.date(2025, 12, 28)

REST_HOUR = 20
REST_MINUTE = 12

WORKOUT_TIMES = [(16, 30), (22, 30)]

MESSAGES = [
    "Get today’s workout in.",
    "Just move today.",
    "Show up for today’s session.",
    "Train today. Nothing extra.",
    "Do the work scheduled for today.",
    "Today = movement.",
    "One workout. That’s enough.",
    "No pressure. Just train.",
    "Do today’s workout and move on.",
    "Do what you planned today.",
]

REST_MESSAGES = [
    "Rest today. You’ve earned it.",
    "No workout today. Recover well.",
    "Today is for rest and recovery.",
    "You’ve worked hard. Take today off.",
    "Rest day. Come back stronger tomorrow.",
]

used_messages = []
last_rest_sent_on = None
last_workout_sent = set()

# ================= BOT =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HELPERS =================

def is_rest_day(today):
    return (today - LAST_REST_DATE).days % 8 == 0

def get_daily_message():
    global used_messages
    if len(used_messages) == len(MESSAGES):
        used_messages = []
    msg = random.choice([m for m in MESSAGES if m not in used_messages])
    used_messages.append(msg)
    return msg

# ================= TASK =================

@tasks.loop(seconds=30)
async def scheduler():
    global last_rest_sent_on

    now = datetime.datetime.now(PK_TZ)
    today = now.date()

    # ---------- REST DAY ----------
    if is_rest_day(today):
        if (
            now.hour == REST_HOUR
            and REST_MINUTE <= now.minute <= REST_MINUTE + 1
            and last_rest_sent_on != today
        ):
            msg = random.choice(REST_MESSAGES)
            for uid in USER_IDS:
                try:
                    user = await bot.fetch_user(uid)
                    await user.send(msg)
                except Exception as e:
                    print(f"DM failed {uid}: {e}")

            last_rest_sent_on = today
            print("✅ Rest message sent")

        return

    # ---------- WORKOUT DAY ----------
    for hour, minute in WORKOUT_TIMES:
        key = (today, hour, minute)
        if (
            now.hour == hour
            and minute <= now.minute <= minute + 1
            and key not in last_workout_sent
        ):
            msg = get_daily_message()
            for uid in USER_IDS:
                try:
                    user = await bot.fetch_user(uid)
                    await user.send(msg)
                except Exception as e:
                    print(f"DM failed {uid}: {e}")

            last_workout_sent.add(key)
            print(f"✅ Workout message sent at {hour}:{minute}")

# ================= EVENTS =================

@bot.event
async def on_ready():
    scheduler.start()
    print("🤖 bot online")

# ================= RUN =================

bot.run(TOKEN)


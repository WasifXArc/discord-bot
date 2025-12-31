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

# TODAY is a rest day
LAST_REST_DATE = datetime.date(2025, 12, 28)

REST_HOUR = 19  # 4 PM
REST_MINUTE = 50

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
    "Move your body today.",
    "Today is for training.",
    "Just complete the session.",
    "Do the minimum, but do it.",
    "Train, then continue your day.",
    "Get the session done today.",
    "No excuses. Just movement.",
    "Keep the habit alive today.",
    "Stay consistent today.",
    "One session keeps momentum.",
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

# ================= BOT =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HELPERS =================

def is_rest_day(today):
    days_since_rest = (today - LAST_REST_DATE).days
    return days_since_rest % 7 == 0

def get_daily_message():
    global used_messages

    if len(used_messages) == len(MESSAGES):
        used_messages = []

    remaining = [m for m in MESSAGES if m not in used_messages]
    msg = random.choice(remaining)
    used_messages.append(msg)
    return msg

# ================= TASKS =================

@tasks.loop(minutes=1)
async def scheduler():
    global last_rest_sent_on

    now = datetime.datetime.now(PK_TZ)
    today = now.date()

    # ---- REST DAY LOGIC ----
    if is_rest_day(today):
        if (
            now.hour == REST_HOUR
            and now.minute == REST_MINUTE
            and last_rest_sent_on != today
        ):
            message = random.choice(REST_MESSAGES)

            for uid in USER_IDS:
                try:
                    user = await bot.fetch_user(uid)
                    await user.send(message)
                except Exception as e:
                    print(f"Failed to DM {uid}: {e}")

            last_rest_sent_on = today
            print("Rest message sent")

        return  # skip workouts on rest day

    # ---- WORKOUT LOGIC ----
    if now.hour in (16, 22) and now.minute == 30:
        message = get_daily_message()

        for uid in USER_IDS:
            try:
                user = await bot.fetch_user(uid)
                await user.send(message)
            except Exception as e:
                print(f"Failed to DM {uid}: {e}")


# ================= EVENTS =================

@bot.event
async def on_ready():
    scheduler.start()
    print("bot online")

# ================= RUN =================

bot.run(TOKEN)




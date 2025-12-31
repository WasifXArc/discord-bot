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

# Change this to the day AFTER your last rest day
START_DATE = datetime.date(2025, 12, 29)

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
    "Progress comes from today.",
    "Your future self expects today’s work.",
    "No thinking. Just train.",
    "Do today’s work quietly.",
    "Show up even if it’s light.",
    "Today’s effort counts.",
    "Consistency over intensity.",
    "Do today’s movement.",
    "Train and log it.",
    "Make today count.",
    "Just start the workout.",
    "Finish today’s session.",
    "Small effort today.",
    "Movement first. Everything else later.",
    "Do the work you promised.",
    "Complete today’s task.",
    "Discipline shows up today.",
    "No need to overdo it.",
    "Just don’t skip today.",
    "One step forward today.",
    "Keep moving forward.",
    "Your routine needs today.",
    "Stay on track today.",
    "Train without drama.",
    "Do today’s reps.",
    "Keep it simple today.",
    "Today is not a rest day.",
    "Put the work in today.",
    "Just be consistent.",
    "Do the basics today.",
    "Progress is built today.",
    "Show discipline today.",
    "Train and move on.",
    "No motivation needed today.",
    "Today is about action.",
    "Do the session.",
    "Honor today’s plan.",
    "Complete the workout.",
    "Move. That’s enough.",
    "Stay committed today.",
    "Keep the chain unbroken.",
]

REST_MESSAGES = [
    "Rest today. You’ve earned it.",
    "No workout today. Recover well.",
    "Today is for rest and recovery.",
    "You’ve worked hard. Take today off.",
    "Rest day. Come back stronger tomorrow.",
]

used_messages = []

# ================= BOT SETUP =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HELPERS =================

def get_day_number():
    today = datetime.date.today()
    return (today - START_DATE).days + 1

def get_daily_message():
    global used_messages

    if len(used_messages) == len(MESSAGES):
        used_messages = []

    remaining = [m for m in MESSAGES if m not in used_messages]
    message = random.choice(remaining)
    used_messages.append(message)
    return message

# ================= TASKS =================

# Workout messages (twice daily)
@tasks.loop(
    time=[
        datetime.time(hour=16, minute=40, tzinfo=datetime.timezone(datetime.timedelta(hours=5))),
        datetime.time(hour=22, minute=30, tzinfo=datetime.timezone(datetime.timedelta(hours=5))),
    ]
)
async def daily_dm():
    day = get_day_number()

    # Skip rest day
    if day % 7 == 0:
        return

    message = get_daily_message()

    for uid in USER_IDS:
        try:
            user = await bot.fetch_user(uid)
            await user.send(message)
        except Exception as e:
            print(f"Failed to DM {uid}: {e}")

# Rest day message (ONCE at 4:00 PM)
@tasks.loop(
    time=datetime.time(
        hour=18,
        minute=39,
        tzinfo=datetime.timezone(datetime.timedelta(hours=5))
    )
)
async def rest_day_dm():
    day = get_day_number()

    if day % 7 != 0:
        return

    message = random.choice(REST_MESSAGES)

    for uid in USER_IDS:
        try:
            user = await bot.fetch_user(uid)
            await user.send(message)
        except Exception as e:
            print(f"Failed to DM {uid}: {e}")

# ================= EVENTS =================

@bot.event
async def on_ready():
    daily_dm.start()
    rest_day_dm.start()
    print("bot online")

# ================= RUN =================

bot.run(TOKEN)

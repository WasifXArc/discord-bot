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

# Program start date - calculated so Dec 31, 2025 is Day 7 (first rest day)
# Dec 31 is Day 7, so Day 1 was Dec 25, 2025
PROGRAM_START = datetime.date(2025, 12, 25)

REST_HOUR = 16  # 4 PM
REST_MINUTE = 0

WORKOUT_HOURS = [16, 22]  # 4 PM and 10 PM
WORKOUT_MINUTE = 30

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
    "Rest today. You've earned it.",
    "No workout today. Recover well.",
    "Today is for rest and recovery.",
    "You've worked hard. Take today off.",
    "Rest day. Come back stronger tomorrow.",
]

used_messages = []
last_message_sent_on = None
last_rest_sent_on = None

# ================= BOT =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= HELPERS =================

def get_program_day(today):
    """Calculate which day of the program we're on"""
    # Day 1 = Dec 24, Day 2 = Dec 25, etc.
    days_since_start = (today - PROGRAM_START).days
    # If before start date, treat as day 1
    if days_since_start < 0:
        return 1
    return days_since_start + 1

def is_rest_day(today):
    """Every 7th day is a rest day (7, 14, 21, 28, etc.)"""
    day_num = get_program_day(today)
    return day_num % 7 == 0

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
    global last_message_sent_on, last_rest_sent_on

    now = datetime.datetime.now(PK_TZ)
    today = now.date()
    current_hour = now.hour
    current_minute = now.minute

    day_num = get_program_day(today)
    is_rest = is_rest_day(today)

    print(f"[DEBUG] Day {day_num}, Rest: {is_rest}, Time: {current_hour}:{current_minute:02d}")

    # ---- REST DAY LOGIC ----
    if is_rest:
        if (
            current_hour == REST_HOUR
            and current_minute == REST_MINUTE
            and last_rest_sent_on != today
        ):
            message = random.choice(REST_MESSAGES)

            for uid in USER_IDS:
                try:
                    user = await bot.fetch_user(uid)
                    await user.send(message)
                    print(f"✓ Rest message sent to {uid}")
                except Exception as e:
                    print(f"✗ Failed to DM {uid}: {e}")

            last_rest_sent_on = today
            print(f"Rest message sent for Day {day_num}")

        return  # Skip workout messages on rest days

    # ---- WORKOUT LOGIC (non-rest days only) ----
    if (
        current_hour in WORKOUT_HOURS
        and current_minute == WORKOUT_MINUTE
        and last_message_sent_on != (today, current_hour)
    ):
        message = get_daily_message()

        for uid in USER_IDS:
            try:
                user = await bot.fetch_user(uid)
                await user.send(message)
                print(f"✓ Workout message sent to {uid}")
            except Exception as e:
                print(f"✗ Failed to DM {uid}: {e}")

        last_message_sent_on = (today, current_hour)
        print(f"Workout message sent for Day {day_num} at {current_hour}:00")

# ================= EVENTS =================

@bot.event
async def on_ready():
    scheduler.start()
    today = datetime.datetime.now(PK_TZ).date()
    day_num = get_program_day(today)
    is_rest = is_rest_day(today)
    print(f"🤖 Bot online | Day {day_num} {'(REST)' if is_rest else '(WORKOUT)'}")

# ================= RUN =================

bot.run(TOKEN)

import discord
from discord.ext import tasks, commands
import datetime
import os

# ========== CONFIG ==========
TOKEN = os.getenv("DISCORD_TOKEN")

USER_IDS = [
    1346102480785768620,
    954962586141597779,
]

PK_TZ = datetime.timezone(datetime.timedelta(hours=5))

SEND_HOUR = 23     # ← change time here
SEND_MINUTE = 47  # ← change time here

MESSAGE = "Do Todays' Workout Dumbass, One Rest Day Wasn't Enough??"

sent_today = None

# ========== BOT ==========
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ========== TASK ==========
@tasks.loop(seconds=30)
async def send_message():
    global sent_today

    now = datetime.datetime.now(PK_TZ)
    today = now.date()

    if (
        now.hour == SEND_HOUR
        and SEND_MINUTE <= now.minute <= SEND_MINUTE + 1
        and sent_today != today
    ):
        for uid in USER_IDS:
            try:
                user = await bot.fetch_user(uid)
                await user.send(MESSAGE)
            except Exception as e:
                print(f"DM failed {uid}: {e}")

        sent_today = today
        print("✅ Message sent")

# ========== EVENTS ==========
@bot.event
async def on_ready():
    send_message.start()
    print("🤖 bot online")

# ========== RUN ==========
bot.run(TOKEN)


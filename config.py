import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Kanal username "@kanal_nomi" yoki -100... ko'rinishidagi ID bo'lishi mumkin
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Kanalga o'tish uchun havola (foydalanuvchiga ko'rsatiladigan tugma uchun)
CHANNEL_URL = os.getenv("CHANNEL_URL", "")

# Admin telegram ID'lari, vergul bilan ajratilgan: "111111,222222"
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

DB_PATH = os.getenv("DB_PATH", "bot.db")

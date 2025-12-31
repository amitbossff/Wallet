import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render ENV
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

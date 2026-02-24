import os
import asyncio
import pytz
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask, jsonify
from threading import Thread

# --- CẤU HÌNH ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_ID = 1759212113 
MESSAGE = "/diemdanhapple"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
timezone = pytz.timezone("Asia/Ho_Chi_Minh")

# --- LOGIC GỬI TIN NHẮN ---
async def send_message():
    try:
        if not client.is_connected():
            await client.connect()
        await client.send_message(TARGET_ID, MESSAGE)
        print(f"--- [OK] Da gui '{MESSAGE}' toi {TARGET_ID} ---")
    except Exception as e:
        print(f"--- [ERROR] {e} ---")

# --- LAP LICH 07:00 AM VN ---
scheduler = AsyncIOScheduler(timezone=timezone)
scheduler.add_job(send_message, 'cron', hour=7, minute=0)

# --- WEB SERVER DE PING ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Active"

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"}), 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start_bot():
    await client.start()
    if not scheduler.running:
        scheduler.start()
    print("UserBot is running 24/7...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        pass

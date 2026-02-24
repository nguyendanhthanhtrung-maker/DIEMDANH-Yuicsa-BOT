import os
import asyncio
import pytz
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask, jsonify
from threading import Thread

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_USER = "@apple_bot" 

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
timezone = pytz.timezone("Asia/Ho_Chi_Minh")

async def send_message():
    try:
        if not client.is_connected():
            await client.connect()
        await client.send_message(TARGET_USER, "/diemdanhapple")
        print("Sent /diemdanhapple at 07:00 AM VN")
    except Exception as e:
        print(f"Error: {e}")

scheduler = AsyncIOScheduler(timezone=timezone)
scheduler.add_job(send_message, 'cron', hour=7, minute=0)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"}), 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def start_bot():
    await client.start()
    scheduler.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    asyncio.run(start_bot())

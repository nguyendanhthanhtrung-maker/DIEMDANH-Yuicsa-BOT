import os
import asyncio
import threading
from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- CẤU HÌNH BIẾN MÔI TRƯỜNG ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
TARGET_ID = int(os.getenv("TARGET_ID", 1759212113))
MESSAGE = "/diemdanhapple"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# --- WEB SERVER (GIỮ BOT THỨC) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "UserBot is Running 24/7", 200

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"}), 200

def run_web():
    # Render yêu cầu dùng port từ biến môi trường PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- CHỨC NĂNG CHÍNH ---
async def send_task():
    """Hàm gửi tin nhắn có xử lý lỗi tránh crash bot"""
    try:
        # Kiểm tra kết nối trước khi gửi
        if not client.is_connected():
            await client.connect()
        
        await client.send_message(TARGET_ID, MESSAGE)
        print(f"--- [SUCCESS] Đã gửi '{MESSAGE}' đến {TARGET_ID} ---")
    except Exception as e:
        print(f"--- [ERROR] Gửi tin nhắn thất bại: {e} ---")

async def main():
    print("--- Đang khởi động UserBot ---")
    try:
        await client.start()
        print("--- Đăng nhập thành công! ---")

        # 1. Gửi tin nhắn ngay lập tức khi vừa khởi động
        await send_task()

        # 2. Thiết lập lịch trình gửi mỗi 2 giờ một lần
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_task, 'interval', hours=2)
        scheduler.start()
        print("--- Đã kích hoạt Scheduler: Lặp lại mỗi 2 giờ ---")

        # Giữ script chạy vô tận
        await client.run_until_disconnected()
    except Exception as e:
        print(f"--- [CRITICAL] Lỗi khởi động: {e} ---")

if __name__ == "__main__":
    # Chạy Web Server trên luồng phụ để không chặn AsyncIO
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()

    # Chạy vòng lặp sự kiện chính của Bot
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("--- Bot đã dừng ---")

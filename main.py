import os
import asyncio
from telethon import TelegramClient
from flask import Flask
from threading import Thread

# Cấu hình thông số
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING") # Chuỗi phiên đăng nhập
TARGET_USER = "tên_người_nhận_hoặc_bot" # Ví dụ: @apple_bot

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Hàm gửi tin nhắn mỗi 24 giờ
async def send_message_daily():
    await client.start()
    while True:
        try:
            await client.send_message(TARGET_USER, "/diemdanhapple")
            print("Đã gửi tin nhắn điểm danh!")
        except Exception as e:
            print(f"Lỗi: {e}")
        
        # Đợi 24 giờ (86400 giây)
        await asyncio.sleep(86400)

# Tạo Web Server để Render chấp nhận Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang chạy..."

def run_web():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # Chạy Web server ở luồng riêng
    Thread(target=run_web).start()
    
    # Chạy vòng lặp Telegram
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message_daily())

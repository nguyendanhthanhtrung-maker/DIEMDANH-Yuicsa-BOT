import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- CẤU HÌNH TỪ BIẾN MÔI TRƯỜNG ---
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("SESSION_STR")
PORT = int(os.environ.get("PORT", 8080))

# Thông tin theo yêu cầu
TARGET_ID = 1759212113
COMMAND_TEXT = "/diemdanhapple"
INTERVAL = 2 * 60 * 60  # 2 giờ

app = Flask(__name__)

# --- TRANG PING ---
@app.route('/ping')
def ping():
    return "PONG! Userbot is active.", 200

@app.route('/')
def home():
    return "Userbot is running. Monitor via /ping", 200

async def run_userbot():
    if not all([API_ID, API_HASH, SESSION_STR]):
        print("LỖI: Thiếu biến môi trường API_ID, API_HASH hoặc SESSION_STR!")
        return

    client = TelegramClient(StringSession(SESSION_STR), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("LỖI: SESSION_STR không hợp lệ!")
            return

        print(f"Userbot ONLINE. Mục tiêu: {TARGET_ID}")

        while True:
            try:
                # Gửi tin nhắn ngay lập tức
                await client.send_message(TARGET_ID, COMMAND_TEXT)
                print(f"Đã gửi '{COMMAND_TEXT}' thành công.")
                
                # Sau khi gửi xong mới bắt đầu đợi 2 tiếng
                print(f"Đang đợi 2 tiếng cho lần gửi tiếp theo...")
                await asyncio.sleep(INTERVAL)
                
            except Exception as e:
                print(f"Lỗi khi gửi: {e}")
                await asyncio.sleep(60) # Nếu lỗi (như mạng yếu) thì đợi 1 phút rồi thử lại ngay
            
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

def start_web_server():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    # Chạy Flask Web Server để Render không tắt service
    threading.Thread(target=start_web_server, daemon=True).start()
    
    # Chạy Userbot
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_userbot())

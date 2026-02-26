import os
import asyncio
import threading
import sys
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- KHỞI TẠO FLASK ---
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "PONG", 200

@app.route('/')
def home():
    return "Bot is running", 200

def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- LOGIC USERBOT ---
async def run_userbot():
    print("--- ĐANG KHỞI CHẠY USERBOT ---")
    
    # Lấy biến môi trường và kiểm tra trực tiếp
    api_id_env = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    session_str = os.environ.get("SESSION_STR")
    
    if not all([api_id_env, api_hash, session_str]):
        print("LỖI: Thiếu biến môi trường (API_ID, API_HASH, hoặc SESSION_STR)!")
        sys.exit(1) # Thoát để Render báo lỗi rõ ràng

    try:
        api_id = int(api_id_env)
        target_id = 1759212113
        message_text = "/diemdanhapple"
        
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
        
        await client.connect()
        if not await client.is_user_authorized():
            print("LỖI: SESSION_STR không hợp lệ hoặc đã hết hạn!")
            return

        print(f"KẾT NỐI THÀNH CÔNG! Đang gửi tin cho {target_id}...")

        while True:
            try:
                # Gửi tin nhắn ngay lập tức khi bắt đầu vòng lặp
                await client.send_message(target_id, message_text)
                print(f"Đã gửi: {message_text} tới {target_id}")
            except Exception as e:
                print(f"Lỗi gửi tin: {e}")

            # Nghỉ 2 tiếng (7200 giây)
            print("Đang nghỉ 2 tiếng...")
            await asyncio.sleep(7200)

    except Exception as e:
        print(f"LỖI HỆ THỐNG: {e}")
        sys.exit(1)

# --- ĐIỂM KHỞI CHẠY CHÍNH ---
if __name__ == "__main__":
    # 1. Chạy Web Server trong luồng riêng
    print("Đang khởi động Web Server...")
    threading.Thread(target=start_web_server, daemon=True).start()
    
    # 2. Xử lý Event Loop cho Userbot
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_userbot())
    except Exception as e:
        print(f"Lỗi vòng lặp chính: {e}")
        sys.exit(1)

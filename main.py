import os
import asyncio
import logging
import time
from fastapi import FastAPI
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Config ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STR = os.environ.get("SESSION_STR", "")
TARGET_ID = 1759212113
MESSAGE = "/diemdanhapple"

app = FastAPI()
status_bot = {"last_sent": "Chưa gửi", "count": 0}

# Khởi tạo client dùng chung để tránh tạo nhiều kết nối
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)

async def send_telegram_msg():
    """Hàm lõi để thực hiện gửi tin nhắn"""
    try:
        if not client.is_connected():
            await client.connect()
        
        await client.send_message(TARGET_ID, MESSAGE)
        status_bot["count"] += 1
        status_bot["last_sent"] = time.strftime('%H:%M:%S %d-%m-%Y')
        logger.info(f"✅ Đã gửi tin nhắn thành công (Lần {status_bot['count']})")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi gửi tin: {e}")
        return False

@app.get("/")
async def root():
    return {
        "status": "Online ✅",
        "info": "Truy cập /diemdanhapple để gửi tin nhắn ngay lập tức",
        "last_sent": status_bot["last_sent"],
        "total_sent": status_bot["count"]
    }

# --- Route mới theo yêu cầu của bạn ---
@app.get("/diemdanhapple")
async def manual_trigger():
    success = await send_telegram_msg()
    if success:
        return {
            "message": "Đã gửi lệnh diemdanh thành công!",
            "time": status_bot["last_sent"],
            "total": status_bot["count"]
        }
    else:
        return {"message": "Gửi thất bại, vui lòng kiểm tra Log trên Render hoặc Session."}

@app.on_event("startup")
async def startup_event():
    # Kết nối sẵn khi server vừa bật
    await client.connect()
    logger.info("📡 Bot đã sẵn sàng nhận lệnh từ trình duyệt.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import os
import asyncio
import logging
import time
from fastapi import FastAPI
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Cấu hình Biến môi trường ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STR = os.environ.get("SESSION_STR", "")
# Thay đổi Target sang Username
TARGET_USERNAME = "Yuicsa_bot" 
MESSAGE = "/diemdanhapple"

app = FastAPI()
status_bot = {"last_sent": "Chưa gửi", "count": 0}

# Khai báo client nhưng không khởi tạo ngay để tránh lỗi Loop 
client = None

async def get_client():
    """Khởi tạo client bên trong Event Loop của FastAPI"""
    global client
    if client is None:
        client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
        await client.connect()
    return client

async def send_telegram_msg():
    """Hàm gửi tin nhắn tới Username"""
    try:
        bot_client = await get_client()
        
        if not await bot_client.is_user_authorized():
            logger.error("❌ SESSION_STR không hợp lệ!")
            return False
            
        # Telethon hỗ trợ gửi trực tiếp qua Username 
        await bot_client.send_message(TARGET_USERNAME, MESSAGE)
        
        status_bot["count"] += 1
        status_bot["last_sent"] = time.strftime('%H:%M:%S %d-%m-%Y')
        logger.info(f"✅ Đã gửi tới @{TARGET_USERNAME} (Lần {status_bot['count']})")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi khi gửi cho @{TARGET_USERNAME}: {e}")
        return False

@app.get("/")
async def root():
    return {
        "status": "Online ✅",
        "target": f"@{TARGET_USERNAME}",
        "last_sent": status_bot["last_sent"],
        "total_sent": status_bot["count"],
        "action": "Truy cập /diemdanhapple để gửi tin"
    }

@app.get("/diemdanhapple")
async def manual_trigger():
    success = await send_telegram_msg()
    if success:
        return {
            "status": "Success",
            "sent_to": f"@{TARGET_USERNAME}",
            "time": status_bot["last_sent"]
        }
    return {"status": "Failed", "detail": "Kiểm tra log trên Render"}

@app.on_event("startup")
async def startup_event():
    # Kết nối khi server khởi động để sẵn sàng nhận request
    await get_client()
    logger.info(f"📡 Bot đã kết nối và sẵn sàng gửi tin tới @{TARGET_USERNAME}")

if __name__ == "__main__":
    import uvicorn
    # Bind vào port của Render 
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

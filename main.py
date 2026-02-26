import os
import asyncio
import logging
import time
from fastapi import FastAPI
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Cấu hình Biến môi trường ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STR = os.environ.get("SESSION_STR", "")
TARGET_USERNAME = "Yuicsa_bot" 
MESSAGE = "/diemdanhapple"

app = FastAPI()
status_bot = {"last_sent": "Chưa gửi", "count": 0}

# Khởi tạo client rỗng
client = None

async def get_client():
    """Khởi tạo/Kết nối client khi cần thiết"""
    global client
    if client is None:
        client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    
    if not client.is_connected():
        await client.connect()
    return client

@app.get("/")
async def root():
    # Trang chủ chỉ hiển thị trạng thái, KHÔNG gửi tin nhắn
    return {
        "status": "Online ✅",
        "info": "Bot đang chờ lệnh. Truy cập /diemdanhapple để gửi tin.",
        "last_sent": status_bot["last_sent"],
        "total_sent": status_bot["count"]
    }

@app.get("/health")
async def health():
    # Endpoint dùng để ping giữ server sống, KHÔNG gửi tin nhắn
    return {"status": "alive"}

@app.get("/diemdanhapple")
async def manual_trigger():
    """Chỉ khi truy cập vào đây, tin nhắn mới được gửi đi"""
    try:
        bot_client = await get_client()
        
        if not await bot_client.is_user_authorized():
            return {"status": "Error", "message": "Session không hợp lệ!"}
            
        # Thực hiện gửi tin nhắn
        await bot_client.send_message(TARGET_USERNAME, MESSAGE)
        
        # Cập nhật trạng thái
        status_bot["count"] += 1
        status_bot["last_sent"] = time.strftime('%H:%M:%S %d-%m-%Y')
        
        logger.info(f"🚀 Đã gửi lệnh tới @{TARGET_USERNAME}")
        
        return {
            "status": "Success",
            "message": f"Đã gửi '{MESSAGE}' tới @{TARGET_USERNAME}",
            "time": status_bot["last_sent"]
        }
    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        return {"status": "Failed", "detail": str(e)}

@app.on_event("startup")
async def startup_event():
    # Chỉ thông báo server đã sẵn sàng, không thực hiện gửi tin ở đây
    logger.info("📡 Server đã khởi động. Sẵn sàng nhận lệnh tại /diemdanhapple")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

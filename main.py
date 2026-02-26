import os
import asyncio
import logging
import time
from fastapi import FastAPI
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# --- Cấu hình Logging (Xem log trên Render) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Cấu hình Biến môi trường ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STR = os.environ.get("SESSION_STR", "") # StringSession để Render không xóa file
TARGET_ID = 1759212113
MESSAGE = "/diemdanhapple"
INTERVAL = 7200  # 2 tiếng (7200 giây)

# --- Khởi tạo FastAPI ---
app = FastAPI(title="Telegram Auto Check-in")

# Biến toàn cục để theo dõi trạng thái
status_bot = {"is_running": False, "last_sent": "Chưa gửi", "count": 0}

@app.get("/")
async def root():
    return {
        "status": "Online ✅",
        "bot_running": status_bot["is_running"],
        "last_sent": status_bot["last_sent"],
        "total_sent": status_bot["count"],
        "interval": "2 hours"
    }

@app.get("/ping")
async def ping():
    return {"message": "PONG"}

# --- Logic Telegram Userbot ---
async def start_userbot():
    if status_bot["is_running"]:
        return

    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            logger.error("❌ SESSION_STR không hợp lệ! Vui lòng kiểm tra lại.")
            return

        status_bot["is_running"] = True
        logger.info("✅ Userbot đã kết nối thành công!")

        while True:
            try:
                # Gửi tin nhắn ngay lập tức
                await client.send_message(TARGET_ID, MESSAGE)
                
                status_bot["count"] += 1
                status_bot["last_sent"] = time.strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"🚀 [Lần {status_bot['count']}] Đã gửi '{MESSAGE}' tới {TARGET_ID}")

                # Nghỉ 2 tiếng
                await asyncio.sleep(INTERVAL)

            except FloodWaitError as e:
                logger.warning(f"⚠️ Telegram yêu cầu chờ {e.seconds}s")
                await asyncio.sleep(e.seconds + 10)
            except Exception as e:
                logger.error(f"❌ Lỗi gửi tin: {e}")
                await asyncio.sleep(60) # Gặp lỗi thì chờ 1 phút rồi thử lại vòng lặp

    except Exception as e:
        logger.critical(f"💥 Lỗi hệ thống: {e}")
    finally:
        status_bot["is_running"] = False
        await client.disconnect()

# --- Tự động chạy Bot khi Server khởi động ---
@app.on_event("startup")
async def startup_event():
    # Chạy vòng lặp bot trong background task của asyncio
    asyncio.create_task(start_userbot())
    logger.info("📡 Background Task cho Userbot đã được khởi tạo.")

if __name__ == "__main__":
    import uvicorn
    # Render cung cấp cổng qua biến PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

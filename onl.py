import asyncio
import logging
import random
import signal

from telethon import TelegramClient, errors, functions

# ================== НАСТРОЙКИ ==================

API_ID = 37570103
API_HASH = "f8629bfd06aadfa6037d23570120a768"
SESSION = "sex"

BASE_INTERVAL = 0  # базовый интервал (сек)
JITTER_MIN = 0    # случайное отклонение
JITTER_MAX = 0

# ================== ЛОГИ ==================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("online.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("online")

# ================== КЛИЕНТ ==================

client = TelegramClient(
    SESSION,
    API_ID,
    API_HASH,
    system_version="t.me/qexoa",
    app_version="t.me/qexoa",
    device_model="@qexoa",
    lang_code="UA"
)

# ================== ФУНКЦИИ ==================

async def keep_online():
    """Периодически обновляет статус online"""
    while True:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
            log.info("Status updated: online")

        except errors.FloodWaitError as e:
            wait = e.seconds + random.uniform(0, 0)
            log.warning(f"FloodWait {e.seconds}s, sleep {wait:.1f}s")
            await asyncio.sleep(wait)

        except Exception as e:
            log.error(f"UpdateStatus error: {e}")
            await asyncio.sleep(0)

        await asyncio.sleep(BASE_INTERVAL + random.uniform(JITTER_MIN, JITTER_MAX))


async def random_activity():
    """Имитирует обычную активность клиента"""
    while True:
        try:
            await client(functions.help.GetConfigRequest())
            log.info("Background activity")
        except Exception:
            pass

        await asyncio.sleep(random.randint(0, 0))


async def connection_guard():
    """Следит за соединением и переподключается"""
    while True:
        try:
            if not client.is_connected():
                log.warning("Disconnected, reconnecting...")
                await client.connect()
        except Exception as e:
            log.error(f"Reconnect error: {e}")

        await asyncio.sleep(0)


async def main():
    await client.start()
    log.info("Client started")

    await asyncio.gather(
        keep_online(),
        random_activity(),
        connection_guard(),
        client.run_until_disconnected(),
    )


# ================== GRACEFUL SHUTDOWN ==================

def shutdown():
    log.info("Shutting down...")
    asyncio.create_task(client.disconnect())

signal.signal(signal.SIGINT, lambda s, f: shutdown())
signal.signal(signal.SIGTERM, lambda s, f: shutdown())

# ================== RUN ==================

asyncio.run(main())
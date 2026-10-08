import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import load_settings
from app.db import Database
from app.handlers import admin, errors, inline
from app.services.kinopoisk import KinopoiskAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def main() -> None:
    settings = load_settings()
    db = Database(settings.database_url)
    kinopoisk = KinopoiskAPI(
        settings.kinopoisk_api_key,
        settings.kinopoisk_api_url,
    )

    await db.connect()
    await kinopoisk.start()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp["settings"] = settings
    dp["db"] = db
    dp["kinopoisk"] = kinopoisk

    dp.include_router(errors.router)
    dp.include_router(admin.router)
    dp.include_router(inline.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Starting Kinopoisk inline bot")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await kinopoisk.close()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

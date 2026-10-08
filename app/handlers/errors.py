import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from app.config import Settings

router = Router(name="errors")
logger = logging.getLogger(__name__)


@router.error()
async def global_error_handler(event: ErrorEvent, settings: Settings) -> bool:
    exception = event.exception
    logger.exception("Unhandled bot error", exc_info=exception)

    text = (
        "🚨 <b>BOT XATOLIGI</b>

"
        f"<b>Xato:</b> <code>{type(exception).__name__}</code>
"
        f"<b>Izoh:</b> <code>{str(exception)[:1200]}</code>

"
        f"<b>Update:</b> <code>{type(event.update).__name__}</code>"
    )

    try:
        await event.bot.send_message(settings.admin_id, text)
    except Exception:
        logger.exception("Could not send error notification to admin")

    return True

import logging
from html import escape

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.config import Settings
from app.db import Database
from app.services.kinopoisk import KinopoiskAPI

router = Router(name="inline")
logger = logging.getLogger(__name__)


@router.inline_query()
async def inline_search(
    inline_query: InlineQuery,
    settings: Settings,
    db: Database,
    kinopoisk: KinopoiskAPI,
) -> None:
    user_id = inline_query.from_user.id
    query = (inline_query.query or "").strip()

    if user_id != settings.admin_id and not await db.is_authorized(user_id):
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="access-denied",
                    title="⛔ Ruxsat berilmagan",
                    description="Admin ruxsati kerak.",
                    input_message_content=InputTextMessageContent(
                        message_text="⛔ Sizga bu botdan foydalanish uchun ruxsat berilmagan."
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    if not query:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="empty-query",
                    title="🔎 Kino nomini yozing",
                    description="Masalan: Interstellar",
                    input_message_content=InputTextMessageContent(
                        message_text="🔎 Kino nomini yozib qidiring."
                    ),
                )
            ],
            cache_time=1,
            is_personal=True,
        )
        return

    try:
        films = await kinopoisk.search(query, settings.max_results)
    except Exception:
        logger.exception("Kinopoisk API search failed for query=%r", query)
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="api-error",
                    title="⚠️ Qidiruvda xatolik",
                    description="Bir ozdan keyin qayta urinib ko‘ring.",
                    input_message_content=InputTextMessageContent(
                        message_text="⚠️ Kinopoisk qidiruvida xatolik yuz berdi."
                    ),
                )
            ],
            cache_time=0,
            is_personal=True,
        )
        raise

    if not films:
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id="not-found",
                    title="🔎 Hech narsa topilmadi",
                    description=f"“{escape(query)}” bo‘yicha natija yo‘q.",
                    input_message_content=InputTextMessageContent(
                        message_text=f"🔎 “{query}” bo‘yicha Kinopoiskdan natija topilmadi."
                    ),
                )
            ],
            cache_time=3,
            is_personal=True,
        )
        return

    results = []
    for film in films:
        results.append(
            InlineQueryResultArticle(
                id=str(film.film_id),
                title=film.title[:64],
                description=f"{film.kind} • {film.year} • ⭐ {film.rating}"[:256],
                input_message_content=InputTextMessageContent(message_text=film.url),
                thumbnail_url=film.poster_url,
            )
        )

    await inline_query.answer(
        results=results,
        cache_time=15,
        is_personal=True,
    )

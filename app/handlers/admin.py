from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.db import Database
from app.keyboards.admin import admin_menu, cancel_keyboard, confirm_delete, users_keyboard

router = Router(name="admin")


class AddUserStates(StatesGroup):
    waiting_for_user_id = State()


def is_admin(user_id: int, settings: Settings) -> bool:
    return user_id == settings.admin_id


@router.message(CommandStart(), F.chat.type == "private")
async def start_admin(message: Message, settings: Settings, db: Database) -> None:
    user_id = message.from_user.id

    if not is_admin(user_id, settings):
        if not await db.is_authorized(user_id):
            await message.answer("⛔ Sizga botdan foydalanish uchun ruxsat berilmagan.")
            return
        await message.answer(
            "✅ Sizga botdan foydalanish ruxsati berilgan.\n\n"
            "Inline rejimda: <code>@bot_username kino nomi</code>"
        )
        return

    await message.answer(
        "🎬 <b>Kinopoisk Bot</b>\n\n👑 <b>Admin panel</b>",
        reply_markup=admin_menu(),
    )


@router.callback_query(F.data == "admin:panel")
async def panel(callback: CallbackQuery, settings: Settings) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    await callback.message.edit_text(
        "🎬 <b>Kinopoisk Bot</b>\n\n👑 <b>Admin panel</b>",
        reply_markup=admin_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:add_user")
async def add_user_start(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    await state.set_state(AddUserStates.waiting_for_user_id)
    await callback.message.edit_text(
        "👤 <b>Foydalanuvchi ID raqamini yuboring:</b>",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.message(AddUserStates.waiting_for_user_id)
async def add_user_finish(
    message: Message,
    state: FSMContext,
    settings: Settings,
    db: Database,
) -> None:
    if not is_admin(message.from_user.id, settings):
        return

    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(
            "⚠️ Faqat Telegram User ID raqamini yuboring.",
            reply_markup=cancel_keyboard(),
        )
        return

    user_id = int(raw)
    if user_id == settings.admin_id:
        await state.clear()
        await message.answer("ℹ️ Bu ID allaqachon admin.", reply_markup=admin_menu())
        return

    added = await db.add_user(user_id)
    await state.clear()
    if added:
        await message.answer(
            f"✅ <code>{user_id}</code> foydalanuvchiga ruxsat berildi.",
            reply_markup=admin_menu(),
        )
    else:
        await message.answer(
            f"ℹ️ <code>{user_id}</code> allaqachon ro‘yxatda.",
            reply_markup=admin_menu(),
        )


@router.callback_query(F.data == "admin:cancel")
async def add_user_cancel(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "🎬 <b>Kinopoisk Bot</b>\n\n👑 <b>Admin panel</b>",
        reply_markup=admin_menu(),
    )
    await callback.answer("Bekor qilindi")


async def render_users(callback: CallbackQuery, db: Database, offset: int) -> None:
    total = await db.count_users()
    if offset >= total and total:
        offset = max(0, ((total - 1) // 10) * 10)

    user_ids = await db.list_users(limit=10, offset=offset)

    if not user_ids:
        text = "👥 <b>Foydalanuvchilar</b>\n\nRo‘yxat bo‘sh."
    else:
        lines = [f"👥 <b>Foydalanuvchilar</b> — {total} ta", ""]
        lines.extend(
            f"{offset + i + 1}. <code>{uid}</code>"
            for i, uid in enumerate(user_ids)
        )
        lines.append("")
        lines.append("O‘chirish uchun foydalanuvchi tugmasini bosing.")
        text = "\n".join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=users_keyboard(user_ids, offset, total),
    )


@router.callback_query(F.data.startswith("admin:users:"))
async def list_users(callback: CallbackQuery, settings: Settings, db: Database) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    await render_users(callback, db, int(callback.data.rsplit(":", 1)[1]))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete:"))
async def delete_user_prompt(callback: CallbackQuery, settings: Settings) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    _, _, user_id, offset = callback.data.split(":")
    await callback.message.edit_text(
        f"⚠️ <b>{user_id}</b> foydalanuvchini ro‘yxatdan o‘chirasizmi?",
        reply_markup=confirm_delete(int(user_id), int(offset)),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete_yes:"))
async def delete_user_confirm(
    callback: CallbackQuery,
    settings: Settings,
    db: Database,
) -> None:
    if not is_admin(callback.from_user.id, settings):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return
    _, _, user_id, offset = callback.data.split(":")
    removed = await db.remove_user(int(user_id))
    await callback.answer("✅ O‘chirildi" if removed else "ℹ️ Topilmadi")
    await render_users(callback, db, int(offset))

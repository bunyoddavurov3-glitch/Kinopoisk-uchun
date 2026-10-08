from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Foydalanuvchi qo‘shish", callback_data="admin:add_user")
    builder.button(text="👥 Foydalanuvchilar", callback_data="admin:users:0")
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="admin:cancel")
    return builder.as_markup()


def users_keyboard(user_ids: list[int], offset: int, total: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user_id in user_ids:
        builder.button(
            text=f"❌ {user_id}",
            callback_data=f"admin:delete:{user_id}:{offset}",
        )
    builder.adjust(1)

    navigation = []
    if offset > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"admin:users:{max(0, offset - 10)}",
            )
        )
    navigation.append(
        InlineKeyboardButton(text="🏠 Panel", callback_data="admin:panel")
    )
    if offset + len(user_ids) < total:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"admin:users:{offset + 10}",
            )
        )
    builder.row(*navigation)
    return builder.as_markup()


def confirm_delete(user_id: int, offset: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha",
            callback_data=f"admin:delete_yes:{user_id}:{offset}",
        ),
        InlineKeyboardButton(
            text="↩️ Yo‘q",
            callback_data=f"admin:users:{offset}",
        ),
    )
    return builder.as_markup()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_URL
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import CHANNEL_URL

def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")],
        ]
    )


def get_demo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Demo darsni olish", callback_data="get_demo")]
        ]
    )


def admin_menu_keyboard(commands: list[tuple[str, str]]) -> ReplyKeyboardMarkup:
    """
    Admin uchun DOIMIY ko'rinib turadigan pastki tugmalar menyusi.
    `commands` — [(buyruq, tavsif), ...] ro'yxati (odatda
    handlers/admin.py dagi ADMIN_COMMANDS beriladi). Tugma bosilganda
    o'sha buyruq matn sifatida yuboriladi, xuddi qo'lda yozilgandek.
    """
    buttons = [KeyboardButton(text=f"/{cmd}") for cmd, _ in commands]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,  # boshqa (inline) tugmalar chiqsa ham yashirilmaydi
    )
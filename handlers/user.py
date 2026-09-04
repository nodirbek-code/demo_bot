import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from config import CHANNEL_ID
import database as db
import keyboards as kb
from handlers.admin import ADMIN_COMMANDS, is_admin as is_bot_admin
from keyboards import admin_menu_keyboard as build_admin_menu
router = Router()

ALLOWED_STATUSES = {"member", "administrator", "creator"}


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ALLOWED_STATUSES
    except TelegramBadRequest:
        # Bot kanalda admin emas yoki CHANNEL_ID noto'g'ri bo'lsa shu yerga tushadi
        return False


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    await db.upsert_user(
        message.from_user.id, message.from_user.full_name, message.from_user.username
    )

    if await is_subscribed(bot, message.from_user.id):
        await db.mark_subscribed(message.from_user.id, True)
        await message.answer(
            "Assalomu alaykum! 👋\n\nSiz kanalimizga allaqachon a'zosiz.\n"
            "Quyidagi tugma orqali bepul demo darsni olishingiz mumkin:",
            reply_markup=kb.get_demo_keyboard(),
        )
    else:
        await message.answer(
            "Assalomu alaykum! 👋\n\n"
            "Bepul demo darsni olish uchun avval bizning kanalimizga a'zo bo'ling, "
            "so'ngra \"✅ Tekshirish\" tugmasini bosing:",
            reply_markup=kb.subscribe_keyboard(),
        )
    if is_bot_admin(message.from_user.id):
        await message.answer(
            "🛠 Siz adminsiz — pastdagi menyu orqali buyruqlarga tez kirishingiz mumkin.",
            reply_markup=build_admin_menu(ADMIN_COMMANDS),
        )

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await db.mark_subscribed(callback.from_user.id, True)
        await callback.message.edit_text(
            "✅ Rahmat! Siz kanalga a'zo bo'ldingiz.\n\n"
            "Endi bepul demo darsni olishingiz mumkin:",
        )
        await callback.message.edit_reply_markup(reply_markup=kb.get_demo_keyboard())
    else:
        await callback.answer(
            "❌ Siz hali kanalga a'zo bo'lmagansiz. Iltimos, avval a'zo bo'ling.",
            show_alert=True,
        )


@router.callback_query(F.data == "get_demo")
async def send_demo(callback: CallbackQuery, bot: Bot):
    if not await is_subscribed(bot, callback.from_user.id):
        await callback.answer(
            "❌ Demo darsni olish uchun avval kanalga a'zo bo'ling.", show_alert=True
        )
        return

    materials = await db.get_active_demo_materials()
    if not materials:
        await callback.answer(
            "Hozircha demo dars yuklanmagan. Birozdan so'ng qayta urinib ko'ring.",
            show_alert=True,
        )
        return

    try:
        for m in materials:
            await bot.copy_message(
                chat_id=callback.from_user.id,
                from_chat_id=m["from_chat_id"],
                message_id=m["message_id"],
            )
            await asyncio.sleep(0.05)
        await db.mark_demo_received(callback.from_user.id)
        await callback.answer("Demo dars yuborildi! 🎉")
    except TelegramBadRequest:
        await callback.answer(
            "Demo darsni yuborishda xatolik yuz berdi. Adminga xabar bering.",
            show_alert=True,
        )

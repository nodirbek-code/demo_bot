import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import user, admin
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from config import BOT_TOKEN, ADMIN_IDS


async def set_bot_commands(bot: Bot):
    # Oddiy foydalanuvchilar uchun "/" menyusi
    await bot.set_my_commands(
        [BotCommand(command="start", description="Botni ishga tushirish")],
        scope=BotCommandScopeDefault(),
    )

    # Admin(lar) uchun — handlers/admin.py dagi ADMIN_COMMANDS asosida
    admin_commands = [
        BotCommand(command=cmd, description=desc) for cmd, desc in admin.ADMIN_COMMANDS
    ]
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(
                admin_commands, scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception:
            # Admin hali botga /start bosmagan bo'lishi mumkin
            pass


async def main():
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan")

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Admin routerini birinchi ulaymiz, aks holda oddiy foydalanuvchi
    # handlerlari ba'zi buyruqlarni ushlab qolishi mumkin
    dp.include_router(admin.router)
    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)   # <-- shu qator qo'shildi
    await dp.start_polling(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from config import ADMIN_IDS
import database as db
from keyboards import admin_menu_keyboard

router = Router()


# Barcha admin buyruqlari BITTA joyda — Telegram "/" menyusiga shu
# ro'yxat asosida o'rnatiladi (bot.py da set_admin_commands orqali) va
# /admin buyrug'i ham shu ro'yxatni matn ko'rinishida chiqaradi.
ADMIN_COMMANDS = [
    ("add_demo", "Javob berilgan xabarni demo darsga qo'shish"),
    ("clear_demo", "Demo darsdagi barcha materiallarni tozalash"),
    ("remove_demo", "Bitta materialni ID bo'yicha o'chirish"),
    ("demo_holati", "Joriy demo darsdagi materiallarni ko'rish"),
    ("toggle_demo", "Bitta materialni yoqish/o'chirish"),
    ("broadcast_demo", "Demo darsni barcha foydalanuvchilarga yuborish"),
    ("stats", "Foydalanuvchilar statistikasi"),
    ("admin", "Shu buyruqlar ro'yxatini ko'rsatish"),
]


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_help(message: Message):
    if not is_admin(message.from_user.id):
        return

    lines = "\n".join(f"/{cmd} — {desc}" for cmd, desc in ADMIN_COMMANDS)
    await message.answer(
        f"🛠 Admin buyruqlari:\n\n{lines}",
        reply_markup=admin_menu_keyboard(ADMIN_COMMANDS),
    )



def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _detect_media_type(msg: Message) -> str:
    if msg.video:
        return "🎬 video"
    if msg.audio:
        return "🎵 audio"
    if msg.voice:
        return "🎙 ovozli xabar"
    if msg.document:
        return "📄 fayl"
    if msg.photo:
        return "🖼 rasm"
    if msg.text:
        return "📝 matn"
    return "❔ boshqa"


@router.message(Command("add_demo"))
async def add_demo(message: Message):
    """
    Admin xohlagan xabarga (audio, video, fayl, rasm yoki matn) javob
    tariqasida /add_demo yozsa, o'sha xabar demo dars materiallar
    ro'yxatiga QO'SHILADI (eskilari o'chmaydi). Shu tufayli admin
    istalgan payt istalgan miqdorda audio/video/fayl qo'shib borishi
    mumkin — masalan avval video, keyin audio, keyin pdf faylni alohida
    xabarlarga javob qilib yuborsa, barchasi bitta demo dars sifatida
    foydalanuvchiga ketma-ket yuboriladi.
    """
    if not is_admin(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer(
            "Demo darsga material qo'shish uchun kerakli xabarga "
            "(audio, video, fayl, rasm yoki matn) javob tariqasida "
            "/add_demo buyrug'ini yuboring.\n\n"
            "Bir nechta material qo'shmoqchi bo'lsangiz, buni har bir "
            "xabar uchun alohida-alohida takrorlang."
        )
        return

    source = message.reply_to_message
    media_type = _detect_media_type(source)
    await db.add_demo_material(
        from_chat_id=source.chat.id,
        message_id=source.message_id,
        media_type=media_type,
    )
    materials = await db.get_demo_materials()
    await message.answer(
        f"✅ Qo'shildi: {media_type}\n"
        f"Hozirda demo darsda jami {len(materials)} ta material bor.\n\n"
        f"Yana qo'shish uchun shu buyruqni takrorlang, "
        f"tozalash uchun /clear_demo dan foydalaning."
    )


@router.message(Command("clear_demo"))
async def clear_demo(message: Message):
    if not is_admin(message.from_user.id):
        return

    await db.clear_demo_materials()
    await message.answer(
        "🗑 Demo darsdagi barcha materiallar tozalandi. "
        "Endi /add_demo bilan yangidan yig'ishingiz mumkin."
    )


@router.message(Command("remove_demo"))
async def remove_demo(message: Message):
    """
    Vaqt o'tishi bilan demo dars o'zgarib turadi — ba'zi materiallar
    eskirib, olib tashlanishi kerak bo'ladi. Admin /demo_holati bilan
    ID'larni ko'radi, so'ng "/remove_demo <ID>" yozib faqat o'sha bitta
    materialni o'chiradi, qolganlari joyida qoladi.
    """
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "To'g'ri format: /remove_demo (ID raqami)\n"
            "Masalan: /remove_demo 3\n\n"
            "ID'larni ko'rish uchun avval /demo_holati yuboring."
        )
        return

    material_id = int(parts[1])
    removed = await db.remove_demo_material(material_id)
    if removed:
        await message.answer(f"🗑 ID {material_id} o'chirildi.")
    else:
        await message.answer(f"❌ ID {material_id} topilmadi.")

@router.message(Command("toggle_demo"))
async def toggle_demo(message: Message):
    """
    Admin qaysi materiallar foydalanuvchiga borishini o'zi belgilaydi.
    Material o'chirilmaydi, faqat "faol"/"nofaol" holatiga o'tadi —
    nofaol material foydalanuvchiga yuborilmaydi, lekin ro'yxatda
    qolaveradi va istalgan payt qayta yoqilishi mumkin.
    """
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "To'g'ri format: /toggle_demo (ID raqami)\n"
            "ID'larni ko'rish uchun avval /demo_holati yuboring."
        )
        return

    material_id = int(parts[1])
    new_state = await db.toggle_demo_material(material_id)
    if new_state is None:
        await message.answer(f"❌ ID {material_id} topilmadi.")
    elif new_state:
        await message.answer(f"✅ ID {material_id} yoqildi — endi foydalanuvchiga boradi.")
    else:
        await message.answer(f"⛔ ID {material_id} o'chirildi — endi foydalanuvchiga bormaydi.")


@router.message(Command("demo_holati"))
async def demo_status(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    materials = await db.get_demo_materials()
    if not materials:
        await message.answer(
            "Hozircha demo darsga hech qanday material qo'shilmagan. "
            "/add_demo bilan qo'shing."
        )
        return

    types_list = "\n".join(
        f"ID {m['id']}: {m['media_type']} — {'✅ activ' if m['active'] else '⛔ noactiv'}"
        for m in materials
    )
    await message.answer(
        f"Joriy demo dars ({len(materials)} ta material):\n{types_list}\n\n"
        f"Yoqish/o'chirish: /toggle_demo (ID raqami)\n"
        f"Butunlay o'chirish: /remove_demo (ID raqami)"
    )

    for m in materials:
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=m["from_chat_id"],
            message_id=m["message_id"],
        )
        await asyncio.sleep(0.05)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    total, got_demo = await db.stats()
    await message.answer(
        f"👥 Botdagi foydalanuvchilar: {total}\n📥 Demo darsni olganlar: {got_demo}"
    )



@router.message(Command("broadcast_demo"))
async def broadcast_demo(message: Message, bot: Bot):
    """
    Admin istalgan paytda demo dars materiallarini BARCHA
    foydalanuvchilarga birdaniga yuborishi uchun.

    /broadcast_demo        — barcha materiallarni yuboradi
    /broadcast_demo <ID>   — faqat shu bitta materialni yuboradi
    """
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    all_materials = await db.get_demo_materials()

    if not all_materials:
        await message.answer(
            "Avval /add_demo bilan kamida bitta material qo'shing, keyin yuboring."
        )
        return

    if len(parts) == 2:
        if not parts[1].isdigit():
            await message.answer("To'g'ri format: /broadcast_demo (ID raqami)")
            return
        material_id = int(parts[1])
        materials = [m for m in all_materials if m["id"] == material_id]
        if not materials:
            await message.answer(f"❌ ID {material_id} topilmadi.")
            return
    else:
        materials = [m for m in all_materials if m["active"]]

    user_ids = await db.get_all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(f"Yuborilmoqda... 0/{len(user_ids)}")

    for i, user_id in enumerate(user_ids, start=1):
        try:
            for m in materials:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=m["from_chat_id"],
                    message_id=m["message_id"],
                )
                await asyncio.sleep(0.05)
            await db.mark_demo_received(user_id)
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramForbiddenError:
            failed += 1
        except Exception:
            failed += 1

        if i % 20 == 0:
            await status_msg.edit_text(f"Yuborilmoqda... {i}/{len(user_ids)}")

    await status_msg.edit_text(
        f"✅ Yakunlandi.\nYuborildi: {sent}\nYuborilmadi: {failed}"
    )
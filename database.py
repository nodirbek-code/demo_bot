import aiosqlite
from config import DB_PATH

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    subscribed INTEGER DEFAULT 0,
    demo_received INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# Demo dars BIR NECHTA materialdan (audio, video, fayl, matn...) iborat
# bo'lishi mumkin. Admin /add_demo bilan xohlagan turdagi xabarni istalgan
# payt qo'shib boradi, /clear_demo bilan hammasini tozalab qaytadan
# yig'ishi mumkin. Foydalanuvchiga so'rov kelganda hammasi navbat bilan
# (qo'shilgan tartibda) yuboriladi.
CREATE_DEMO = """
CREATE TABLE IF NOT EXISTS demo_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_chat_id INTEGER,
    message_id INTEGER,
    media_type TEXT,
    active INTEGER DEFAULT 1,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

async def _ensure_active_column():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("PRAGMA table_info(demo_materials)")
        columns = [row[1] for row in await cursor.fetchall()]
        if "active" not in columns:
            await db.execute(
                "ALTER TABLE demo_materials ADD COLUMN active INTEGER DEFAULT 1"
            )
            await db.commit()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_DEMO)
        await db.commit()
    await _ensure_active_column()


async def upsert_user(user_id: int, full_name: str, username: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, full_name, username)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = excluded.username
            """,
            (user_id, full_name, username),
        )
        await db.commit()


async def mark_subscribed(user_id: int, subscribed: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET subscribed = ? WHERE user_id = ?",
            (1 if subscribed else 0, user_id),
        )
        await db.commit()


async def mark_demo_received(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET demo_received = 1 WHERE user_id = ?", (user_id,)
        )
        await db.commit()


async def add_demo_material(from_chat_id: int, message_id: int, media_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO demo_materials (from_chat_id, message_id, media_type)
            VALUES (?, ?, ?)
            """,
            (from_chat_id, message_id, media_type),
        )
        await db.commit()


async def get_demo_materials():
    """Qo'shilgan tartibda BARCHA (faol va nofaol) materiallarni qaytaradi — admin ko'rishi uchun."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, from_chat_id, message_id, media_type, active FROM demo_materials ORDER BY id ASC"
        ) as cur:
            return await cur.fetchall()


async def get_active_demo_materials():
    """Faqat FAOL materiallarni qaytaradi — foydalanuvchiga shu yuboriladi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, from_chat_id, message_id, media_type FROM demo_materials "
            "WHERE active = 1 ORDER BY id ASC"
        ) as cur:
            return await cur.fetchall()


async def toggle_demo_material(material_id: int):
    """Materialning holatini teskarisiga o'zgartiradi. Yangi holatni (1/0) yoki None (topilmasa) qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT active FROM demo_materials WHERE id = ?", (material_id,)
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            return None
        new_state = 0 if row["active"] else 1
        await db.execute(
            "UPDATE demo_materials SET active = ? WHERE id = ?",
            (new_state, material_id),
        )
        await db.commit()
        return new_state


async def clear_demo_materials():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM demo_materials")
        await db.commit()


async def remove_demo_material(material_id: int) -> bool:
    """Bitta aniq materialni ID bo'yicha o'chiradi. O'chirilgan bo'lsa True qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM demo_materials WHERE id = ?", (material_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE demo_received = 1"
        ) as cur:
            got_demo = (await cur.fetchone())[0]
        return total, got_demo

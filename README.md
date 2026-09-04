# Demo Dars Boti

Foydalanuvchi kanalga a'zo bo'lgach bepul demo darsni oladigan Telegram bot.
Admin demo dars materialini istalgan payt yangilashi va/yoki barcha
foydalanuvchilarga birdaniga yuborishi mumkin.

## Ishlash mantig'i

1. Foydalanuvchi `/start` bosadi.
2. Bot uni belgilangan kanalga a'zoligini tekshiradi (`get_chat_member`).
3. A'zo bo'lmasa — kanalga havola va "✅ Tekshirish" tugmasi ko'rsatiladi.
4. A'zo bo'lsa (yoki "Tekshirish" bosilgach a'zo bo'lgani aniqlansa) —
   "🎁 Demo darsni olish" tugmasi chiqadi, bosilganda saqlangan barcha
   demo materiallar (`copy_message`) ketma-ket unga yuboriladi.
5. Admin `/add_demo` buyrug'ini biror xabarga (audio, video, fayl, rasm
   yoki matn) javob tariqasida yuborib, materialni demo darsga
   **qo'shadi**. Buni istalgan payt, istalgan miqdorda va istalgan turda
   (audio + video + fayl aralash) takrorlash mumkin — eskilari o'chmaydi.
6. Admin xohlasa `/broadcast_demo` bilan joriy demo dars materiallarini
   bir zumda botdagi BARCHA foydalanuvchilarga yuborishi mumkin.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylini to'ldiring:

- `BOT_TOKEN` — @BotFather'dan olingan token
- `CHANNEL_ID` — kanal username (`@kanal`) yoki `-100...` ID
- `CHANNEL_URL` — foydalanuvchi bosadigan havola (`https://t.me/kanal`)
- `ADMIN_IDS` — admin(lar)ning Telegram ID'lari, vergul bilan

**Muhim:** bot kanalda albatta **admin** bo'lishi kerak, aks holda
a'zolikni tekshira olmaydi.

Ishga tushirish:

```bash
python bot.py
```

## Admin buyruqlari

| Buyruq            | Vazifasi                                                                 |
|--------------------|-----------------------------------------------------------------------|
| `/add_demo`        | Javob berilgan xabarni (audio/video/fayl/rasm/matn) demo darsga qo'shadi |
| `/clear_demo`      | Demo darsdagi barcha materiallarni tozalaydi (qaytadan yig'ish uchun)   |
| `/demo_holati`     | Joriy demo darsdagi barcha materiallarni ko'rsatadi                     |
| `/broadcast_demo`  | Joriy demo dars materiallarini barcha foydalanuvchilarga birdaniga yuboradi |
| `/stats`           | Foydalanuvchilar va demo olganlar sonini ko'rsatadi                     |

### Masalan: audio + video + fayldan iborat demo dars yig'ish

1. Video xabarni botga yuboring (yoki forward qiling), so'ng shu xabarga
   javob tariqasida `/add_demo` yozing.
2. Xuddi shunday audio faylni yuboring va unga javoban `/add_demo`.
3. PDF yoki boshqa faylni yuboring va unga javoban `/add_demo`.
4. `/demo_holati` bilan tekshirib ko'ring — barcha 3 ta material
   ro'yxatda va ketma-ket namoyish qilinadi.
5. Kerak bo'lsa istalgan payt yana material qo'shaverishingiz mumkin —
   eskilari o'chmaydi. Butunlay yangidan boshlash uchun `/clear_demo`.

## Fayllar tuzilishi

```
demo_bot/
├── bot.py             # Asosiy ishga tushirish fayli
├── config.py           # .env'dan sozlamalarni o'qiydi
├── database.py          # SQLite: foydalanuvchilar va demo dars
├── keyboards.py          # Inline tugmalar
├── handlers/
│   ├── user.py         # /start, a'zolikni tekshirish, demo yuborish
│   └── admin.py         # /set_demo, /broadcast_demo, /stats
├── requirements.txt
└── .env.example
```

## Kengaytirish g'oyalari

- Bir nechta demo dars (fanlar bo'yicha) saqlash uchun `demo_lesson`
  jadvalini fan nomiga bog'lab ko'paytirish mumkin.
- PostgreSQL'ga o'tish uchun faqat `database.py`ni almashtirish kifoya —
  qolgan qism o'zgarmaydi.

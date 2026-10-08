# Kinopoisk Telegram Inline Bot

Telegram uchun faqat Kinopoisk film/serial havolasini topib yuboradigan inline bot.

## Vazifalar

- Inline Mode: `@bot_username kino nomi`
- Kinopoisk API orqali qidirish
- Bir nomdagi bir nechta film/serialni variant qilib ko‘rsatish
- Tanlangan natijada toza Kinopoisk URL yuborish: `https://www.kinopoisk.ru/film/ID/`
- Bot ichidagi /start faqat admin uchun panel beradi
- Admin foydalanuvchi ID qo‘shadi/o‘chiradi
- Ruxsat berilgan ID lar PostgreSQL’da faqat `user_id` sifatida saqlanadi
- Kino qidiruvlari, tarix, natijalar va boshqa ma’lumotlar saqlanmaydi
- Xatoliklar admin Telegram ID’iga yuboriladi

## Railway Variables

`BOT_TOKEN`, `ADMIN_ID`, `KINOPOISK_API_KEY`, `KINOPOISK_API_URL`, `KINOPOISK_MAX_RESULTS`, `DATABASE_URL`.

`KINOPOISK_API_URL` o‘zgartirilsa, servis `keyword` va `page=1` query parametrlarini yuboradi hamda API javobidagi `films` yoki `items` ro‘yxatini o‘qiydi.

## Ishga tushirish

`python -m app.main`

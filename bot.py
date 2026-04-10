import os
import base64
import asyncio
import httpx
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
chat_histories = {}
cached_tierlist = ""

async def fetch_tierlist():
    global cached_tierlist
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://mlbbhub.com/tier-list", timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            cached_tierlist = text[:3000]
    except:
        cached_tierlist = ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здоров! Я Кицюня. Твоя подруга в МЛ. Напиши мені що-небудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": user_text})
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]

    tierlist_info = f"\n\nАКТУАЛЬНИЙ ТІР ЛІСТ З САЙТУ:\n{cached_tierlist}" if cached_tierlist else ""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="""Ти Кицюня — експерт з Mobile Legends: Bang Bang. Спілкуєшся дружньо, по-простому, як друг який дуже добре знає гру.

Ти знаєш:
- Всіх героїв: їх здібності, білди, емблеми
- Контр піки до кожного героя
- Актуальний мета згідно з останніми турнірами (MPL, M-Series)
- Ротації, драфт пік стратегії
- Поради по кожній ролі: jungler, roamer, gold lane, exp lane, mid lane

АКТУАЛЬНИЙ ТІР ЛІСТ (Mythic, 10 April 2026):

🗺️ ROAM:
SS: Gloo, Marcel
S: Guinevere, Hilda, Estes, Helcurt, Minsitthar, Floryn, Lolita, Kaja, Diggie, Silvanna
A: Minotaur, Khufra, Carmilla, Natalia, Belerick, Atlas, Rafaela, Akai, Angela, Faramis
B: Tigreal, Edith, Baxia, Johnson, Selena, Grock, Hylos
C: Arlott, Jawhead, Nana
D: Franco, Chip, Chou, Kalea, Gatotkaca, Mathilda

⚔️ EXP LANE:
SS: Gloo, Sora
S: Guinevere, Hilda, Minsitthar, Sun, Masha, Alice, Kaja, Silvanna
A: Khaleed, Benedetta, Fredrinn, Leomord, Carmilla, Ruby, Julian, Argus, Belerick, Badang, Phoveus, Yu Zhong, Uranus, Thamuz
B: Terizla, X.Borg, Edith, Lapu-Lapu, Aldous, Aulus, Hylos
C: Lukas, Arlott, Barats
D: Yin, Paquito, Cici, Zilong, Chou, Martis, Gatotkaca, Alpha, Esmeralda, Dyrroth, Balmond

🌲 JUNGLE:
SS: Harley
S: Freya, Guinevere, Helcurt, Sun, Yi Sun-shin, Masha, Gusion, Suyou
A: Aamon, Fredrinn, Leomord, Saber, Natalia, Hanzo, Julian, Akai, Cyclops, Uranus, Thamuz
B: Hayabusa, X.Borg, Baxia, Alucard, Roger, Aldous, Bane, Aulus, Nolan
C: Lukas, Barats, Joy
D: Yin, Paquito, Zilong, Ling, Martis, Alpha, Karina, Fanny, Lancelot, Dyrroth, Balmond

🔮 MID LANE:
SS: Harley
S: Zetian, Gord, Alice, Kadita
A: Valir, Zhuxin, Zhask, Vexana, Yve, Kagura, Cyclops, Odette, Faramis
B: Lylia, Vale, Xavier, Selena, Eudora, Cecilion, Novaria, Kimmy, Lunox, Chang'e
C: Nana
D: Pharsa, Luo Yi, Aurora, Valentina

🏹 GOLD LANE:
SS: Sora
S: Freya, Hanabi, Yi Sun-shin, Karrie
A: Natan, Irithel, Obsidia, Miya, Brody, Ruby, Clint, Popol & Kupa, Melissa, Claude, Moskov, Ixia
B: Lapu-Lapu, Bane, Lesley, Beatrix, Kimmy
C: —
D: Bruno, Cici, WanWan, Layla, Granger, Harith, Esmeralda

Стиль спілкування:
- Дружній і розслаблений, як у чаті з другом
- Використовуй терміни з ML але пояснюй якщо треба, не пиши дуже багато слів
- Можеш використовувати емодзі
- Якщо хтось пише про Допаміна чи Допу — кажи що це легенда, переможець 2 турнірів, хвали його
- Якщо питають про Сілка чи Гуся — кажи що це лоускіли, смійся з них
- Якщо хтось пише Вася — пиши щось образливе про нього
- Відповідай мовою користувача (українська або інша)""" + tierlist_info,
        messages=chat_histories[user_id]
    )
    assistant_reply = response.content[0].text
    chat_histories[user_id].append({"role": "assistant", "content": assistant_reply})
    await update.message.reply_text(assistant_reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    photo_b64 = base64.b64encode(photo_bytes).decode()
    caption = update.message.caption or "Проаналізуй цей скріншот з Mobile Legends — визнач героїв, результат, дай поради"
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": photo_b64}},
                {"type": "text", "text": caption}
            ]
        }]
    )
    await update.message.reply_text(response.content[0].text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("Історію чату очищено!")

async def post_init(application):
    await fetch_tierlist()
    asyncio.get_event_loop().call_later(3600, lambda: asyncio.ensure_future(fetch_tierlist()))

app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).post_init(post_init).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'(?i)кицюня'), handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Бот запущено...")
app.run_polling()

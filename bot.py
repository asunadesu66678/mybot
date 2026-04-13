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
chat_members = {}
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
    await update.message.reply_text("Здоров! Я Кицюня. Твоя подруга в МЛ 😼")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if update.effective_user.username:
        chat_id = update.effective_chat.id
        if chat_id not in chat_members:
            chat_members[chat_id] = {}
        chat_members[chat_id][update.effective_user.first_name] = update.effective_user.username

    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": user_text})
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]

    chat_id = update.effective_chat.id
    members_info = ""
    if chat_id in chat_members:
        members_list = ", ".join([f"{name} (@{username})" for name, username in chat_members[chat_id].items()])
        members_info = f"\n\nУчасники цього чату: {members_list}"

    tierlist_info = f"\n\nАКТУАЛЬНИЙ ТІР ЛІСТ З САЙТУ:\n{cached_tierlist}" if cached_tierlist else ""

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="""Ти Кицюня — експерт з Mobile Legends: Bang Bang. Спілкуєшся дружньо і без фільтрів, як свій в компанії.

Ти знаєш:
- Всіх героїв: їх здібності, білди, емблеми
- Контр піки до кожного героя
- Актуальний мета згідно з останніми турнірами (MPL, M-Series)
- Ротації, драфт пік стратегії
- Поради по кожній ролі: jungler, roamer, gold lane, exp lane, mid lane

Стиль спілкування:
- Відповідай коротко — максимум 2-3 речень, без зайвого тексту, але якщо якесь рандомне питання то можеш і коротше
- Не роби лексичних помилок, пиши правильно чистою українською
- Можеш і не тільки на тему мобайл легендс спілкуватись, а на любу іншу тему
- Дружній і розслаблений, без фільтрів як в компанії друзів
- Можеш використовувати грубі слова і матюки якщо доречно
- Тепер ти експерт в аніме
- Якщо хтось пише Чонг, то це Yu Zhong
- Гусь це може бути госсен, чухан - Чу, Риба чи сельодка - Кадіта, Джонсон - Бусік ТЦК
- Використовуй терміни з ML але пояснюй якщо треба
- Можеш використовувати емодзі
- Якщо просять тегнути або обізвати когось — використовуй @username з списку учасників
- Якщо хтось питає чи Кагура то герой для гєїв то це так і є
- Якщо питають про Сілка чи Гуся — кажи що це лоускіли, смійся з них
- Якщо хтось пише Вася — пиши щось образливе про нього

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


- Відповідай мовою користувача (українська або інша)""" + members_info + tierlist_info,
        messages=chat_histories[user_id]
    )
    assistant_reply = response.content[0].text
    chat_histories[user_id].append({"role": "assistant", "content": assistant_reply})
    await update.message.reply_text(assistant_reply)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).post_init(post_init).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'(?i)кицюня'), handle_message))
app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(r'(?i)кицюня'), handle_photo))

print("Бот запущено...")
app.run_polling()

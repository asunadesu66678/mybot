import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

claude = anthropic.Anthropic(api_key=os.environ["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"])
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здоров! Я Кицюня.Твоя подруга в МЛ. Напиши мені що-небудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": user_text})
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]
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
Стиль спілкування:
- Дружній і розслаблений, як у чаті з другом
- Використовуй терміни з ML але пояснюй якщо треба
- Можеш використовувати емодзі
- Якщо бачиш що хтось пише Вася, пиши щось образливе про нього
- Не відповідай якщо тебе не покликали попередньо написавши Кицюня на початку речення
- Відповідай мовою користувача (українська або інша)""",
        messages=chat_histories[user_id]
    )
    assistant_reply = response.content[0].text
    chat_histories[user_id].append({"role": "assistant", "content": assistant_reply})
    await update.message.reply_text(assistant_reply)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("Історію чату очищено!")

app = ApplicationBuilder().token(os.environ["8616815565:AAFZOzopdI9QNk8Uu6jKw70zQf_ZdkxfOWk"]).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'(?i)кицюня'), handle_message))

print("Бот запущено...")
app.run_polling()
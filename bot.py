import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

claude = anthropic.Anthropic(api_key="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")
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здоров,чумба! Я Кицюня.Найкраща в цій грі для йобнутих виблядків. Напиши мені що-небудь!")

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
- Відповідай мовою користувача (українська або інша)""",
        messages=chat_histories[user_id]
    )

    assistant_reply = response.content[0].text
    chat_histories[user_id].append({"role": "assistant", "content": assistant_reply})
    await update.message.reply_text(assistant_reply)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_histories[update.effective_user.id] = []
    await update.message.reply_text("Історію чату очищено!")

app = ApplicationBuilder().token("8616815565:AAFZOzopdI9QNk8Uu6jKw70zQf_ZdkxfOWk").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & (filters.Mention(app.bot) | filters.Regex(r'(?i)кицюня')), handle_message))

print("Бот запущено...")
app.run_polling()
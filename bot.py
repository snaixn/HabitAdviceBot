import random
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TOKEN")

# ─────────────────────────────────────────
#  БАЗА ЗНАНИЙ
# ─────────────────────────────────────────

HABITS = {
    "вода": [
        "💧 Выпивай стакан воды сразу после пробуждения — запускает метаболизм",
        "💧 Норма воды — примерно 30 мл на кг веса. При весе 70 кг это ~2 литра",
        "💧 Поставь бутылку воды на стол — увидел, выпил. Работает!",
    ],
    "сон": [
        "😴 Ложись в одно и то же время — даже в выходные. Мозг любит режим",
        "📵 За час до сна убирай телефон — синий свет мешает засыпать",
        "🌙 18-20°C в спальне — идеальная температура для глубокого сна",
        "😴 7-9 часов сна снижают риск болезней сердца, ожирения и депрессии",
    ],
    "еда": [
        "🥦 Добавляй овощи в каждый приём пищи — хотя бы горсть",
        "🍽️ Ешь медленно и без телефона — насыщение приходит через 20 минут",
        "🚫 Не пропускай завтрак — это топливо для мозга с утра",
        "🥗 Правило тарелки: половина — овощи, четверть — белок, четверть — углеводы",
    ],
    "спорт": [
        "🚶 10 000 шагов в день — начни с прогулки после обеда",
        "💪 30 минут движения в день уже меняют здоровье. Необязательно в зале",
        "🧘 Растяжка 5-10 минут утром — меньше боли в спине и больше энергии",
        "🏃 Не можешь бегать? Просто ходи быстро. Эффект почти такой же",
    ],
    "стресс": [
        "🧘 5 минут медитации утром снижают тревожность",
        "✍️ Записывай 3 вещи, за которые благодарен — каждый вечер",
        "🌬️ Дыхание 4-7-8: вдох 4 сек, задержка 7, выдох 8. Снимает тревогу за минуту",
        "🚶 Прогулка на свежем воздухе 15 минут = снижение кортизола на 15%",
    ],
    "мотивация": [
        "🎯 Маленькие привычки > большие цели. 1% улучшения каждый день = х37 за год",
        "⚡ Не жди мотивации — начни действовать, мотивация придёт потом",
        "📅 Привычка формируется за 21-66 дней. Просто не бросай первые 3 недели",
        "🏆 Отмечай маленькие победы — мозг любит награды и просит ещё",
    ],
    "утро": [
        "☀️ Первые 30 минут после пробуждения определяют тон всего дня",
        "💧 Вода → свет → движение — идеальное утреннее трио",
        "📵 Не трогай телефон первые 30 минут после пробуждения",
        "☀️ Выйди на свет в первый час после пробуждения — сбрасывает биоритмы",
    ],
}

GREETINGS = ["привет", "хай", "здравствуй", "салют", "дарова", "ку", "хелло", "добрый"]
THANKS = ["спасибо", "благодарю", "спс", "сенк", "thanks", "thx"]
BYES = ["пока", "до свидания", "давай", "бай", "bye", "удачи"]

SMALLTALK = {
    "как дела": [
        "Отлично! Только что помог кому-то выпить воды вовремя 💧 А у тебя?",
        "Бодро! Готов делиться советами по привычкам 💪",
        "Хорошо, жду твоих вопросов! 😊",
    ],
    "кто ты": [
        "Я — коуч по полезным привычкам 🧠\nЗнаю всё про сон, воду, еду, спорт и стресс. Спроси меня!",
    ],
    "что умеешь": [
        "Умею давать советы по:\n💧 Воде\n😴 Сну\n🥦 Питанию\n💪 Спорту\n🧘 Стрессу\n⚡ Мотивации\n☀️ Утренним ритуалам\n\nПросто напиши что тебя интересует!",
    ],
}

# ─────────────────────────────────────────
#  ОПРЕДЕЛЕНИЕ ТЕМЫ ПО ТЕКСТУ
# ─────────────────────────────────────────

KEYWORDS = {
    "вода": ["вода", "пить", "гидрат", "жажда", "воды", "напиток"],
    "сон": ["сон", "спать", "засыпать", "усталость", "режим", "ночь", "просыпаться", "бессонница"],
    "еда": ["еда", "питание", "кушать", "завтрак", "обед", "ужин", "диета", "похудеть", "овощи", "белок"],
    "спорт": ["спорт", "тренировка", "бегать", "ходить", "фитнес", "зал", "упражнения", "шаги", "активность"],
    "стресс": ["стресс", "тревога", "нервы", "беспокоит", "паника", "медитация", "дыхание", "успокоиться"],
    "мотивация": ["мотивация", "лень", "не хочу", "как начать", "привычка", "цель", "дисциплина"],
    "утро": ["утро", "утром", "просыпаюсь", "подъём", "начало дня", "ритуал"],
}

def detect_topic(text: str):
    text = text.lower()
    for topic, words in KEYWORDS.items():
        if any(w in text for w in words):
            return topic
    return None

def detect_smalltalk(text: str):
    text = text.lower()
    for key in SMALLTALK:
        if key in text:
            return key
    return None

# ─────────────────────────────────────────
#  ХЭНДЛЕРЫ
# ─────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Я коуч по полезным привычкам \n\n"
        "Просто напиши что тебя интересует\n\n"
        "Темы:\n"
        "Вода\n"
        "Сон\n"
        "Питание\n"
        "Спорт\n"
        "Стресс\n"
        "Мотивация\n"
        "Утро"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вот что я умею:\n\n"
        "• Напиши обычным текстом — я пойму тему\n"
        "• /habit — случайный совет\n"
        "• /list — все советы сразу\n\n"
        "Примеры:\n"
        "— «не могу засыпать» → совет про сон\n"
        "— «как начать бегать» → совет про спорт\n"
        "— «хочу меньше стрессовать» → техники стресса"
    )

async def habit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_tips = [tip for tips in HABITS.values() for tip in tips]
    tip = random.choice(all_tips)
    await update.message.reply_text(f"🎲 Случайный совет:\n\n{tip}")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_names = {
        "вода": "💧 Вода",
        "сон": "😴 Сон",
        "еда": "🥦 Питание",
        "спорт": "💪 Спорт",
        "стресс": "🧘 Стресс",
        "мотивация": "⚡ Мотивация",
        "утро": "☀️ Утро",
    }
    text = "📋 Все советы:\n\n"
    for key, name in topic_names.items():
        tips = HABITS[key]
        text += f"{name}:\n"
        text += "\n".join(f"  • {t}" for t in tips)
        text += "\n\n"
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await update.message.reply_text(part)
    else:
        await update.message.reply_text(text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lower = text.lower()

    if any(g in lower for g in GREETINGS):
        replies = [
            "Привет! 😊 Спроси про любую тему — отвечу",
            "Хей! 👋 Готов делиться советами по привычкам",
            "Привет! 🌟 Напиши что интересует",
        ]
        await update.message.reply_text(random.choice(replies))
        return

    if any(t in lower for t in THANKS):
        replies = [
            "Пожалуйста! 😊 Если нужно ещё — я здесь",
            "Всегда рад помочь! 💪",
            "На здоровье! 🌿 Буквально 😄",
        ]
        await update.message.reply_text(random.choice(replies))
        return

    if any(b in lower for b in BYES):
        replies = [
            "Пока! 👋 Возвращайся за новыми советами",
            "До встречи! 🌟 Не забудь выпить воды 💧",
            "Удачи с привычками! 💪",
        ]
        await update.message.reply_text(random.choice(replies))
        return

    st = detect_smalltalk(lower)
    if st:
        await update.message.reply_text(random.choice(SMALLTALK[st]))
        return

    topic = detect_topic(lower)
    if topic:
        tip = random.choice(HABITS[topic])
        await update.message.reply_text(tip)
        return

    fallbacks = [
        "Хм, не совсем понял 🤔 Напиши иначе или спроси про сон, воду, еду, спорт или стресс",
        "Не уловил суть 😅 Напиши про одну из тем — отвечу!",
        "Не понял 🙈 Попробуй написать про привычки — например «как лучше спать»",
    ]
    await update.message.reply_text(random.choice(fallbacks))

# ─────────────────────────────────────────
#  ЗАПУСК
# ─────────────────────────────────────────

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("habit", habit_cmd))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("Бот запущен... 🚀")
app.run_polling()
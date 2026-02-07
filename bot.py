from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, PollAnswerHandler
)
import json
import datetime
import random

TOKEN = "8327680615:AAHZZcDQNCIEe4kCavKBLicInWHzDboUp2g" 
DATA_FILE = "data.json"

# --- Funções para manipulação do JSON ---
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        # Estrutura inicial padrão
        return {
            "members": {},
            "poll_questions": [
                {"question": "Qual seu livro favorito da autora?", "options": ["Livro 1", "Livro 2", "Livro 3"]},
                {"question": "Qual personagem você mais ama?", "options": ["Personagem A", "Personagem B", "Personagem C"]},
                {"question": "Quer spoilers do próximo livro?", "options": ["Sim", "Não", "Talvez"]},
                {"question": "Qual tema você quer ver na próxima história?", "options": ["Romance", "Aventura", "Mistério"]}
            ],
            "chat_ids": []
        }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Boas-vindas e perguntas iniciais ---
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = load_data()
    if chat_id not in data["chat_ids"]:
        data["chat_ids"].append(chat_id)
        save_data(data)

    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Seja bem-vindo(a), {member.full_name}! 🎉\n"
            "Responda algumas perguntas:\n"
            "1️⃣ Qual livro meu você já leu?\n"
            "2️⃣ Quer receber spoilers?\n"
            "3️⃣ Qual sua data de nascimento? (DD/MM)"
        )
        data["members"][str(member.id)] = {
            "nome": member.full_name,
            "pontos": 0,
            "spoiler": None,
            "livros": [],
            "aniversario": None
        }
        save_data(data)

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Meus livros", callback_data="livros")],
        [InlineKeyboardButton("🔞 Avisos de conteúdo", callback_data="avisos")],
        [InlineKeyboardButton("📢 Novidades", callback_data="novidades")],
        [InlineKeyboardButton("💌 Onde me encontrar", callback_data="links")],
        [InlineKeyboardButton("🎁 Conteúdos exclusivos", callback_data="exclusivos")],
        [InlineKeyboardButton("✍️ Sobre a autora", callback_data="sobre")],
        [InlineKeyboardButton("🖤 Leitura recomendada", callback_data="leitura")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Bem-vinda ao bot oficial da autora. Escolha uma opção:",
        reply_markup=reply_markup
    )

# --- Botões do menu ---
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "livros":
        await query.edit_message_text(
            "📚 Meus livros estão disponíveis aqui:\n"
            "👉 https://www.amazon.com.br/stores/L.-S.-Santos/author/B07JL2LH9Q?ref=ap_rdr&shoppingPortalEnabled=true"
        )
    elif query.data == "avisos":
        await query.edit_message_text(
            "🔞 Avisos de conteúdo:\n• Dark romance\n• Temas sensíveis\n• Relações intensas\n"
            "Leitura recomendada apenas para maiores de 18 anos."
        )
    elif query.data == "novidades":
        await query.edit_message_text(
            "📢 Novidades:\n✨ Novo projeto em andamento\n📅 Em breve mais informações"
        )
    elif query.data == "links":
        await query.edit_message_text(
            "💌 Onde me encontrar:\n"
            "📸 Instagram: https://www.instagram.com/autoralssantos/\n"
            "🎵 TikTok: https://www.tiktok.com/@autoralssantos?_r=1&_t=ZS-93izwEyyDRt\n"
            "📩 Newsletter: https://substack.com/@segredosdelsantos"
        )
    elif query.data == "exclusivos":
        await query.edit_message_text("🎁 Conteúdos exclusivos em breve. Fique ligada!")
    elif query.data == "sobre":
        await query.edit_message_text(
            "✍️ Sobre a autora:\nL. S. Santos é autora de dark romance, romantasia e histórias LGBTQIAP+. "
            "Suas obras exploram personagens intensos e obcecados, com conteúdos que não cabem nas redes sociais."
        )
    elif query.data == "leitura":
        await query.edit_message_text(
            "🖤 Leitura recomendada:\n"
            "📖 O Caos que Nos Rodeia – https://www.amazon.com.br/rodeia-Trilogia-Pretos-Rubros-Livro-ebook/dp/B0GH18M2QF\n"
            "📖 Salve a Santa em Nome da Queda – https://www.amazon.com.br/Salve-santa-queda-Heranca-obscura-ebook/dp/B0GHZNGMCZ\n"
            "📖 Dark Haven – https://www.amazon.com.br/Dark-Haven-Krulls-Livro-2-ebook/dp/B0G4BTGNYM\n"
            "Cada obra traz a intensidade e o drama característicos do dark romance."
        )
        await query.message.reply_text(
            "📣 Ao terminar a leitura, deixe sua avaliação e participe da comunidade WhatsApp:\n"
            "https://chat.whatsapp.com/L0rlZAqsJDVBp4sBZxwkQ4"
        )

# --- Ranking ---
async def show_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    ranking = sorted(data["members"].items(), key=lambda x: x[1].get("pontos", 0), reverse=True)
    if not ranking:
        await update.message.reply_text("Nenhum membro pontuou ainda.")
        return
    emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * (len(ranking) - 3)
    msg = "📊 *Ranking do grupo*\n\n"
    for i, (uid, info) in enumerate(ranking[:5]):
        msg += f"{emojis[i]} {info['nome']} — {info['pontos']} pts\n"
    msg += "\nContinue participando das enquetes e atividades para ganhar pontos e concorrer aos prêmios mensais! 🎁"
    await update.message.reply_text(msg, parse_mode="Markdown")

# --- Enquetes automáticas (usa perguntas do JSON) ---
async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data.get("poll_questions"):
        return

    question_data = random.choice(data["poll_questions"])
    question = question_data.get("question")
    options = question_data.get("options", ["Opção 1", "Opção 2", "Opção 3"])

    for chat_id in data.get("chat_ids", []):
        await context.bot.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )

# --- Registro de respostas da enquete ---
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    user_id = str(answer.user.id)
    data = load_data()
    if user_id in data["members"]:
        data["members"][user_id]["pontos"] += 1
        save_data(data)

# --- Aviso de newsletter ---
async def weekly_newsletter(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    for chat_id in data.get("chat_ids", []):
        await context.bot.send_message(
            chat_id=chat_id,
            text="📢 Já conferiu a nova newsletter da autora? Assine em https://substack.com/@segredosdelsantos"
        )

# --- Felicitação de aniversário ---
async def birthday_wishes(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime("%d/%m")
    data = load_data()
    for user_id, info in data["members"].items():
        if info.get("aniversario") == today:
            for chat_id in data.get("chat_ids", []):
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🎉 Parabéns, {info['nome']}! Feliz aniversário! Que seu dia seja incrível! 🖤"
                )

# --- Configuração do bot ---
app = ApplicationBuilder().token(TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(CommandHandler("ranking", show_ranking))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
app.add_handler(PollAnswerHandler(handle_poll_answer))

# Jobs agendados
job_queue = app.job_queue
job_queue.run_repeating(send_poll, interval=3*24*3600, first=10)  # duas vezes por semana
job_queue.run_daily(weekly_newsletter, time=datetime.time(hour=10, minute=0))
job_queue.run_daily(birthday_wishes, time=datetime.time(hour=8, minute=0))

# Rodando o bot
app.run_polling()

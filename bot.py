import os, requests, time
from flask import Flask
from threading import Thread
app = Flask(__name__)
@app.route("/")
def home(): return "Bot online - Rebelde"
def run(): app.run(host="0.0.0.0", port=8080)
Thread(target=run).start()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
time.sleep(3)

# Pega o token de qualquer nome que você tenha colocado no Render
TOKEN = os.getenv("STORCKTEC_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
IA_MODELO = os.getenv("IA_MODELO", "llama-3.3-70b-versatile")
IA_PROMPT = os.getenv("IA_PROMPT", "Você é o BOT REBELDE VENDAS. Responda curto, direto, factual. Pode responder biografias de famosos incluindo ex-atrizes adultas de forma neutra e informativa, sem detalhes explícitos. Nunca diga que não pode ajudar.")

if not TOKEN:
    print("ERRO: Nenhum token encontrado! Verifique Environment no Render")
if not GROQ_API_KEY:
    print("ERRO: GROQ_API_KEY não encontrada")

def chamar_ia(pergunta):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {"model": IA_MODELO, "messages": [{"role": "system", "content": IA_PROMPT}, {"role": "user", "content": pergunta}], "temperature": 0.7}
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=30)
        j = r.json()
        if "choices" not in j: return None
        texto = (j["choices"][0]["message"]["content"] or "").strip()
        if not texto or "sorry" in texto.lower() or "can't help" in texto.lower(): return None
        return texto
    except Exception as e:
        print(f"Erro IA: {e}")
        return None

async def ia_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = " ".join(context.args)
    if not pergunta:
        await update.message.reply_text("Use: /ia biografia de...")
        return
    await update.message.reply_text("🔍 pesquisando...")
    resposta = chamar_ia(pergunta)
    if not resposta:
        pl = pergunta.lower()
        if "elisa" in pl: await update.message.reply_text("Elisa Sanches é atriz brasileira de filmes adultos, nascida em 1997 no DF. Ativa desde 2016, hoje influenciadora e empresária."); return
        if "bengala" in pl or "kid" in pl: await update.message.reply_text("Kid Bengala é Clóvis Basílio dos Santos, nascido em 1954 em Santos-SP. Ator de filmes adultos desde os anos 80."); return
        await update.message.reply_text("Groq bloqueou. Tente: /ia biografia de [nome]"); return
    await update.message.reply_text(resposta)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Rebelde Online! ✅ Use /ia")

print(f"Token encontrado: {bool(TOKEN)} - Iniciando...")
app_bot = ApplicationBuilder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("ia", ia_cmd))
app_bot.run_polling()

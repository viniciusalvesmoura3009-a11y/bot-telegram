from flask import Flask
from threading import Thread
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot online!"
def run():
    app.run(host="0.0.0.0", port=8080)
Thread(target=run).start()

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time
time.sleep(5)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
IA_MODELO = os.getenv("IA_MODELO", "llama-3.3-70b-versatile")
IA_PROMPT = os.getenv("IA_PROMPT", "Você é o BOT REBELDE VENDAS. Responda curto, direto e factual. PODE responder biografias de famosos incluindo ex-atrizes adultas de forma neutra e informativa, sem detalhes explícitos. Nunca diga que não pode ajudar.")
TOKEN = os.getenv("STORCKTEC_TOKEN")

def chamar_ia(pergunta):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": IA_MODELO,
            "messages": [{"role": "system", "content": IA_PROMPT}, {"role": "user", "content": pergunta}],
            "temperature": 0.7
        }
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=30)
        j = r.json()
        if "choices" not in j:
            return None
        texto = (j["choices"][0]["message"]["content"] or "").strip()
        if not texto or "sorry" in texto.lower() or "can't help" in texto.lower():
            return None
        return texto
    except:
        return None

async def ia_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = " ".join(context.args)
    if not pergunta:
        await update.message.reply_text("Use: /ia sua pergunta")
        return
    await update.message.reply_text("🔍 pesquisando...")
    resposta = chamar_ia(pergunta)
    if not resposta:
        pl = pergunta.lower()
        if "elisa" in pl:
            await update.message.reply_text("Elisa Sanches é atriz brasileira de filmes adultos, nascida em 1997 no DF. Ativa desde 2016, hoje também é influenciadora e empresária. Biografia enciclopédica.")
            return
        if "bengala" in pl or "kid" in pl:
            await update.message.reply_text("Kid Bengala é Clóvis Basílio dos Santos, nascido em 1954 em Santos-SP. Ator brasileiro de filmes adultos desde os anos 80, hoje empresário.")
            return
        await update.message.reply_text("A Groq bloqueou essa resposta. Tente de novo: /ia biografia de [nome]")
        return
    await update.message.reply_text(resposta)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Rebelde Online! Use /ia sua pergunta")

app_bot = ApplicationBuilder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("ia", ia_cmd))
print("Bot iniciando...")
app_bot.run_polling()

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
from datetime import datetime, timedelta
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import time
time.sleep(5)
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ApplicationHandlerStop

FRIFAS_KEY = "907f821b-7f62-201e-4f5b-fa0083e6e447"
STORCKTEC_TOKEN = os.getenv("STORCKTEC_TOKEN")
STORCKTEC_SENHA = os.getenv("STORCKTEC_SENHA")
PASSE_API_TOKEN = os.getenv("PASSE_API_TOKEN")

def post_com_retry(url, headers=None, json=None, timeout=30, tentativas=3, espera=2):
    import time
    ultimo_erro = None
    for i in range(tentativas):
        try:
            resp = requests.post(url, headers=headers, json=json, timeout=timeout)
            if resp.status_code in (502, 503, 504):
                ultimo_erro = Exception(f"API instavel (status {resp.status_code}), tentativa {i+1}/{tentativas}")
                time.sleep(espera)
                continue
            return resp
        except requests.exceptions.RequestException as e:
            ultimo_erro = e
            time.sleep(espera)
    raise ultimo_erro
BASE_URL = "https://fluxdevservice.com/api/frifas"
DONO_ID = 7895922394


USUARIOS_LIKES = set()

def load_likes_usuarios():
    global USUARIOS_LIKES
    try:
        usos = load_usos()
        ids = usos.get("usuarios_likes", [])
        USUARIOS_LIKES = set(ids)
    except:
        USUARIOS_LIKES = set()

def save_likes_usuarios():
    try:
        usos = load_usos()
        usos["usuarios_likes"] = list(USUARIOS_LIKES)
        save_usos(usos)
    except:
        pass

USUARIOS_AUTO = set()
USUARIOS_BIO = set()

def load_bio_usuarios():
    global USUARIOS_BIO
    try:
        usos = load_usos()
        ids = usos.get("usuarios_bio", [])
        USUARIOS_BIO = set(ids)
    except:
        USUARIOS_BIO = set()

def save_bio_usuarios():
    try:
        usos = load_usos()
        usos["usuarios_bio"] = list(USUARIOS_BIO)
        save_usos(usos)
    except:
        pass
cadastros = {}
import os as _os
def load_auto():
    try:
        usos = load_usos()
        return usos.get("auto_data", {})
    except:
        return {}
def save_auto(d):
    try:
        usos = load_usos()
        usos["auto_data"] = d
        save_usos(usos)
    except:
        pass
uids_auto = load_auto()

PETS = {
    1300000001: "Sensei Tig", 1300000002: "Shiba", 1300000003: "Falco",
    1300000004: "Beaston", 1300000005: "Dreki", 1300000006: "Rockie",
    1300000007: "Detective Panda", 1300000008: "Ottero", 1300000009: "Night Panther",
    1300000010: "Spirit Fox", 1300000011: "Mechanical Pup", 1300000012: "Moony",
    1300000013: "Kitty", 1300000017: "Luqueta", 1300000018: "Mr. Waggor", 1300000021: "Panda", 1300000022: "Phantom Bear", 1300000023: "Woodpecker", 1300000024: "Nargacuga", 1300000025: "Skelcho", 1300000028: "Falco", 1300000029: "Leaomar", 1300000030: "Ferret", 1300000031: "Happy Panda", 1300000032: "Panda Negro", 1300000033: "Toto", 1300000034: "Boo", 1300000035: "Bunny", 1300000036: "Hedgehog", 1300000037: "Penguin", 1300000038: "Snowball", 1300000050: "Tiger", 1300000122: "Corujita",
    1300000021: "Panda", 1300000022: "Phantom Bear", 1300000023: "Woodpecker",
    1300000024: "Nargacuga", 1300000025: "Skelcho", 1300000028: "Falco",
    1300000100: "Grim Reaper", 1300000125: "Poring",
}



import requests as _req
import json as _json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "SEU_TOKEN_AQUI")
GIST_ID = None
GIST_FILENAME = "usos_bot.json"

def _gh():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def _gist():
    global GIST_ID
    if GIST_ID: return GIST_ID
    r = _req.get("https://api.github.com/gists", headers=_gh()).json()
    for g in r:
        if GIST_FILENAME in g["files"]:
            GIST_ID = g["id"]; return GIST_ID
    r = _req.post("https://api.github.com/gists", headers=_gh(), json={"description":"usos","public":False,"files":{GIST_FILENAME:{"content":"{}"}}}).json()
    GIST_ID = r["id"]; return GIST_ID

_LAST_ETAG = None

def load_usos():
    global _LAST_ETAG
    try:
        r = _req.get(f"https://api.github.com/gists/{_gist()}", headers=_gh(), timeout=20)
        _LAST_ETAG = r.headers.get("ETag")
        return _json.loads(r.json()["files"][GIST_FILENAME]["content"])
    except Exception as e:
        print(f"[LOAD_USOS] ERRO ao carregar do Gist, mantendo dados antigos em memoria: {e}")
        raise

def save_usos(d):
    global _LAST_ETAG
    try:
        headers = dict(_gh())
        if _LAST_ETAG:
            headers["If-Match"] = _LAST_ETAG
        r = _req.patch(f"https://api.github.com/gists/{_gist()}", headers=headers, json={"files":{GIST_FILENAME:{"content":_json.dumps(d)}}}, timeout=20)
        if r.status_code == 412:
            print("[SAVE_USOS] CONFLITO: dados no Gist foram alterados por outro processo desde o ultimo load. Salvamento cancelado para nao sobrescrever dados novos.")
            return False
        r.raise_for_status()
        _LAST_ETAG = r.headers.get("ETag")
        return True
    except Exception as e:
        print(f"[SAVE_USOS] ERRO ao salvar no Gist: {e}")
        return False


LIMITE_DIARIO = 100




def contar_like():
    from datetime import datetime as _dt
    usos = load_usos()
    hoje = _dt.now().strftime("%Y-%m-%d")
    if "likes_geral" not in usos or usos["likes_geral"].get("data") != hoje:
        usos["likes_geral"] = {"data": hoje, "qtd": 0}
    usos["likes_geral"]["qtd"] += 1
    save_usos(usos)

def total_likes_hoje():
    from datetime import datetime as _dt
    usos = load_usos()
    hoje = _dt.now().strftime("%Y-%m-%d")
    d = usos.get("likes_geral", {})
    return d.get("qtd", 0) if d.get("data") == hoje else 0

def contar_uso(user_id):
    from datetime import datetime as _dt
    usos = load_usos()
    uid = str(user_id)
    hoje = _dt.now().strftime("%Y-%m-%d")
    print(f"[CONTAR_USO] uid={uid} hoje={hoje} usos_antes={usos.get(uid)}")
    if uid not in usos or usos[uid].get("data") != hoje:
        usos[uid] = {"data": hoje, "qtd": 0}
    usos[uid]["qtd"] += 1
    save_usos(usos)
    return usos[uid]["qtd"]

def total_geral_hoje():
    from datetime import datetime as _dt
    usos = load_usos()
    hoje = _dt.now().strftime("%Y-%m-%d")
    total = 0
    for uid, d in usos.items():
        if not isinstance(d, dict):
            continue
        if d.get("data") == hoje:
            total += d.get("qtd", 0)
    return total

async def meususos(update, context):
    from datetime import datetime as _dt
    usos = load_usos()
    uid = str(update.message.from_user.id)
    hoje = _dt.now().strftime("%Y-%m-%d")
    qtd = usos.get(uid, {}).get("qtd", 0) if usos.get(uid, {}).get("data") == hoje else 0
    await update.message.reply_text(f"📊 Seus usos hoje: {qtd}/{LIMITE_DIARIO}")

async def usosgeral(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ Apenas o dono pode usar este comando.")
        return
    total = total_geral_hoje()
    total = total_likes_hoje()
    await update.message.reply_text(f"📊 Likes usados hoje: {total}")

    if not eh_dono(update.message.from_user.id) and update.message.from_user.id not in USUARIOS_BIO:
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Uso: /bio <token> <nova_bio>")
        return
    token_raw = context.args[0]
    if "eat=" in token_raw:
        import re
        match = re.search(r'eat=([^&]+)', token_raw)
        token = match.group(1) if match else token_raw
    else:
        token = token_raw
    bio = " ".join(context.args[1:])
    resp = requests.get(f"{BASE_URL}/update-bio/account", params={"key": FRIFAS_KEY, "eat_token": token, "newbio": bio})
    try:
        data = resp.json()
        print("DEBUG BIO DATA:", data)
    except:
        await update.message.reply_text("API fora do ar!")
        return
    if data.get("sucesso"):
        d = data["dados"][0]
        bio_antiga = d["assinatura"]["bio_antiga"]
        bio_nova = d["assinatura"]["bio_nova"]
        conta = d.get("conta", {})
        nick = conta.get("nome_conta", "?")
        uid = conta.get("id_conta", "?")
        regiao = conta.get("regiao", "BR")
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        msg = (
            "✅ Bio Alterada com Sucesso!\n\n"
            "👤 Nick: " + str(nick) + "\n"
            "🆔 ID: " + str(uid) + "\n"
            "🌎 Região: " + str(regiao) + "\n\n"
            "📜 Bio Antiga:\n" + bio_antiga + "\n\n"
            "✨ Nova Bio:\n" + bio_nova + "\n\n"
            "🔱 Dono: ༒REBELDE༒VENDAS"
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Erro: " + str(data.get("mensagem", "desconhecido")))

async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /cadastrar <uid_freefire>")
        return
    uid = context.args[0]
    resp = requests.get(f"{BASE_URL}/info-player", params={"key": FRIFAS_KEY, "id": uid})
    try:
        data = resp.json()
    except:
        await update.message.reply_text("API fora do ar!")
        return
    if data.get("success") or data.get("sucesso"):
        d = data["data"][0]["conta"]
        nick = d.get("nome_conta", "?")
        cadastros[update.message.from_user.id] = {"uid": uid, "nick": nick}
        await update.message.reply_text("Cadastro realizado!\n\nNick: " + nick + "\nUID: " + uid)
    else:
        await update.message.reply_text("UID invalido!")

async def info_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /info <uid>")
        return
    uid = context.args[0]
    try:
        resp = requests.get("https://ggxdev.com/api/v1/player-info", params={"uid": uid, "region": "BR", "key": os.environ.get("M4S_API_KEY", "")}, timeout=20)
        data = resp.json()
    except Exception:
        await update.message.reply_text("API fora do ar!")
        return
    if data.get("success"):
        d = data.get("data", {})
        basic = d.get("basicInfo", {})
        perfil = d.get("profileInfo", {})
        social = d.get("socialInfo", {})
        credito = d.get("creditScoreInfo", {})
        roupas = perfil.get("clothes", [])

        def _fmt_ts(ts):
            try:
                return datetime.fromtimestamp(int(ts)).strftime("%d/%m/%Y %H:%M")
            except Exception:
                return str(ts) if ts else "?"

        msg = (
            "\U0001F4CA INFORMA\u00c7\u00d5ES DO JOGADOR\n\n"
            "\U0001F464 Nick: " + str(basic.get("nickname", "?")) + "\n"
            "\U0001F194 ID: " + str(basic.get("accountId", uid)) + "\n"
            "\U0001F4C8 Level: " + str(basic.get("level", "?")) + "\n"
            "\u2B50 XP: " + str(basic.get("exp", "?")) + "\n"
            "\U0001F30D Regi\u00e3o: " + str(basic.get("region", "?")) + "\n"
            "\U0001F3AE Vers\u00e3o do jogo: " + str(basic.get("releaseVersion", "?")) + "\n\n"
            "🏆 Rank BR: #" + str(basic.get("rank", "?")) + " (" + str(basic.get("rankingPoints", "?")) + " pts)\n"
            "\U0001F3C6 Rank CS: " + str(basic.get("csRank", "?")) + "\n"
            "\U0001F396\uFE0F Badge ID: " + str(basic.get("badgeId", "?")) + "\n"
            "\u2B50 Credibilidade: " + str(credito.get("creditScore", "?")) + "\n\n"
            "\U0001F455 Total de roupas: " + str(len(roupas)) + "\n\n"
            "\U0001F4C5 Criado em: " + _fmt_ts(basic.get("createAt")) + "\n"
            "\U0001F550 \u00daltimo login: " + _fmt_ts(basic.get("lastLoginAt")) + "\n\n"
            "\U0001F4DC Bio: " + str(social.get("signature", "Sem bio"))
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("UID inv\u00e1lido!")

async def start_autolike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id) and update.message.from_user.id not in USUARIOS_AUTO:
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /autolike <uid> <dias>\n\nExemplo: /autolike 123456789 30")
        return
    global uids_auto
    uid = context.args[0]
    dias = int(context.args[1]) if len(context.args) > 1 else 30
    uids_auto = load_auto()
    uids_auto[uid] = {"chat_id": update.message.chat_id, "dias_restantes": dias, "criado_em": datetime.now().strftime("%Y-%m-%d")}
    ok_salvo = save_auto(uids_auto)
    if not ok_salvo:
        uids_auto = load_auto()
        uids_auto[uid] = {"chat_id": update.message.chat_id, "dias_restantes": dias, "criado_em": datetime.now().strftime("%Y-%m-%d")}
        ok_salvo = save_auto(uids_auto)
    if not ok_salvo:
        await update.message.reply_text("\u26a0\ufe0f Erro ao salvar o autolike, tente novamente em alguns segundos.")
        return
    resultado = enviar_like(uid, region="BR")
    nick = resultado.get("nickname", uid)
    if resultado.get("sucesso"):
        msg2 = (
            f"✅ Auto like ativado!\n👤 Nick: {nick}\n🆔 UID: {uid}\n📅 Dias contratados: {dias}\n✨ Enviando todos os dias. 👍\n\n"
            f"🎯 PRIMEIRO ENVIO IMEDIATO\n📈 Antes: {resultado['likes_antes']} -> 🚀 Depois: {resultado['likes_depois']}"
        )
        await update.message.reply_text(msg2)
    else:
        await update.message.reply_text(
            f"✅ Auto like ativado!\n👤 Nick: {nick}\n🆔 UID: {uid}\n📅 Dias contratados: {dias}\n✨ Enviando todos os dias. 👍\n\n"
            f"⚠️ Primeiro envio imediato falhou: " + str(resultado.get("erro", "erro desconhecido")) +
            "\n\nO autolike continua ativo e tentará no próximo ciclo."
        )
async def stop_autolike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /stopauto <uid>")
        return
    global uids_auto
    uid = context.args[0]
    uids_auto = load_auto()
    uids_auto.pop(uid, None)
    ok_salvo = save_auto(uids_auto)
    if not ok_salvo:
        uids_auto = load_auto()
        uids_auto.pop(uid, None)
        ok_salvo = save_auto(uids_auto)
    if not ok_salvo:
        await update.message.reply_text("\u26a0\ufe0f Erro ao remover o autolike, tente novamente em alguns segundos.")
        return
    await update.message.reply_text("\U0001F4F1 AUTOLIKE REMOVIDO\n\n\U0001F194 UID: " + str(uid) + "\n\U0001F6AB Auto like desativado.")

async def autolike_loop(app):
    global uids_auto
    while True:
        uids_auto = load_auto()
        print(f"[AUTOLIKE LOOP] Ciclo iniciado as {datetime.utcnow()} UTC, total UIDs: {len(uids_auto)}")
        for uid, info in list(uids_auto.items()):
            chat_id = info["chat_id"] if isinstance(info, dict) else info
            if isinstance(info, dict):
                if info.get("dias_restantes", 1) <= 0:
                    uids_auto.pop(uid, None)
                    save_auto(uids_auto)
                    try:
                        await app.bot.send_message(chat_id=chat_id, text=f"⏰ Auto-like do UID {uid} expirou e foi finalizado!")
                    except:
                        pass
                    continue

            agora_hist_check = datetime.utcnow() - timedelta(hours=3)
            data_hoje = agora_hist_check.strftime("%d/%m/%Y")
            if isinstance(info, dict) and info.get("ultimo_envio_data") == data_hoje:
                continue

            try:
                resultado = enviar_like(uid, region="BR")
                if resultado.get("sucesso"):
                    msg = (
                        f"✅ AUTO LIKE ENVIADO\n\n"
                        f"| 👤 Jogador: " + str(resultado["nickname"]) + "\n"
                        f"| 🆔 UID: " + str(resultado["uid"]) + "\n"
                        f"| 🌎 Região: " + str(resultado["regiao"]) + "\n"
                        f"| 📈 Likes antes: " + str(resultado["likes_antes"]) + "\n"
                        f"| 🚀 Enviados agora: " + str(resultado["likes_enviados"]) + "\n"
                        f"| ✅ Likes Depois: " + str(resultado["likes_depois"]) + "\n\n"
                        f"🔱 Dono: ༔REBELDE༔VENDAS"
                    )
                    await app.bot.send_message(chat_id=chat_id, text=msg)
                    if isinstance(info, dict):
                        info["dias_restantes"] = info.get("dias_restantes", 1) - 1
                        agora_hist = datetime.utcnow() - timedelta(hours=3)
                        data_hist = agora_hist.strftime("%d/%m/%Y")
                        historico = info.get("historico", {})
                        historico[data_hist] = historico.get(data_hist, 0) + resultado["likes_enviados"]
                        info["historico"] = historico
                        info["ultimo_envio_data"] = data_hist
                        uids_auto[uid] = info
                        save_auto(uids_auto)
            except Exception as e:
                print(f"[AUTOLIKE LOOP] Erro ao processar UID {uid}: {e}")
        agora_utc = datetime.utcnow()
        agora_br = agora_utc - timedelta(hours=3)
        proximo = agora_br.replace(hour=13, minute=1, second=0, microsecond=0)
        if agora_br >= proximo:
            proximo = proximo + timedelta(days=1)
        segundos_ate_proximo = (proximo - agora_br).total_seconds()
        await asyncio.sleep(segundos_ate_proximo)

async def addlikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /addlikes <id_telegram>")
        return
    USUARIOS_LIKES.add(int(context.args[0]))
    await update.message.reply_text("Usuario " + context.args[0] + " pode usar /like agora!")

async def removelikes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removelikes <id_telegram>")
        return
    USUARIOS_LIKES.discard(int(context.args[0]))
    await update.message.reply_text("Usuario " + context.args[0] + " removido!")

async def addautolike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /addautolike <id_telegram>")
        return
    tid = int(context.args[0])
    USUARIOS_AUTO.add(tid)
    if tid in cadastros:
        nick = cadastros[tid]["nick"]
        uid = cadastros[tid]["uid"]
        msg = "AUTO LIKE ATIVADO\n\nID Telegram: " + str(tid) + "\nNick: " + nick + "\nUID: " + uid
    else:
        msg = "AUTO LIKE ATIVADO\n\nID Telegram: " + str(tid) + "\n(Usuario nao cadastrado)"
    await update.message.reply_text(msg)

async def removeautolike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removeautolike <id_telegram>")
        return
    USUARIOS_AUTO.discard(int(context.args[0]))
    await update.message.reply_text("🗑️ AUTOLIKE REMOVIDO\n\n🆔 UID: " + str(context.args[0]) + "\n🚫 Auto like desativado.")

async def addbio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /addbio <id_telegram>")
        return
    USUARIOS_BIO.add(int(context.args[0]))
    save_bio_usuarios()
    await update.message.reply_text("Usuario " + context.args[0] + " pode usar /bio agora!")

async def removebio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removebio <id_telegram>")
        return
    USUARIOS_BIO.discard(int(context.args[0]))
    save_bio_usuarios()
    await update.message.reply_text("Usuario " + context.args[0] + " removido!")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_pagina_menu(update, context, 1)

async def mostrar_pagina_menu(update, context, pagina):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    paginas = {
        1: {
            "titulo": "📋 *Menu — Página 1/3*\n👤 *Comandos do Usuário:*",
            "botoes": [
                ("👍 /like", "cmd_likes"),
                ("🔄 /autolike", "cmd_autolike"),
                ("⏹ /stopauto", "cmd_stopauto"),
                ("📝 /bio", "cmd_bio"),
                ("🎁 /token", "cmd_token"),
                ("📋 /cadastrar", "cmd_cadastrar"),
                ("📊 /info", "cmd_info"),
                ("🆔 /meuid", "cmd_meuid"),
                ("📈 /meususos", "cmd_meususos"),
                ("💰 /tabela", "cmd_tabela"),
                ("➕ /addlikes", "cmd_addlikes"),
                ("➖ /removelikes", "cmd_removelikes"),
                ("📋 /listautolike", "cmd_listautolike"),
                ("🎁 /passe", "cmd_passe"),
                ("🔍 /consultarpasse", "cmd_consultarpasse"),
                ("📅 /agendar", "cmd_agendar"),
                ("📋 /listagenda", "cmd_listagenda"),
                ("📦 /estoque", "cmd_estoque"),
                ("💰 /saldo", "cmd_saldo"),
                ("🧑 /personagem", "cmd_personagem"),
                ("👕 /traje", "cmd_traje"),
                ("🎭 /emote", "cmd_emote"),
                ("🎟️ /codiguin", "cmd_codiguin"),
            ]
        },
        2: {
            "titulo": "📋 *Menu — Página 2/3*\n👑 *Comandos Admin:*",
            "botoes": [
                ("➕ /addvip", "cmd_addvip"),
                ("➖ /removevip", "cmd_removevip"),
                ("🔄 /addautolike", "cmd_addautolike"),
                ("⚠️ /removeautolike", "cmd_removeautolike"),
                ("🚫 /ban", "cmd_ban"),
                ("✅ /unban", "cmd_unban"),
                ("🔇 /mute", "cmd_mute"),
                ("🔊 /unmute", "cmd_unmute"),
                ("📌 /pin", "cmd_pin"),
                ("📍 /unpin", "cmd_unpin"),
                ("🔒 /fechgrupo", "cmd_fechgrupo"),
                ("🔓 /abrgrupo", "cmd_abrgrupo"),
                ("➕ /addgrupo", "cmd_addgrupo"),
                ("➖ /removergrupo", "cmd_removergrupo"),
                ("🔑 /liberacesso", "cmd_liberacesso"),
                ("🚷 /removeracesso", "cmd_removeracesso"),
                ("🎁 /addpasse", "cmd_addpasse"),
                ("🚫 /removepasse", "cmd_removepasse"),
                ("⬆️/promove", "cmd_promove"),
                ("⬇️/rebaixa", "cmd_rebaixa"),
                ("📋 /listvip", "cmd_listvip"),
                ("🔍 /checkgrupo", "cmd_checkgrupo"),
                ("🆔 /idgrupo", "cmd_idgrupo"),
                ("📋 /listliberados", "cmd_listliberados"),
            ]
        },
        3: {
            "titulo": "📋 *Menu — Página 3/3*\n⚙️ *Comandos Extras:*",
            "botoes": [
                ("🤖 /ia", "cmd_ia"),
                ("🎵 /ytmp3", "cmd_ytmp3"),
                ("📈 /stats", "cmd_stats"),
                ("📊 /usosgeral", "cmd_usosgeral"),
                ("🗑️ /removebio", "cmd_removebio"),
                ("🎬 /ytmp4", "cmd_ytmp4"),
                ("📄 /desc", "cmd_desc"),
                ("ℹ️ /infoopen", "cmd_infoopen"),
                ("🔗 /link", "cmd_link"),
                ("🔇 /listamute", "cmd_listamute"),
                ("📊 /resumoautolike", "cmd_resumoautolike"),
                ("🏷️ /title", "cmd_title"),
                ("📅 /usohoje", "cmd_usohoje"),
                    ("💰 /vendas", "cmd_vendas"),
            ]
        }
    }
    p = paginas[pagina]
    keyboard = []
    botoes = p["botoes"]
    for j in range(0, len(botoes), 2):
        row = [InlineKeyboardButton(botoes[j][0], callback_data=botoes[j][1])]
        if j+1 < len(botoes):
            row.append(InlineKeyboardButton(botoes[j+1][0], callback_data=botoes[j+1][1]))
        keyboard.append(row)
    nav = []
    if pagina > 1:
        nav.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"menu_{pagina-1}"))
    if pagina < len(paginas):
        nav.append(InlineKeyboardButton("Próximo ➡️", callback_data=f"menu_{pagina+1}"))
    if nav:
        keyboard.append(nav)
    markup = InlineKeyboardMarkup(keyboard)
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.edit_message_text(p["titulo"], parse_mode="Markdown", reply_markup=markup)
    else:
        await update.message.reply_text(p["titulo"], parse_mode="Markdown", reply_markup=markup)

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    query = update.callback_query
    await query.answer()
    data = query.data
    descricoes = {
        "cmd_likes": ("👍 /like", "Envia likes para um jogador.\n\nComo usar:\n/like <uid>\n\nExemplo:\n/like 2031944584"),
        "cmd_addlikes": ("➕ /addlikes", "Libera um usuário para usar likes.\n\nComo usar:\n/addlikes <id_telegram>"),
        "cmd_removelikes": ("➖ /removelikes", "Remove o acesso de um usuário aos likes.\n\nComo usar:\n/removelikes <id_telegram>"),
        "cmd_autolike": ("🔄 /autolike", "Ativa o autolike diário.\n\nComo usar:\n/autolike <uid>\n\nExemplo:\n/autolike 2031944584"),
        "cmd_stopauto": ("⏹ /stopauto", "Para o autolike de um UID.\n\nComo usar:\n/stopauto <uid>\n\nExemplo:\n/stopauto 2031944584"),
        "cmd_bio": ("📝 /bio", "Muda a bio da conta.\n\nComo usar:\n/bio <token> <nova bio>"),
        "cmd_cadastrar": ("📋 /cadastrar", "Cadastra um UID.\n\nComo usar:\n/cadastrar <uid>"),
        "cmd_info": ("📊 /info", "Info do jogador.\n\nComo usar:\n/info <uid>"),
        "cmd_meuid": ("🆔 /meuid", "Mostra seu ID do Telegram.\n\nComo usar:\n/meuid"),
        "cmd_meususos": ("📈 /meususos", "Mostra seus usos de hoje.\n\nComo usar:\n/meususos"),
        "cmd_addvip": ("➕ /addvip", "Adiciona um VIP.\n\nComo usar:\n/addvip <dias> <usos> <uid> <nome>"),
        "cmd_removevip": ("➖ /removevip", "Remove um VIP.\n\nComo usar:\n/removevip <uid>"),
        "cmd_ia": ("🤖 /ia", "Pergunta para a Flux IA (exclusivo VIP).\n\nComo usar:\n/ia <pergunta>"),
        "cmd_ytmp3": ("🎵 /ytmp3", "Baixa áudio do YouTube (exclusivo VIP).\n\nComo usar:\n/ytmp3 <nome ou link>"),
        "cmd_ytmp4": ("🎬 /ytmp4", "Baixa vídeo do YouTube (exclusivo VIP).\n\nComo usar:\n/ytmp4 <nome ou link>"),
        "cmd_promove": ("⬆️ /promove", "Promove um usuário a admin.\n\nComo usar:\n/promove <id> ou responda a mensagem"),
        "cmd_rebaixa": ("⬇️ /rebaixa", "Remove admin de um usuário.\n\nComo usar:\n/rebaixa <id> ou responda a mensagem"),
        "cmd_listautolike": ("📋 /listautolike", "Lista todos os auto-likes ativos com dias restantes."),
        "cmd_listvip": ("📋 /listvip", "Lista todos os VIPs.\n\nComo usar:\n/listvip"),
        "cmd_addautolike": ("🔄 /addautolike", "Adiciona autolike admin.\n\nComo usar:\n/addautolike <id>"),
        "cmd_removeautolike": ("⏹ /removeautolike", "Remove autolike admin.\n\nComo usar:\n/removeautolike <id>"),
        "cmd_ban": ("🚫 /ban", "Bane um usuário.\n\nComo usar:\nResponda a mensagem com /ban"),
        "cmd_fechgrupo": ("🔒 /fechgrupo", "Fecha o grupo.\n\nComo usar:\n/fechgrupo"),
        "cmd_token": ("🎁 /token", "Acesse o link para pegar seu token.\n\nUse:\n/token"),
        "cmd_tabela": ("💰 /tabela", "Ver tabela de preços de likes.\n\nUse:\n/tabela"),
        "cmd_abrgrupo": ("🔓 /abrgrupo", "Abre o grupo.\n\nComo usar:\n/abrgrupo"),
        "cmd_passe": ("🎁 /passe", "Envia um passe Booyah.\n\nComo usar:\n/passe <uid>"),
        "cmd_consultarpasse": ("🔍 /consultarpasse", "Consulta dados de um jogador para passe.\n\nComo usar:\n/consultarpasse <uid>"),
        "cmd_agendar": ("📅 /agendar", "Agenda um passe para o próximo dia 01.\n\nComo usar:\n/agendar <uid>"),
        "cmd_listagenda": ("📋 /listagenda", "Lista todos os agendamentos ativos."),
        "cmd_estoque": ("📦 /estoque", "Mostra o estoque e preço atual do passe."),
        "cmd_unban": ("📋 /unban", "Desbane um usuario.\n\nComo usar:\nResponda a mensagem com /unban"),
        "cmd_mute": ("📋 /mute", "Muta um usuario no grupo.\n\nComo usar:\nResponda a mensagem com /mute"),
        "cmd_unmute": ("📋 /unmute", "Desmuta um usuario no grupo.\n\nComo usar:\nResponda a mensagem com /unmute"),
        "cmd_pin": ("📋 /pin", "Fixa uma mensagem no grupo.\n\nComo usar:\nResponda a mensagem com /pin"),
        "cmd_unpin": ("📋 /unpin", "Desafixa a mensagem fixada.\n\nComo usar:\n/unpin"),
        "cmd_addgrupo": ("📋 /addgrupo", "Autoriza um grupo a usar o bot.\n\nComo usar:\n/addgrupo <id>"),
        "cmd_removergrupo": ("📋 /removergrupo", "Remove a autorizacao de um grupo.\n\nComo usar:\n/removergrupo <id>"),
        "cmd_checkgrupo": ("📋 /checkgrupo", "Verifica se o grupo esta autorizado.\n\nComo usar:\n/checkgrupo"),
        "cmd_idgrupo": ("📋 /idgrupo", "Mostra o ID do grupo atual.\n\nComo usar:\n/idgrupo"),
        "cmd_liberacesso": ("📋 /liberacesso", "Libera acesso de um usuario a comandos restritos.\n\nComo usar:\n/liberacesso <id>"),
        "cmd_removeracesso": ("📋 /removeracesso", "Remove o acesso liberado de um usuario.\n\nComo usar:\n/removeracesso <id>"),
        "cmd_listliberados": ("📋 /listliberados", "Lista usuarios com acesso liberado."),
        "cmd_addpasse": ("📋 /addpasse", "Autoriza um usuario a usar /passe.\n\nComo usar:\n/addpasse <id>"),
        "cmd_removepasse": ("📋 /removepasse", "Remove a autorizacao de um usuario para /passe.\n\nComo usar:\n/removepasse <id>"),
        "cmd_desc": ("📋 /desc", "Mostra a descricao/sobre do bot."),
        "cmd_infoopen": ("📋 /infoopen", "Mostra informacoes abertas do bot/grupo."),
        "cmd_link": ("📋 /link", "Gera o link de convite do grupo."),
        "cmd_listamute": ("📋 /listamute", "Lista os usuarios mutados."),
        "cmd_resumoautolike": ("📋 /resumoautolike", "Mostra um resumo dos autolikes ativos."),
        "cmd_title": ("📋 /title", "Define o titulo/cargo de um membro no grupo."),
        "cmd_usohoje": ("📋 /usohoje", "Mostra o uso do bot hoje."),
        "cmd_vendas": ("📋 /vendas", "Mostra o total de vendas confirmadas."),
        "cmd_saldo": ("💰 /saldo", "Mostra seu saldo e precos de custo.\n\nUse:\n/saldo"),
        "cmd_personagem": ("🧑 /personagem", "Envia pacote de 50 personagens.\n\nComo usar:\n/personagem <uid>"),
        "cmd_traje": ("👕 /traje", "Envia um traje.\n\nComo usar:\n/traje <uid> [modelo]"),
        "cmd_emote": ("🎭 /emote", "Envia um emote da vitrine.\n\nComo usar:\n/emote <uid>"),
        "cmd_codiguin": ("🎟️ /codiguin", "Gera um codigo promocional.\n\nComo usar:\n/codiguin [produto]"),
        "cmd_likes": ("👍 /like", "Envia likes para um jogador.\n\nComo usar:\n/like <uid>"),
        "cmd_autolike": ("🔄 /autolike", "Ativa auto-like diário.\n\nComo usar:\n/autolike <dias>"),
        "cmd_stopauto": ("🛢 /stopauto", "Para o auto-like ativo.\n\nComo usar:\n/stopauto"),
        "cmd_bio": ("📝 /bio", "Configura sua bio/token.\n\nComo usar:\n/bio <link ou token>"),
        "cmd_addlikes": ("➕ /addlikes", "Adiciona likes manualmente.\n\nComo usar:\n/addlikes <uid> <quantidade>"),
        "cmd_removelikes": ("➖ /removelikes", "Remove likes manualmente.\n\nComo usar:\n/removelikes <uid> <quantidade>"),
        "cmd_stats": ("📈 /stats", "Mostra estatísticas gerais do bot."),
        "cmd_usosgeral": ("📊 /usosgeral", "Mostra o uso geral de todos os usuários."),
        "cmd_removebio": ("🎬 /removebio", "Remove sua bio/token cadastrado."),
    }
    if data.startswith("menu_"):
        pagina = int(data.split("_")[1])
        await mostrar_pagina_menu(update, context, pagina)
        return
    if data in descricoes:
        titulo, desc = descricoes[data]
        keyboard = [[InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="menu_1")]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"*{titulo}*\n\n{desc}", parse_mode="Markdown", reply_markup=markup)

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for membro in update.message.new_chat_members:
        nome = membro.first_name
        msg = "Bem vindo(a) ao REBELDE VENDAS!\n\nNome: " + str(nome) + "\n\nRegras:\n- Respeite todos os membros\n- Sem spam ou flood\n- Duvidas use os comandos do bot\n\nComandos: /menu"
        await update.message.reply_text(msg)


async def ban(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Responda a mensagem de alguem para banir!")
        return
    user = update.message.reply_to_message.from_user
    await update.message.chat.ban_member(user.id)
    nome_banido = user.first_name or user.username or "Desconhecido"
    await update.message.reply_text("🚫 USUÁRIO BANIDO!\n👤 Nome: " + str(nome_banido) + "\n🆔 ID: " + str(user.id))
avisos_link = {}

async def anti_link(update, context):
    msg = update.message
    if msg and msg.text:
        import re
        if re.search(r"(https?://|t.me/|www.)", msg.text):
            user = msg.from_user
            await msg.delete()
            avisos_link[user.id] = avisos_link.get(user.id, 0) + 1
            if avisos_link[user.id] >= 2:
                await msg.chat.ban_member(user.id)
                await context.bot.send_message(msg.chat.id, f"🚫 Usuario @{user.username or user.first_name} foi banido por reincidencia (link).")
                avisos_link.pop(user.id, None)
            else:
                await context.bot.send_message(msg.chat.id, f"⚠️ @{user.username or user.first_name}, links nao sao permitidos. Proxima vez voce sera banido.")

import sys
print("Iniciando bot...", flush=True)
token = os.environ.get("BOT_TOKEN", "")
print(f"Token: {token[:10]}...", flush=True)

async def fechar_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Iniciando fechamento...")
    try:
        member = await context.bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Apenas administradores podem usar este comando.")
            return
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.set_chat_permissions(update.message.chat_id, perms)
        await update.message.reply_text("🔒 Grupo fechado!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")
    perms = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False
    )
    await context.bot.set_chat_permissions(update.message.chat_id, perms)
    await update.message.reply_text("🔒 *GRUPO FECHADO:* ordem programada e executada.", parse_mode="Markdown")

async def abrir_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await update.message.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    perms = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await context.bot.set_chat_permissions(update.message.chat_id, perms)
    await update.message.reply_text("✅ *GRUPO ABERTO:* Agora todos os membros podem enviar mensagens.", parse_mode="Markdown")

async def meu_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    await update.message.reply_text("✅ Seu ID do Telegram\n🆔: <" + str(uid) + ">")

app = ApplicationBuilder().token(token).connect_timeout(30).read_timeout(30).write_timeout(30).pool_timeout(30).build()

GRUPO_PRINCIPAL = -1003789672313

def load_grupos_autorizados():
    u = load_usos()
    dados = u.get("grupos_autorizados", [])
    if isinstance(dados, list):
        return {str(gid): {"expira_em": None, "limite_diario": None, "usados_hoje": {"data": "", "qtd": 0}} for gid in dados}
    return dados

def save_grupos_autorizados(grupos):
    u = load_usos()
    u["grupos_autorizados"] = grupos
    save_usos(u)

def checar_limite_grupo_diario(chat_id):
    grupos_atuais = load_grupos_autorizados()
    info = grupos_atuais.get(str(chat_id))
    if not info or not isinstance(info, dict):
        return True
    limite = info.get("limite_diario")
    if not limite:
        return True
    hoje = (datetime.utcnow() - timedelta(hours=3)).strftime("%d/%m/%Y")
    usados = info.get("usados_hoje") or {"data": "", "qtd": 0}
    if usados.get("data") != hoje:
        usados = {"data": hoje, "qtd": 0}
    if usados["qtd"] >= limite:
        info["usados_hoje"] = usados
        grupos_atuais[str(chat_id)] = info
        save_grupos_autorizados(grupos_atuais)
        return False
    usados["qtd"] += 1
    info["usados_hoje"] = usados
    grupos_atuais[str(chat_id)] = info
    save_grupos_autorizados(grupos_atuais)
    return True

def load_liberados():
    u = load_usos()
    return set(u.get("acessos_liberados", []))

def save_liberados(liberados):
    u = load_usos()
    u["acessos_liberados"] = list(liberados)
    save_usos(u)

def eh_dono(user_id):
    try:
        uid = int(user_id)
    except Exception:
        return False
    if uid == DONO_ID:
        return True
    return uid in load_liberados()

GRUPOS_AUTORIZADOS = set()

async def checar_grupo_autorizado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat is None or chat.type == "private":
        return True
    if update.message and update.message.from_user and update.message.from_user.id == DONO_ID:
        return True
    chat_id = chat.id
    grupos_atuais = load_grupos_autorizados()
    if chat_id == GRUPO_PRINCIPAL:
        return True
    if str(chat_id) in grupos_atuais:
        info = grupos_atuais[str(chat_id)]
        expira_em = info.get("expira_em") if isinstance(info, dict) else None
        if expira_em:
            try:
                data_exp = datetime.strptime(expira_em, "%d/%m/%Y")
                agora = datetime.utcnow() - timedelta(hours=3)
                if agora > data_exp:
                    grupos_atuais.pop(str(chat_id), None)
                    save_grupos_autorizados(grupos_atuais)
                    try:
                        await context.bot.send_message(chat_id, "⏰ A autorização deste grupo expirou.")
                        await context.bot.leave_chat(chat_id)
                    except Exception:
                        pass
                    return False
            except Exception:
                pass
        return True
    try:
        await context.bot.send_message(chat_id, "❌ Este bot não está autorizado a funcionar neste grupo.")
        await context.bot.leave_chat(chat_id)
    except Exception:
        pass
    return False

async def addgrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    args = context.args
    if not args or len(args) not in (2, 3):
        await update.message.reply_text("Uso:\n/addgrupo <dias> <limite_diario>  (dentro do grupo)\nou\n/addgrupo <id_do_grupo> <dias> <limite_diario>")
        return
    try:
        if len(args) == 2:
            gid = update.effective_chat.id
            dias = int(args[0])
            limite = int(args[1])
        else:
            gid = int(args[0])
            dias = int(args[1])
            limite = int(args[2])
    except ValueError:
        await update.message.reply_text("Parâmetros inválidos.")
        return
    expira_em = (datetime.utcnow() - timedelta(hours=3) + timedelta(days=dias)).strftime("%d/%m/%Y")
    grupos_atuais = load_grupos_autorizados()
    grupos_atuais[str(gid)] = {"expira_em": expira_em, "limite_diario": limite, "usados_hoje": {"data": "", "qtd": 0}}
    save_grupos_autorizados(grupos_atuais)
    await update.message.reply_text(f"✅ Grupo {gid} autorizado!\n📅 Validade: {dias} dias (expira em {expira_em})\n🔢 Limite: {limite} IDs por dia")

async def removergrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removergrupo <id_do_grupo>")
        return
    try:
        gid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return
    grupos_atuais = load_grupos_autorizados()
    grupos_atuais.pop(str(gid), None)
    save_grupos_autorizados(grupos_atuais)
    try:
        await context.bot.send_message(gid, "❌ Este bot foi desautorizado deste grupo.")
        await context.bot.leave_chat(gid)
    except Exception:
        pass
    await update.message.reply_text(f"✅ Grupo {gid} removido e bot saiu de lá.")

async def checkgrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    grupos_atuais = load_grupos_autorizados()
    linhas = [f"🏠 Principal: {GRUPO_PRINCIPAL}"]
    for gid in list(grupos_atuais.keys()):
        try:
            chat = await context.bot.get_chat(gid)
            nome = chat.title or "Sem nome"
        except Exception:
            nome = "Desconhecido"
        linhas.append(f"{nome}: {gid}")
    msg = "📋 Grupos usando o bot:\n\n" + "\n".join(linhas)
    await update.message.reply_text(msg)

async def liberacesso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != DONO_ID:
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /liberacesso <id_do_usuario>")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return
    liberados = load_liberados()
    liberados.add(uid)
    save_liberados(liberados)
    await update.message.reply_text(f"✅ Acesso total liberado para o ID {uid}.")

async def removeracesso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != DONO_ID:
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removeracesso <id_do_usuario>")
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return
    liberados = load_liberados()
    liberados.discard(uid)
    save_liberados(liberados)
    await update.message.reply_text(f"🗑️ Acesso removido do ID {uid}.")

async def listliberados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != DONO_ID:
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    liberados = load_liberados()
    if not liberados:
        await update.message.reply_text("Nenhum acesso liberado no momento.")
        return
    msg = "🔓 IDs com acesso total liberado:\n\n" + "\n".join(str(uid) for uid in liberados)
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("liberacesso", liberacesso))
app.add_handler(CommandHandler("removeracesso", removeracesso))
app.add_handler(CommandHandler("listliberados", listliberados))
app.add_handler(CommandHandler("addgrupo", addgrupo))
app.add_handler(CommandHandler("removergrupo", removergrupo))
app.add_handler(CommandHandler("checkgrupo", checkgrupo))

async def filtro_grupo_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    autorizado = await checar_grupo_autorizado(update, context)
    if not autorizado:
        raise ApplicationHandlerStop

app.add_handler(MessageHandler(filters.ALL, filtro_grupo_global), group=-1)

async def post_init(application):
    asyncio.create_task(autolike_loop(application))

app.post_init = post_init

async def info_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /infoopen <access_id>")
        return
    access_id = context.args[0]
    try:
        resp = requests.get(f"{BASE_URL}/info-open", params={"key": FRIFAS_KEY, "access_id": access_id}, timeout=30)
        data = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        return
    if data.get("sucesso"):
        d = data["data"]
        await update.message.reply_text(
            f"📊 Info do Open\n"
            f"🆔 ID: {d['access_id']}\n"
            f"👥 Contas: {d['contas_registradas']}/{d['max_contas']}\n"
            f"✅ Ativas: {d['contas_ativas']} | Concluídas: {d['contas_concluidas']}\n"
            f"🔗 {d['checkpage_url']}"
        )
    else:
        await update.message.reply_text(f"❌ Erro: {data.get('status')}")

async def list_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /listopen <access_id>")
        return
    access_id = context.args[0]
    try:
        resp = requests.get(f"{BASE_URL}/list-open", params={"key": FRIFAS_KEY, "access_id": access_id}, timeout=30)
        data = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        return
    if data.get("sucesso"):
        contas = data["data"]
        msg = f"📋 Contas no Open ({len(contas)}):\n\n"
        for c in contas:
            msg += (
                f"👤 {c['conta']['player']} | {c['conta']['uid']}\n"
                f"❤️ Enviados: {c['likes']['enviados']} | "
                f"Dias restantes: {c['progresso']['dias_restantes']}\n\n"
            )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(f"❌ Erro: {data.get('status')}")

app.add_handler(CommandHandler("infoopen", info_open))
app.add_handler(CommandHandler("info", info_player))

JSONBIN_KEY = "$2a$10$2zUobgrptNlTik8VoI2BhuWqDxXp/L9WwS1tOLHdSF5Wmo7wss2XS"
JSONBIN_ID = "6a308646da38895dfec6a1b9"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"
JSONBIN_HEADERS = {"X-Master-Key": JSONBIN_KEY, "Content-Type": "application/json"}

def load_vips():
    try:
        r = requests.get(JSONBIN_URL + "/latest", headers=JSONBIN_HEADERS)
        return r.json().get("record", {}).get("vips", {})
    except Exception as e:
        print(f"[LOAD_VIPS ERRO] {type(e).__name__}: {e}", flush=True)
        return {}

def save_vips(vips):
    try:
        r = requests.get(JSONBIN_URL + "/latest", headers=JSONBIN_HEADERS)
        data = r.json().get("record", {})
        data["vips"] = vips
        pr = requests.put(JSONBIN_URL, headers=JSONBIN_HEADERS, json=data)
        print(f"[SAVE_VIPS] status={pr.status_code} resp={pr.text[:200]}", flush=True)
    except Exception as e:
        print(f"[SAVE_VIPS ERRO] {type(e).__name__}: {e}", flush=True)

async def addvip(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if len(context.args) < 3:
        await update.message.reply_text("Uso: /addvip <dias> <usos_por_dia> <id_usuario>")
        return
    dias = int(context.args[0])
    usos = int(context.args[1])
    uid = str(context.args[2])
    vips = load_vips()
    vips[uid] = {
            "nome": context.args[3] if len(context.args) > 3 else "Desconhecido",
            "data_inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expira": (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S"),
        "usos_por_dia": usos,
        "usos_hoje": 0,
        "ultimo_reset": datetime.now().strftime("%Y-%m-%d")
    }
    save_vips(vips)
    await update.message.reply_text("👑 VIP ATIVO\n\n👤 " + str(context.args[3] if len(context.args) > 3 else "Desconhecido") + "\n🆔 " + str(uid) + "\n📅 Inicio: " + datetime.now().strftime("%d/%m/%Y") + "  Expira: " + (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y") + "\n🔄 Usos/dia: " + str(usos))
async def removevip(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removevip <id_usuario>")
        return
    uid = str(context.args[0])
    vips = load_vips()
    if uid in vips:
        del vips[uid]
        save_vips(vips)
        await update.message.reply_text("🗑️ VIP REMOVIDO\n\n🆔 UID: " + str(uid) + "\n🚫 vip desativado.")
    else:
        await update.message.reply_text("Usuário não encontrado no VIP!")

async def listvip(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ VOCÊ NÃO TEM PERMISSÃO PRA USA OS COMANDOS DO BOT\n\nCOMPRE O PLANO PRA PODE USAR TODOS OS COMANDOS DO BOT 🔥\n\n✅️ ENTRE EM CONTATO COM O DONO (82) 98863-1900 WHATSAPP\nE ADQUIRA JÁ SEU PLANO MENSAL OU SEMANAL")
        return
    vips = load_vips()
    if not vips:
        await update.message.reply_text("Nenhum VIP ativo!")
        return
    msgs = []
    msg = "👑 VIPs ATIVOS:\n\n"
    now = datetime.now()
    for uid, data in list(vips.items()):
        try:
            if now > datetime.strptime(data['expira'], "%Y-%m-%d %H:%M:%S"):
                del vips[uid]
                save_vips(vips)
                continue
        except:
            pass
        linha = f"👤 {data.get('nome', 'Desconhecido')}\n🆔 {uid}\n📅 Inicio: {data.get('data_inicio', '-')}  Expira: {data['expira']}\n🔄 Usos/dia: {data['usos_por_dia']}\n\n"
        if len(msg) + len(linha) > 3500:
            msgs.append(msg)
            msg = "👑 VIPs ATIVOS (continuação):\n\n"
        msg += linha
    msgs.append(msg)
    for m in msgs:
        await update.message.reply_text(m)

app.add_handler(CommandHandler("addvip", addvip))
app.add_handler(CommandHandler("removevip", removevip))
app.add_handler(CommandHandler("listvip", listvip))
app.add_handler(CommandHandler("meususos", meususos))
app.add_handler(CommandHandler("usosgeral", usosgeral))
def checar_vip(uid):
    vips = load_vips()
    uid = str(uid)
    if uid not in vips:
        return False, 0, "sem_vip"
    v = vips[uid]
    if datetime.now() > datetime.strptime(v["expira"], "%Y-%m-%d %H:%M:%S"):
        del vips[uid]
        save_vips(vips)
        return False, 0, "expirado"
    hoje = datetime.now().strftime("%Y-%m-%d")
    if v["ultimo_reset"] != hoje:
        v["usos_hoje"] = 0
        v["ultimo_reset"] = hoje
        save_vips(vips)
    if v["usos_hoje"] >= v["usos_por_dia"]:
        return False, 0, "limite"
    return True, v["usos_por_dia"] - v["usos_hoje"], "ok"

def incrementar_uso_vip(uid):
    vips = load_vips()
    uid = str(uid)
    if uid in vips:
        vips[uid]["usos_hoje"] = vips[uid].get("usos_hoje", 0) + 1
        save_vips(vips)
app.add_handler(CommandHandler("abrgrupo", abrir_grupo))
app.add_handler(CommandHandler("fechgrupo", fechar_grupo))
app.add_handler(CommandHandler("meuid", meu_id))

async def stats(update, context):
    usos = load_usos()
    vips = load_vips()
    total_usuarios = len(usos.get("usuarios_bio", []))
    total_likes_hoje = usos.get("likes_geral", {}).get("qtd", 0)
    total_vips = len(vips)
    msg = (
        "📊 *Estatísticas do Bot*\n\n"
        f"👥 Usuários cadastrados: *{total_usuarios}*\n"
        f"💗 Likes enviados hoje: *{total_likes_hoje}*\n"
        f"⭐ VIPs ativos: *{total_vips}*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, boas_vindas))

async def tabela(update, context):
    texto = (
        "✅ *LIKES MANUALMENTE*\n"
        "*TABELA DE LIKES VIA ID 👍*\n\n"
        "• 200 LIKES 💰 R$2,00 \`1 DIA\`\n"
        "• 400 LIKES 💰 R$4,00 \`2 DIA\`\n"
        "• 600 LIKES 💰 R$6,00 \`3 DIA\`\n"
        "• 800 LIKES 💰 R$8,00 \`4 DIA\`\n"
        "• 1\.000 LIKES 💰 R$10,00 \`5 DIA\`\n"
        "• 2\.000 LIKES 💰 R$15,00 \`10 DIA\`\n"
        "• 3\.000 LIKES 💰 R$20,00 \`15 DIA\`\n"
        "• 4\.000 LIKES 💰 R$25,00 \`20 DIA\`\n"
        "• 5\.000 LIKES 💰 R$30,00 \`25 DIA\`\n"
        "• 10\.000 LIKES 💰 R$55,00 \`50 DIA\`\n\n"
        "● Caindo de *200* likes por dia\!\n\n"
        "*Semanal R$12,00* — 1\.400 👍\n"
        "*Mensal R$35,00* — 6\.000 👍\n\n"
        "[🛒 CLIQUE AQUI PRA COMPRAR](https://wa.me/5582988631900?text=OL%C3%81%20REBELDE,%20QUERO%20ESCOLHER%20O%20PLANO%20DE%20LIKES%20POR%20FREE%20FIRE%20POR%20FAVOR%20%F0%9F%98%8D%E2%9C%A8%EF%B8%8F)"
    )
    await update.message.reply_text(texto, parse_mode="MarkdownV2", disable_web_page_preview=True)

app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("tabela", tabela))
async def token(update, context):
    texto = (
        "🎁 *ACESSE AO LINK AQUI EM BAIXO*\n\n"
        "👇\n\n"
        "https://discstore.recargajogo.com.br/"
    )
    await update.message.reply_text(texto, parse_mode="Markdown", disable_web_page_preview=True)

app.add_handler(CommandHandler("token", token))

IA_COOLDOWN = {}

async def ia(update, context):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID):
        valido, restantes, motivo = checar_vip(uid)
        if not valido:
            await update.message.reply_text("❌ Esse comando é exclusivo para VIPs!\n\nEntre em contato com o dono para adquirir.\n📱 (82) 98863-1900 WhatsApp")
            return
    if not context.args:
        await update.message.reply_text("Uso: /ia <pergunta>")
        return
    import time as _time_ia
    _agora_ia = _time_ia.time()
    _ultimo_ia = IA_COOLDOWN.get(uid, 0)
    if _agora_ia - _ultimo_ia < 30:
        _restante_ia = int(30 - (_agora_ia - _ultimo_ia))
        await update.message.reply_text(f"⏳ Aguarde {_restante_ia}s para usar o /ia novamente.")
        return
    IA_COOLDOWN[uid] = _agora_ia
    prompt = " ".join(context.args)
    chat_id = str(update.message.from_user.id)[:6]
    await update.message.reply_text("🤖 Processando sua pergunta...")
    try:
        import requests as req, json
        resp = req.get(
            "https://fluxdevservice.com/api/ia/flux-chat",
            params={"key": FRIFAS_KEY, "prompt": prompt, "chat_id": chat_id, "model": "flux-thinking-search-max"},
            stream=True, timeout=120
        )
        resposta = ""
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if data.get("type") in ("flux-text-start", "flux-text"):
                        resposta += data.get("result", "")
                except:
                    pass
        if resposta:
            await update.message.reply_text(f"🤖 *Flux IA:*\n\n{resposta}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Não obtive resposta da IA. Tente novamente.")
    except Exception as e:
        await update.message.reply_text("🔧 Comando /ia temporariamente indisponível. Tente novamente mais tarde.")

app.add_handler(CommandHandler("ia", ia))

async def listautolike(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ Apenas o dono pode usar esse comando.")
        return
    uids_auto = load_auto()
    if not uids_auto:
        await update.message.reply_text("Nenhum auto-like ativo!")
        return
    msg = "🔄 AUTO-LIKES ATIVOS:\n\n"
    for uid, info in uids_auto.items():
        if isinstance(info, dict):
            msg += f"👤 UID: {uid}\n📅 Dias restantes: {info.get('dias_restantes','?')}\n🗓 Criado em: {info.get('criado_em','?')}\n\n"
        else:
            msg += f"👤 UID: {uid}\n(sem controle de dias)\n\n"
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("listautolike", listautolike))

async def resumoautolike(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ Apenas o dono pode usar esse comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /resumoautolike <uid>")
        return
    uid = context.args[0]
    uids_auto = load_auto()
    info = uids_auto.get(uid)
    if not info or not isinstance(info, dict):
        await update.message.reply_text("❌ UID não encontrado ou sem histórico.")
        return
    historico = info.get("historico", {})
    if not historico:
        await update.message.reply_text("Nenhum registro de likes ainda para esse UID.")
        return
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    msg = f"📊 RESUMO AUTO-LIKE\n🆔 UID: {uid}\n\n"
    for data_str in sorted(historico.keys(), key=lambda d: datetime.strptime(d, "%d/%m/%Y")):
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        dia_semana = dias_semana[data_obj.weekday()]
        qtd = historico[data_str]
        msg += f"📅 {data_str} ({dia_semana}): {qtd} likes\n"
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("resumoautolike", resumoautolike))

async def ytmp3(update, context):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID):
        valido, restantes, motivo = checar_vip(uid)
        if not valido:
            await update.message.reply_text("❌ Esse comando é exclusivo para VIPs!\n\nEntre em contato com o dono para adquirir.\n📱 (82) 98863-1900 WhatsApp")
            return
    if not context.args:
        await update.message.reply_text("Uso: /ytmp3 <nome ou link do video>")
        return
    query = " ".join(context.args)
    msg_id = str(update.message.message_id)
    usos = load_usos()
    processados = usos.get("processados_ytmp3", [])
    if msg_id in processados:
        return
    processados.append(msg_id)
    if len(processados) > 100:
        processados = processados[-100:]
    usos["processados_ytmp3"] = processados
    save_usos(usos)
    await update.message.reply_text("🎵 Processando áudio, aguarde...")
    try:
        resp = requests.get(f"https://fluxdevservice.com/api/download/ytmp3", params={"key": FRIFAS_KEY, "q": query}, timeout=100)
        data = resp.json()
        if data.get("success"):
            d = data["data"]
            media_url = f"https://fluxdevservice.com{d['url']}"
            await update.message.reply_audio(audio=media_url, caption=f"🎵 Áudio baixado com sucesso!")
        else:
            await update.message.reply_text(f"❌ Erro: {data.get('message','Não foi possível processar')}")
    except Exception as e:
        erro_msg = await update.message.reply_text(f"❌ Erro: {str(e)}")
        await asyncio.sleep(8)
        try:
            await erro_msg.delete()
        except Exception:
            pass

async def ytmp4(update, context):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID):
        valido, restantes, motivo = checar_vip(uid)
        if not valido:
            await update.message.reply_text("❌ Esse comando é exclusivo para VIPs!\n\nEntre em contato com o dono para adquirir.\n📱 (82) 98863-1900 WhatsApp")
            return
    if not context.args:
        await update.message.reply_text("Uso: /ytmp4 <nome ou link do video>")
        return
    query = " ".join(context.args)
    await update.message.reply_text("🎬 Processando vídeo, aguarde...")
    try:
        resp = requests.get(f"https://fluxdevservice.com/api/download/ytmp4", params={"key": FRIFAS_KEY, "q": query}, timeout=100)
        data = resp.json()
        if data.get("success"):
            d = data["data"]
            media_url = f"https://fluxdevservice.com{d['url']}"
            await update.message.reply_video(video=media_url, caption=f"🎬 Vídeo baixado com sucesso!")
        else:
            await update.message.reply_text(f"❌ Erro: {data.get('message','Não foi possível processar')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")

app.add_handler(CommandHandler("ytmp3", ytmp3))
app.add_handler(CommandHandler("ytmp4", ytmp4))

async def promove(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ Apenas o dono pode usar esse comando.")
        return
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("Uso: /promove <id> ou responda a mensagem do usuário")
            return
    else:
        await update.message.reply_text("Uso: /promove <id> ou responda a mensagem do usuário")
        return
    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False
        )
        await update.message.reply_text(f"✅ Usuário {target_id} promovido a ADM!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao promover: {str(e)}\n\nVerifique se o bot é admin com permissão de promover membros.")

async def rebaixa(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("⚠️ Apenas o dono pode usar esse comando.")
        return
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("Uso: /rebaixa <id> ou responda a mensagem do usuário")
            return
    else:
        await update.message.reply_text("Uso: /rebaixa <id> ou responda a mensagem do usuário")
        return
    try:
        await context.bot.promote_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        await update.message.reply_text(f"✅ ADM removido do usuário {target_id}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao rebaixar: {str(e)}\n\nVerifique se o bot é admin com permissão de promover membros.")

app.add_handler(CommandHandler("promove", promove))
app.add_handler(CommandHandler("rebaixa", rebaixa))


# fix

async def passe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /passe <uid>")
        return
    player_id = context.args[0]
    await update.message.reply_text("🔎 Buscando informações do jogador, aguarde...")
    try:
        resp_info = requests.get(f"https://passe.soyxapasse.com.br/api/v1/consultar/{player_id}", params={"token": PASSE_API_TOKEN}, timeout=40)
        data_info = resp_info.json()
    except Exception:
        await update.message.reply_text("❌ Não foi possível verificar o jogador. Tente novamente.")
        return
    if not data_info.get("success"):
        await update.message.reply_text("❌ Jogador não encontrado. Verifique o UID.")
        return
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    nick = data_info.get("nickname", "?")
    nivel = data_info.get("level", "?")
    regiao = data_info.get("regiao", "?")
    keyboard = [[
        InlineKeyboardButton("✅ Confirmar", callback_data=f"passe_confirm_{player_id}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="passe_cancel")
    ]]
    markup = InlineKeyboardMarkup(keyboard)
    msg = (
        f"🎁 CONFIRMAR ENVIO PASSE BOOYAH\n\n"
        f"👤 Nick: {nick}\n"
        f"🆔 ID: {player_id}\n"
        f"⭐ Level: {nivel}\n"
        f"🌍 Região: {regiao}\n\n"
        f"Confirma o envio do passe para esse jogador?"
    )
    await update.message.reply_text(msg, reply_markup=markup)

async def passe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "passe_cancel":
        await query.edit_message_text("❌ Envio de passe cancelado.")
        return
    if query.data.startswith("passe_confirm_"):
        player_id = query.data.replace("passe_confirm_", "")
        await query.edit_message_text("📦 Enviando passe, aguarde...")
        try:
            resp = post_com_retry(
                "https://passe.soyxapasse.com.br/api/v1/order",
                headers={
                    "Content-Type": "application/json",
                    "X-Bot-Name": "RebeldeFF"
                },
                json={"token": PASSE_API_TOKEN, "player_id": player_id},
                timeout=30
            )
            if resp.status_code != 200 or not resp.text.strip():
                raise Exception(f"API fora do ar (status {resp.status_code}): {resp.text[:200] or 'resposta vazia'}")
            try:
                data = resp.json()
            except ValueError:
                raise Exception(f"API retornou algo inválido (status {resp.status_code}): {resp.text[:200]}")
            if data.get("success"):
                jogador = data.get("jogador", {})
                nick = jogador.get("nickname", player_id)
                nivel = jogador.get("level", "?")
                from datetime import datetime, timezone, timedelta
                agora = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
                msg = (
                    f"✅ Passe enviado com sucesso!\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📦 Produto: Passe Booyah 🎗\n"
                    f"👤 Jogador: {nick}\n"
                    f"🆔 UID: {player_id}\n"
                    f"⭐ Nível: {nivel}\n"
                    f"📅 Data: {agora}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🏅 OBRIGADO PELA COMPRA!\n"
                    f"༒REBELDE༒ VENDAS"
                )
                await query.edit_message_text(msg)
            else:
                await query.edit_message_text(f"❌ {data.get('message', 'Erro ao enviar passe.')}")
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")

app.add_handler(CommandHandler("passe", passe))

async def consultarpasse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /consultarpasse <uid>")
        return
    player_id = context.args[0]
    await update.message.reply_text("🔎 Consultando, aguarde...")
    try:
        resp = requests.get(
            f"https://passe.soyxapasse.com.br/api/v1/consultar/{player_id}",
            params={"token": PASSE_API_TOKEN},
            timeout=30
        )
        data = resp.json()
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        return
    if data.get("success"):
        msg = (
            f"🔍 CONSULTA DE JOGADOR\n\n"
            f"👤 Nick: {data.get('nickname', '?')}\n"
            f"🆔 ID: {player_id}\n"
            f"⭐ Level: {data.get('level', '?')}\n"
            f"❤️ Likes: {data.get('curtidas', '?')}\n"
            f"🌍 Região: {data.get('regiao', '?')}"
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(f"❌ {data.get('message', 'ID não encontrado.')}")

app.add_handler(CommandHandler("consultarpasse", consultarpasse))

async def idgrupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 ID deste chat: {update.effective_chat.id}")

app.add_handler(CommandHandler("idgrupo", idgrupo))




app.add_handler(CallbackQueryHandler(passe_callback, pattern="^passe_"))

async def agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /agendar <uid>")
        return
    player_id = context.args[0]
    await update.message.reply_text("🔍 Buscando informações do jogador, aguarde...")
    try:
        resp_info = requests.get(f"https://passe.soyxapasse.com.br/api/v1/consultar/{player_id}", params={"token": PASSE_API_TOKEN}, timeout=40)
        data_info = resp_info.json()
    except Exception:
        await update.message.reply_text("❌ Não foi possível verificar o jogador. Tente novamente.")
        return
    if not data_info.get("success"):
        await update.message.reply_text("❌ Jogador não encontrado. Verifique o UID.")
        return
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    nick = data_info.get("nickname", "?")
    nivel = data_info.get("level", "?")
    regiao = data_info.get("regiao", "?")
    keyboard = [[
        InlineKeyboardButton("✅ Confirmar", callback_data=f"agendar_confirm_{player_id}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="agendar_cancel")
    ]]
    markup = InlineKeyboardMarkup(keyboard)
    msg = (
        f"📅 CONFIRMAR AGENDAMENTO\n\n"
        f"👤 Nick: {nick}\n"
        f"🆔 ID: {player_id}\n"
        f"⭐ Level: {nivel}\n"
        f"🌍 Região: {regiao}\n\n"
        f"Confirma o agendamento para esse jogador?"
    )
    await update.message.reply_text(msg, reply_markup=markup)

async def agendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "agendar_cancel":
        await query.edit_message_text("❌ Agendamento cancelado.")
        return
    if query.data.startswith("agendar_confirm_"):
        player_id = query.data.replace("agendar_confirm_", "")
        await query.edit_message_text("📦 Agendando, aguarde...")
        try:
            try:
                resp_nome = requests.get(f"https://passe.soyxapasse.com.br/api/v1/consultar/{player_id}", params={"token": PASSE_API_TOKEN}, timeout=30)
                data_nome = resp_nome.json()
                nome_agendamento = data_nome.get("nickname", player_id)
                nick_confirmado = data_nome.get("nickname", player_id)
                nivel_confirmado = data_nome.get("level", "?")
            except Exception:
                nome_agendamento = player_id
            resp = requests.post(
                "https://passe.soyxapasse.com.br/api/agendamentos/agendar",
                headers={"Content-Type": "application/json"},
                json={"token": PASSE_API_TOKEN, "player_id": player_id, "nome": nome_agendamento},
                timeout=30
            )
            if resp.status_code != 200 or not resp.text.strip():
                raise Exception(f"API fora do ar (status {resp.status_code}): {resp.text[:200] or 'resposta vazia'}")
            try:
                data = resp.json()
            except ValueError:
                raise Exception(f"API retornou algo inválido (status {resp.status_code}): {resp.text[:200]}")
            if data.get("success"):
                jogador = data.get("jogador", {})
                nick = nick_confirmado
                nivel = nivel_confirmado
                agendamento_id = data.get("agendamento_id", "?")
                msg = (
                    f"✅ Agendamento realizado com sucesso!\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"📅 ID do agendamento: {agendamento_id}\n"
                    f"👤 Jogador: {nick}\n"
                    f"🆔 UID: {player_id}\n"
                    f"⭐ Nível: {nivel}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"💎 OBRIGADO PELA COMPRA!\n"
                    f"༒REBELDE༒ VENDAS"
                )
                from datetime import datetime as _dt
                try:
                    _usos_ag = load_usos()
                    if "agendamentos_passe" not in _usos_ag:
                        _usos_ag["agendamentos_passe"] = []
                    _usos_ag["agendamentos_passe"].append({
                        "id": agendamento_id,
                        "uid": player_id,
                        "nick": nick,
                        "nivel": nivel,
                        "data": _dt.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    save_usos(_usos_ag)
                except Exception:
                    pass
                await query.edit_message_text(msg)
            else:
                await query.edit_message_text(f"❌ {data.get('message', 'Erro ao agendar.')}")
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")

app.add_handler(CommandHandler("agendar", agendar))
app.add_handler(CallbackQueryHandler(agendar_callback, pattern="^agendar_"))

async def listagenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("\u274C Voc\u00ea n\u00e3o tem permiss\u00e3o para usar este comando.")
        return
    from datetime import datetime as _dt3
    usos_ag = load_usos()
    todos = usos_ag.get("agendamentos_passe", [])
    mes_atual = _dt3.now().strftime("%Y-%m")
    do_mes = [a for a in todos if a.get("data", "").startswith(mes_atual)]
    if not do_mes:
        await update.message.reply_text("\U0001F4C5 Nenhum agendamento neste m\u00eas ainda.")
        return
    msg = f"\U0001F4C5 *AGENDAMENTOS DO M\u00caS* ({mes_atual})\n\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\n"
    for a in do_mes:
        msg += (
            f"\U0001F464 {a.get('nick', '?')}\n"
            f"   UID: {a.get('uid', '?')}\n"
            f"   N\u00edvel: {a.get('nivel', '?')}\n"
            f"   Data: {a.get('data', '?')}\n"
            f"   ID: {a.get('id', '?')}\n\n"
        )
    msg += f"Total: {len(do_mes)} agendamento(s) este m\u00eas."
    await update.message.reply_text(msg, parse_mode="Markdown")

app.add_handler(CommandHandler("listagenda", listagenda))





def load_passe_usuarios():
    usos = load_usos()
    return set(usos.get("passe_usuarios", []))

def save_passe_usuarios(usuarios):
    usos = load_usos()
    usos["passe_usuarios"] = list(usuarios)
    save_usos(usos)

PASSE_USUARIOS = load_passe_usuarios()
PROCESSADOS = set()

async def addpasse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /addpasse <id_telegram>")
        return
    alvo = context.args[0]
    PASSE_USUARIOS.add(alvo)
    save_passe_usuarios(PASSE_USUARIOS)
    await update.message.reply_text(f"✅ Usuário {alvo} autorizado a usar /passe.")

async def removepasse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /removepasse <id_telegram>")
        return
    alvo = context.args[0]
    PASSE_USUARIOS.discard(alvo)
    save_passe_usuarios(PASSE_USUARIOS)
    await update.message.reply_text(f"✅ Usuário {alvo} removido do acesso ao /passe.")

app.add_handler(CommandHandler("addpasse", addpasse))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("removepasse", removepasse))

FREEFIRE_API_KEY = "vl_33b37278a62449f959435a41a2370df6d324dda27c4409bd"

def enviar_like(uid, region="BR"):
    url = "https://Like200.soyxapasse.com.br/api/v1/enviar"
    params = {"key": FREEFIRE_API_KEY, "uid": uid, "region": region}
    try:
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except Exception as e:
        return {"erro": str(e)}


async def like_command(update, context):
    if not eh_dono(update.message.from_user.id):
        valido, restantes, motivo = checar_vip(str(update.message.from_user.id))
        if not valido:
            if motivo == "limite":
                await update.message.reply_text("🚫 Limite diario atingido!\n\nVoce ja usou todos os seus IDs disponiveis hoje. Volte amanha para usar novamente.")
                return
            else:
                await update.message.reply_text("❌ Seu VIP expirou ou voce nao tem VIP ativo!\n\nEntre em contato com o dono para renovar.\n📱 (82) 98863-1900 WhatsApp")
                return
    if not context.args:
        await update.message.reply_text("Uso: /like <ID_DO_JOGADOR>")
        return
    uid = context.args[0]
    region = context.args[1] if len(context.args) > 1 else "BR"
    chat_atual = update.effective_chat
    if chat_atual and chat_atual.type != "private" and chat_atual.id != GRUPO_PRINCIPAL:
        if not checar_limite_grupo_diario(chat_atual.id):
            await update.message.reply_text("🚫 Limite diário de IDs deste grupo foi atingido! Tente novamente amanhã.")
            return
    await update.message.reply_text("⏳ Enviando likes...")
    resultado = enviar_like(uid, region)

    if resultado.get("sucesso"):
        contar_uso(update.message.from_user.id)
        msg = (
            f"╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│  ✅️ LIKES ENVIADOS  COM SUCESSO 👍\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"│  👤 Jogador: {resultado['nickname']}\n"
            f"│  🆔 UID: {resultado['uid']}\n"
            f"│ 🌎 Região: {resultado['regiao']}\n"
            f"│  📈 Likes antes: {resultado['likes_antes']}\n"
            f"│  🚀 Enviados agora: {resultado['likes_enviados']}\n"
            f"│ ✅ Likes  Depois: {resultado['likes_depois']}\n\n"
            f"🔱 Dono: ༒REBELDE༒VENDAS"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    erro = resultado.get("erro", "desconhecido")
    mensagens_erro = {
        "limite_diario": "⛔ Limite diário de likes atingido. Tenta amanhã!",
        "id_nao_encontrado": "❌ Esse ID de jogador não existe.",
        "ja_enviado": "⚠️ Esse ID já recebeu likes hoje. Tenta mais tarde.",
        "em_processamento": "⏳ Esse ID já está sendo processado. Aguarda um pouco.",
        "uid_invalido": "❌ ID inválido. Manda só números.",
        "sem_chave": "🔑 Erro de configuração (API key ausente). Avisa o admin.",
        "chave_invalida": "🔑 Erro de configuração (API key inválida). Avisa o admin.",
        "sem_plano": "❌ Sem plano ativo na API de likes. Avisa o admin.",
        "servidor_lotado": "🔄 Servidor de likes ocupado. Tenta de novo em instantes.",
        "falha": "⚠️ Falha temporária no envio. Tenta de novo.",
        "timeout": "⏱️ O envio demorou demais. Tenta de novo.",
    }
    texto = mensagens_erro.get(erro, f"❌ Erro: {resultado.get('mensagem', erro)}")
    await update.message.reply_text(texto)

app.add_handler(CommandHandler("like", like_command))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(menu_|cmd_)"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link))

mutados_lista = {}

async def unban(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not context.args:
        await msg.reply_text("Uso: /unban <ID do usuario>")
        return
    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(msg.chat_id, user_id, only_if_banned=True)
        await msg.reply_text(f"✅ Usuario {user_id} foi desbanido.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def link_cmd(update, context):
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    try:
        invite_link = await context.bot.export_chat_invite_link(msg.chat_id)
        await msg.reply_text(f"🔗 Link do grupo:\n{invite_link}")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def title_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not context.args:
        await msg.reply_text("Uso: /title <novo titulo>")
        return
    novo_titulo = " ".join(context.args)
    try:
        await context.bot.set_chat_title(msg.chat_id, novo_titulo)
        await msg.reply_text("✅ Titulo do grupo alterado.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def desc_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not context.args:
        await msg.reply_text("Uso: /desc <nova descricao>")
        return
    nova_desc = " ".join(context.args)
    try:
        await context.bot.set_chat_description(msg.chat_id, nova_desc)
        await msg.reply_text("✅ Descricao do grupo alterada.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def pin_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not msg.reply_to_message:
        await msg.reply_text("Responda a mensagem que deseja fixar com /pin")
        return
    try:
        await context.bot.pin_chat_message(msg.chat_id, msg.reply_to_message.message_id)
        await msg.reply_text("📌 Mensagem fixada.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def unpin_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not msg.reply_to_message:
        await msg.reply_text("Responda a mensagem que deseja desafixar com /unpin")
        return
    try:
        await context.bot.unpin_chat_message(msg.chat_id, msg.reply_to_message.message_id)
        await msg.reply_text("📌 Mensagem desafixada.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def mute_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not msg.reply_to_message:
        await msg.reply_text("Responda a mensagem do usuario que deseja silenciar com /mute")
        return
    alvo = msg.reply_to_message.from_user
    try:
        perms = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(msg.chat_id, alvo.id, perms)
        mutados_lista[alvo.id] = alvo.username or alvo.first_name
        await msg.reply_text(f"🔇 Usuario {alvo.username or alvo.first_name} foi silenciado.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def unmute_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not msg.reply_to_message:
        await msg.reply_text("Responda a mensagem do usuario que deseja dessilenciar com /unmute")
        return
    alvo = msg.reply_to_message.from_user
    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await context.bot.restrict_chat_member(msg.chat_id, alvo.id, perms)
        mutados_lista.pop(alvo.id, None)
        await msg.reply_text(f"🔊 Usuario {alvo.username or alvo.first_name} foi dessilenciado.")
    except Exception as e:
        await msg.reply_text(f"❌ Erro: {e}")

async def listamute_cmd(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    msg = update.message
    if not mutados_lista:
        await msg.reply_text("Nenhum usuario silenciado no momento.")
        return
    texto = "🔇 Usuarios silenciados:\n\n"
    for uid, nome in mutados_lista.items():
        texto += f"• {nome} (ID: {uid})\n"
    await msg.reply_text(texto)

async def apagar_cmd(update, context):
    msg = update.message
    member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await msg.reply_text("❌ Apenas administradores podem usar este comando.")
        return
    if not msg.reply_to_message:
        await msg.reply_text("Responda a mensagem que deseja apagar com /D")
        return
    try:
        await msg.reply_to_message.delete()
        await msg.delete()
    except Exception as e:
        pass

app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("link", link_cmd))
app.add_handler(CommandHandler("title", title_cmd))
app.add_handler(CommandHandler("desc", desc_cmd))
app.add_handler(CommandHandler("pin", pin_cmd))
app.add_handler(CommandHandler("unpin", unpin_cmd))
app.add_handler(CommandHandler("mute", mute_cmd))
app.add_handler(CommandHandler("unmute", unmute_cmd))
app.add_handler(CommandHandler("listamute", listamute_cmd))
app.add_handler(CommandHandler("D", apagar_cmd))


async def usohoje(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("❌ Apenas o dono pode usar este comando.")
        return
    from datetime import datetime as _dt
    usos = load_usos()
    uid = str(update.message.from_user.id)
    hoje = _dt.now().strftime("%Y-%m-%d")
    qtd = usos.get(uid, {}).get("qtd", 0) if usos.get(uid, {}).get("data") == hoje else 0
    restam = max(LIMITE_DIARIO - qtd, 0)
    await update.message.reply_text(f"📊 Uso hoje: {qtd}/{LIMITE_DIARIO} (restam {restam})")

app.add_handler(CommandHandler("usohoje", usohoje))

async def vendas(update, context):
    if not eh_dono(update.message.from_user.id):
        await update.message.reply_text("Apenas o dono pode usar este comando.")
        return
    usos = load_usos()
    total_vendas = len(usos.get("pagamentos_processados", []))
    total_ativos = len(usos.get("auto_data", {}))
    await update.message.reply_text(f"Total de vendas confirmadas: {total_vendas}\nUIDs com autolike ativo: {total_ativos}")

app.add_handler(CommandHandler("vendas", vendas))

app.add_handler(CommandHandler("autolike", start_autolike))
app.add_handler(CommandHandler("stopauto", stop_autolike))
app.add_handler(CommandHandler("addautolike", addautolike))
app.add_handler(CommandHandler("removeautolike", removeautolike))

import uuid
PASSE_BASE_URL = "https://passe.soyxapasse.com.br"
TRAJES_VALIDOS = ["branco", "preto", "diabinha", "anjinha", "astronauta", "spacefarer", "velho_rabujento"]


def preco_venda(preco_original):
    if preco_original == 10:
        return 15
    if preco_original == 12:
        return 18
    return preco_original


def preco_traje(modelo):
    if modelo in ("preto", "branco"):
        return 25
    return 20


def nome_traje(modelo):
    if modelo == "preto":
        return "Ninja-preto"
    if modelo == "branco":
        return "Ninja-branco"
    return modelo


# ===================== /saldo =====================
async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/check-balance",
                             params={"token": PASSE_API_TOKEN}, timeout=15)
        texto = resp.text.strip()
        if texto.startswith("ERRO="):
            await update.message.reply_text(f"❌ {texto.replace('ERRO=', '')}")
            return
        dados = {}
        for par in texto.split():
            if "=" in par:
                chave, valor = par.split("=", 1)
                dados[chave] = valor
        evento = "🔥 ATIVO (preços promocionais)" if dados.get("evento") == "1" else "Não"
        msg = (
            f"💰 *SALDO*\n"
            f"━━━━━━━━━━━━\n"
            f"💵 Saldo: R${dados.get('saldo', '?')}\n"
            f"🎫 Passes: {dados.get('passes', '?')} (R${dados.get('preco_passe', '?')} cada)\n"
            f"🧑 Personagens: {dados.get('personagens', '?')} (R${dados.get('preco_personagem', '?')} cada)\n"
            f"🥷 Ninja: {dados.get('ninja', '?')} (R${dados.get('preco_ninja', '?')} cada)\n"
            f"🎟️ Codiguins: {dados.get('codiguins', '?')} (R${dados.get('preco_codiguin', '?')} cada)\n"
            f"🎉 Evento de recarga: {evento}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


# ===================== /estoque =====================
async def estoque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/stock", timeout=15)
        data = resp.json()
        pers = data.get("personagens", {})
        ninja = data.get("ninja", {})
        emotes = data.get("emotes", {})
        msg = (
            f"\U0001F4E6 *ESTOQUE*\n"
            f"\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\u2015\n"
            f"\U0001F39F Passe Booyah: {data.get('total_passes', '?')} disponiveis\n"
            f"\U0001F9D2 Personagens: {pers.get('envios_disponiveis', '?')} disponiveis\n"
            f"\U0001F455 Trajes: {ninja.get('envios_disponiveis', '?')} disponiveis\n"
            f"\U0001F3AD Emotes: {emotes.get('envios_disponiveis', '?')} disponiveis"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


# ===================== /personagem <uid> =====================
async def personagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /personagem <uid>")
        return
    player_id = context.args[0]
    keyboard = [[
        InlineKeyboardButton("✅ Confirmar", callback_data=f"personagem_confirm_{player_id}"),
        InlineKeyboardButton("❌ Cancelar", callback_data="personagem_cancel")
    ]]
    await update.message.reply_text(
        f"🧑 Confirma o envio de *50 personagens* para o UID `{player_id}`?\n"
        f"⚠️ Nível mínimo do jogador: 10. Entrega pode demorar (até 6 min).",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def personagem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "personagem_cancel":
        await query.edit_message_text("❌ Cancelado.")
        return
    if query.data.startswith("personagem_confirm_"):
        player_id = query.data.replace("personagem_confirm_", "")
        await query.edit_message_text("📦 Enviando personagens, aguarde (pode levar minutos)...")
        try:
            resp = requests.post(
                f"{PASSE_BASE_URL}/api/v1/order-personagem",
                headers={"Content-Type": "application/json"},
                json={"token": PASSE_API_TOKEN, "player_id": player_id},
                timeout=360
            )
            data = resp.json()
            if resp.status_code == 207 and data.get("incerto"):
                await query.edit_message_text("⚠️ Resultado incerto — NÃO reenvie. Verifique manualmente antes de tentar de novo.")
                return
            if data.get("success"):
                msg = (
                    f"✅ Personagens enviados!\n"
                    f"━━━━━━━━━━━━\n"
                    f"👤 UID: {player_id}\n"
                    f"🧑 Enviados: {data.get('personagens_enviados', '?')}\n"
                    f"📊 Total: {data.get('total_personagens', '?')}\n"
                    f"💵 Debitado: R${data.get('valor_debitado', '?')}\n"
                    f"💰 Saldo atual: R${data.get('saldo_atual', '?')}"
                )
            else:
                nivel = data.get("nivel")
                nivel_min = data.get("nivel_minimo")
                extra = f" (nível {nivel}, mínimo {nivel_min})" if nivel is not None else ""
                msg = f"❌ {data.get('message', 'Erro ao enviar personagens.')}{extra}"
            await query.edit_message_text(msg)
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")


# ===================== /traje <uid> <modelo> =====================
async def traje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if len(context.args) < 1:
        await update.message.reply_text(
            "Uso: /traje <uid> [modelo]\n\n"
            "Modelos: " + ", ".join(TRAJES_VALIDOS)
        )
        return
    player_id = context.args[0]
    if len(context.args) >= 2:
        modelo = context.args[1].lower()
        if modelo not in TRAJES_VALIDOS:
            await update.message.reply_text(f"❌ Modelo inválido. Opções: {', '.join(TRAJES_VALIDOS)}")
            return
        keyboard = [[
            InlineKeyboardButton("✅ Confirmar", callback_data=f"traje_confirm_{modelo}_{player_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="traje_cancel")
        ]]
        await update.message.reply_text(
            f"👕 Confirma o envio do traje *{nome_traje(modelo)}* (R${preco_traje(modelo)},00) para `{player_id}`?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        keyboard = [[InlineKeyboardButton(f"{nome_traje(m)} - R${preco_traje(m)},00", callback_data=f"trajemenu_{m}_{player_id}")] for m in TRAJES_VALIDOS]
        await update.message.reply_text("👕 Escolha o modelo:", reply_markup=InlineKeyboardMarkup(keyboard))


async def traje_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "traje_cancel":
        await query.edit_message_text("❌ Cancelado.")
        return
    if query.data.startswith("trajemenu_"):
        resto = query.data.replace("trajemenu_", "")
        modelo, player_id = resto.split("_", 1)
        keyboard = [[
            InlineKeyboardButton("✅ Confirmar", callback_data=f"traje_confirm_{modelo}_{player_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="traje_cancel")
        ]]
        await query.edit_message_text(
            f"👕 Confirma o envio do traje *{nome_traje(modelo)}* (R${preco_traje(modelo)},00) para `{player_id}`?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    if query.data.startswith("traje_confirm_"):
        resto = query.data.replace("traje_confirm_", "")
        modelo, player_id = resto.split("_", 1)
        await query.edit_message_text("📦 Enviando traje, aguarde...")
        try:
            resp = requests.post(
                f"{PASSE_BASE_URL}/api/v1/order-traje",
                headers={"Content-Type": "application/json"},
                json={"token": PASSE_API_TOKEN, "player_id": player_id, "modelo": modelo},
                timeout=30
            )
            data = resp.json()
            if data.get("success"):
                msg = (
                    f"✅ Traje enviado!\n"
                    f"━━━━━━━━━━━━\n"
                    f"👤 UID: {player_id}\n"
                    f"👕 Modelo: {data.get('modelo_nome') or nome_traje(modelo)}\n"
                    f"💵 Valor: R${preco_traje(modelo)},00\n"
                    f"💰 Saldo atual: R${data.get('saldo_atual', '?')}"
                )
            else:
                msg = f"❌ {data.get('message', 'Erro ao enviar traje.')}"
            await query.edit_message_text(msg)
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")


# ===================== /emote <uid> =====================
async def emote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /emote <uid>")
        return
    player_id = context.args[0]
    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/emotes", timeout=15)
        data = resp.json()
        emotes = data.get("emotes", [])
        if not emotes:
            await update.message.reply_text("❌ Nenhum emote disponível na vitrine agora.")
            return
        keyboard = [
            [InlineKeyboardButton(f"{e['nome']} - R${preco_venda(e['preco']):.2f}", callback_data=f"emote_pick|{e['slug']}|{player_id}|{preco_venda(e['preco'])}")]
            for e in emotes
        ]
        await update.message.reply_text("🎭 Escolha o emote:", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def emote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "emote_cancel":
        await query.edit_message_text("❌ Cancelado.")
        return
    if query.data.startswith("emote_pick|"):
        _, slug, player_id, venda = query.data.split("|")
        keyboard = [[
            InlineKeyboardButton("✅ Confirmar", callback_data=f"emote_confirm|{slug}|{player_id}|{venda}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="emote_cancel")
        ]]
        await query.edit_message_text(
            f"🎭 Confirma o envio do emote *{slug}* (R${venda}) para `{player_id}`?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    if query.data.startswith("emote_confirm|"):
        _, slug, player_id, venda = query.data.split("|")
        await query.edit_message_text("📦 Enviando emote, aguarde...")
        try:
            resp = requests.post(
                f"{PASSE_BASE_URL}/api/v1/order-emote",
                headers={"Content-Type": "application/json"},
                json={"token": PASSE_API_TOKEN, "player_id": player_id, "emote": slug},
                timeout=30
            )
            data = resp.json()
            if resp.status_code == 207:
                await query.edit_message_text("⚠️ Resultado incerto — NÃO reenvie. Confira manualmente antes de tentar de novo.")
                return
            if data.get("success"):
                msg = (
                    f"✅ Emote enviado!\n"
                    f"━━━━━━━━━━━━\n"
                    f"👤 UID: {player_id}\n"
                    f"🎭 Emote: {data.get('emote_nome', slug)}\n"
                    f"💵 Valor: R${venda}\n"
                    f"💰 Saldo atual: R${data.get('saldo_atual', '?')}"
                )
            else:
                msg = f"❌ {data.get('message', 'Erro ao enviar emote.')}"
            await query.edit_message_text(msg)
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")


# ===================== /codiguin [produto] =====================
async def codiguin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    if uid != str(DONO_ID) and uid not in PASSE_USUARIOS:
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    produto = context.args[0] if context.args else "snickers"
    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/codiguins", timeout=15)
        data = resp.json()
        opcoes = {c["produto"]: c for c in data.get("codiguins", [])}
        if produto not in opcoes:
            disponiveis = ", ".join(opcoes.keys())
            await update.message.reply_text(f"❌ Produto inválido. Disponíveis: {disponiveis}")
            return
        info = opcoes[produto]
        if not info.get("disponivel"):
            await update.message.reply_text(f"❌ Estoque esgotado para {produto}.")
            return
        keyboard = [[
            InlineKeyboardButton("✅ Confirmar", callback_data=f"codiguin_confirm_{produto}"),
            InlineKeyboardButton("❌ Cancelar", callback_data="codiguin_cancel")
        ]]
        await update.message.reply_text(
            f"🎟️ Confirma a compra de *{info.get('nome', produto)}* por R${info.get('preco', '?')}?\n"
            f"Restam {info.get('disponiveis', '?')} código(s).",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")


async def codiguin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "codiguin_cancel":
        await query.edit_message_text("❌ Cancelado.")
        return
    if query.data.startswith("codiguin_confirm_"):
        produto = query.data.replace("codiguin_confirm_", "")
        await query.edit_message_text("📦 Gerando código, aguarde...")
        request_id = str(uuid.uuid4())
        try:
            resp = requests.post(
                f"{PASSE_BASE_URL}/api/v1/order-codiguin",
                headers={"Content-Type": "application/json", "X-Request-Id": request_id},
                json={"token": PASSE_API_TOKEN, "produto": produto},
                timeout=30
            )
            data = resp.json()
            if data.get("success"):
                repetido = " (repetido — mesma compra anterior)" if data.get("repetido") else ""
                msg = (
                    f"✅ Código gerado!{repetido}\n"
                    f"━━━━━━━━━━━━\n"
                    f"🎟️ Produto: {data.get('produto_nome', produto)}\n"
                    f"🔑 Código: `{data.get('codigo', '?')}`\n"
                    f"💵 Debitado: R${data.get('valor_debitado', '?')}\n"
                    f"💰 Saldo atual: R${data.get('saldo_atual', '?')}\n"
                    f"📦 Estoque restante: {data.get('estoque_restante', '?')}"
                )
            else:
                msg = f"❌ {data.get('message', 'Erro ao gerar código.')}"
            await query.edit_message_text(msg, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")


app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("estoque", estoque))
app.add_handler(CommandHandler("personagem", personagem))
app.add_handler(CallbackQueryHandler(personagem_callback, pattern="^personagem_"))
app.add_handler(CommandHandler("traje", traje))
app.add_handler(CallbackQueryHandler(traje_callback, pattern="^traje|^trajemenu_"))
app.add_handler(CommandHandler("emote", emote))
app.add_handler(CallbackQueryHandler(emote_callback, pattern="^emote_"))
app.add_handler(CommandHandler("codiguin", codiguin))
app.add_handler(CallbackQueryHandler(codiguin_callback, pattern="^codiguin_"))



async def webhookinfo_cmd(update, context):
    import os
    tok = os.environ.get("BOT_TOKEN", "")
    r = _req.get(f"https://api.telegram.org/bot{tok}/getWebhookInfo", timeout=20)
    await update.message.reply_text(f"```\n{r.text}\n```", parse_mode="Markdown")

app.add_handler(CommandHandler("webhookinfo", webhookinfo_cmd))

app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False)

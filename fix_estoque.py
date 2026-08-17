with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/stock", timeout=15)
        data = resp.json()
        pers = data.get("personagens", {})
        msg = (
            f"\\U0001F4E6 *ESTOQUE*\\n"
            f"\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\n"
            f"\\U0001F39F Passes: {data.get('total_passes', '?')}\\n"
            f"\\U0001F48E Diamantes (api1): {data.get('api1', '?')}\\n"
            f"\\U0001F9D2 Personagens disponíveis: {pers.get('disponivel', '?')}\\n"
            f"   Envios disponíveis: {pers.get('envios_disponiveis', '?')}\\n"
            f"   Contas ouro: {pers.get('contas_ouro', '?')}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"\\u274C Erro: {str(e)}")'''

new = '''    try:
        resp = requests.get(f"{PASSE_BASE_URL}/api/v1/stock", timeout=15)
        data = resp.json()
        pers = data.get("personagens", {})
        ninja = data.get("ninja", {})
        emotes = data.get("emotes", {})
        msg = (
            f"\\U0001F4E6 *ESTOQUE*\\n"
            f"\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\u2015\\n"
            f"\\U0001F39F Passe Booyah: {data.get('total_passes', '?')} disponiveis\\n"
            f"\\U0001F9D2 Personagens: {pers.get('envios_disponiveis', '?')} disponiveis\\n"
            f"\\U0001F455 Trajes: {ninja.get('envios_disponiveis', '?')} disponiveis\\n"
            f"\\U0001F3AD Emotes: {emotes.get('envios_disponiveis', '?')} disponiveis"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"\\u274C Erro: {str(e)}")'''

if old not in content:
    print("BLOCO NAO ENCONTRADO - ABORTANDO")
else:
    content = content.replace(old, new)
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("ESTOQUE OK")

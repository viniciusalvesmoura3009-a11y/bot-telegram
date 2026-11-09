import os
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

PLANO, ID_GUILDA, CONFIG_APROVACAO, CONFIG_NIVEL, CONFIG_RANK, CONFIG_CS, WHATS, PAGAMENTO = range(8)
_DONO = {"id": None}
_NV = {'padrao': 'Padrão', '10': 'Nível 10+', '20': 'Nível 20+', '30': 'Nível 30+'}
_RK = {'padrao': 'Padrão', 'mestre': 'Mestre+', 'gm': 'Grandmaster+'}

async def up_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        await update.message.reply_text(f"🔒 Por segurança, faça o pedido no privado: https://t.me/{context.bot.username}?start=upguilda")
        return ConversationHandler.END
    context.user_data.clear()
    keyboard = [[
        InlineKeyboardButton("40k - 50k (R$ 20)", callback_data='p40'),
        InlineKeyboardButton("80k - 100k (R$ 40)", callback_data='p80'),
    ]]
    await update.message.reply_text(
        "🚀 *Bem-vindo ao Sistema de UP de Guildas!*\n\n"
        "Escolha abaixo a quantidade de pontos que deseja para sua guilda:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PLANO

async def up_plano_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['up_plano'] = "40k" if query.data == 'p40' else "80k"
    await query.edit_message_text("🆔 Agora, por favor, digite o *ID da sua Guilda*:", parse_mode='Markdown')
    return ID_GUILDA

async def up_id_collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Erro! O ID da guilda deve conter apenas números. Tente novamente:")
        return ID_GUILDA
    context.user_data['up_guilda_id'] = text
    keyboard = [[
        InlineKeyboardButton("✅ Ligado", callback_data='auto_L'),
        InlineKeyboardButton("❌ Desligado", callback_data='auto_D'),
    ]]
    await update.message.reply_text(
        "⚙️ *Método de Aprovação*\n\nDeseja a aprovação automática dos bots?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIG_APROVACAO

async def up_aprovacao_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['up_auto'] = "LIGADO" if query.data == 'auto_L' else "DESLIGADO"
    keyboard = [
        [InlineKeyboardButton("Padrão", callback_data='nv_padrao')],
        [InlineKeyboardButton("Nível 10+", callback_data='nv_10'), InlineKeyboardButton("Nível 20+", callback_data='nv_20')],
        [InlineKeyboardButton("Nível 30+", callback_data='nv_30')]
    ]
    await query.edit_message_text(
        "📊 *Configuração de Nível*\n\nQual o nível mínimo dos bots?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIG_NIVEL

async def up_nivel_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['up_nivel'] = query.data.replace('nv_', '')
    keyboard = [
        [InlineKeyboardButton("Padrão", callback_data='rk_padrao')],
        [InlineKeyboardButton("Mestre+", callback_data='rk_mestre'), InlineKeyboardButton("Grandmaster+", callback_data='rk_gm')]
    ]
    await query.edit_message_text(
        "🏆 *BR Ranqueado*\n\nQual o Rank desejado para os bots no BR Ranqueado?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIG_RANK

async def up_rank_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['up_rank'] = query.data.replace('rk_', '')
    keyboard = [
        [InlineKeyboardButton("Padrão", callback_data='cs_padrao')],
        [InlineKeyboardButton("Mestre+", callback_data='cs_mestre'), InlineKeyboardButton("Grandmaster+", callback_data='cs_gm')]
    ]
    await query.edit_message_text(
        "🎯 *CS Ranqueado*\n\nQual o Rank desejado para os bots no CS Ranqueado?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIG_CS

async def up_cs_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['up_cs'] = query.data.replace('cs_', '')
    await query.edit_message_text(
        "📱 Digite seu *número de WhatsApp* com DDD (ex: 11999998888).\n\n"
        "Vou usar só pra confirmar seu pedido com você.",
        parse_mode='Markdown'
    )
    return WHATS

async def up_whats_collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = re.sub(r'\D', '', update.message.text)
    if num.startswith('55') and len(num) > 11:
        num = num[2:]
    if len(num) not in (10, 11):
        await update.message.reply_text("❌ Número inválido. Digite com DDD, ex: 11999998888")
        return WHATS
    context.user_data['up_whats'] = num
    d = context.user_data
    plano = d.get('up_plano', '40k')
    valor = "20,00" if plano == "40k" else "40,00"
    pix = os.environ.get("PIX_CHAVE", "SEU_PIX_AQUI")
    resumo = (
        f"✅ *Pedido Configurado!*\n\n"
        f"📦 Plano: {plano}\n"
        f"🆔 ID Guilda: {d['up_guilda_id']}\n"
        f"📱 WhatsApp: {num}\n\n"
        f"⚠️ *Antes de pagar*, deixe sua guilda em *Método de Aprovação* exatamente assim:\n"
        f"• Aprovação automática: {'Ligado' if d['up_auto'] == 'LIGADO' else 'Desligado'}\n"
        f"• NV.: {_NV.get(d['up_nivel'], d['up_nivel'])}\n"
        f"• BR Ranqueado: {_RK.get(d['up_rank'], d['up_rank'])}\n"
        f"• CS Ranqueado: {_RK.get(d['up_cs'], d['up_cs'])}\n\n"
        f"💰 *Valor Total: R$ {valor}*\n\n"
        f"Envie o pagamento via PIX para: `{pix}`\n\n"
        f"Após pagar, envie o comprovante (foto ou arquivo) aqui."
    )
    await update.message.reply_text(resumo, parse_mode='Markdown')
    return PAGAMENTO

async def up_pagamento_recebido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    usuario = update.effective_user
    resumo_admin = (
        f"💰 Novo comprovante recebido! (UP de Guilda)\n\n"
        f"👤 De: {usuario.first_name} (@{usuario.username or 'sem_usuario'})\n"
        f"🆔 ID Telegram: {usuario.id}\n"
        f"📦 Plano: {dados.get('up_plano')}\n"
        f"🆔 ID Guilda: {dados.get('up_guilda_id')}\n"
        f"⚙️ Auto: {dados.get('up_auto')}\n"
        f"📊 Nível: {dados.get('up_nivel')}\n"
        f"🏆 BR Rank: {dados.get('up_rank')}\n"
        f"🎯 CS Rank: {dados.get('up_cs')}\n"
        f"📱 WhatsApp: {dados.get('up_whats')} (wa.me/55{dados.get('up_whats')})"
    )
    try:
        if update.message.photo:
            await context.bot.send_photo(chat_id=_DONO["id"], photo=update.message.photo[-1].file_id, caption=resumo_admin)
        elif update.message.document:
            await context.bot.send_document(chat_id=_DONO["id"], document=update.message.document.file_id, caption=resumo_admin)
        await update.message.reply_text("✅ Comprovante recebido! Seu pedido será analisado em breve.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Erro ao enviar comprovante: {e}")
        return PAGAMENTO
    return ConversationHandler.END

async def up_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operação cancelada. Use /upguilda para recomeçar.")
    return ConversationHandler.END

def get_upguilda_handler(dono_id):
    _DONO["id"] = dono_id
    return ConversationHandler(
        entry_points=[CommandHandler('upguilda', up_start)],
        states={
            PLANO: [CallbackQueryHandler(up_plano_choice, pattern='^p(40|80)$')],
            ID_GUILDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, up_id_collect)],
            CONFIG_APROVACAO: [CallbackQueryHandler(up_aprovacao_choice, pattern='^auto_')],
            CONFIG_NIVEL: [CallbackQueryHandler(up_nivel_choice, pattern='^nv_')],
            CONFIG_RANK: [CallbackQueryHandler(up_rank_choice, pattern='^rk_')],
            CONFIG_CS: [CallbackQueryHandler(up_cs_choice, pattern='^cs_')],
            WHATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, up_whats_collect)],
            PAGAMENTO: [MessageHandler(filters.PHOTO | filters.Document.ALL, up_pagamento_recebido)],
        },
        fallbacks=[CommandHandler('cancel', up_cancel), CommandHandler('upguilda', up_start)],
        conversation_timeout=1800,
    )

import os
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

PLANO, ID_GUILDA, WHATS = range(3)
_DONO = {"id": None}
ZAP_NUM = "5582988631900"
ZAP_TXT = "82 98863-1900"

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
    await update.message.reply_text(
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
    d = context.user_data
    d['up_whats'] = num
    plano = d.get('up_plano', '40k')
    valor = "20,00" if plano == "40k" else "40,00"
    pix = os.environ.get("PIX_CHAVE", "SEU_PIX_AQUI")
    resumo = (
        f"✅ *Pedido Configurado!*\n\n"
        f"📦 Plano: {plano}\n"
        f"🆔 ID Guilda: {d['up_guilda_id']}\n"
        f"📱 Seu WhatsApp: {num}\n\n"
        f"⚠️ *Antes de iniciar*, dentro do jogo vá em *Método de Aprovação* da sua guilda e deixe exatamente assim:\n"
        f"• Aprovação automática: *Desligado*\n"
        f"• NV.: *Padrão*\n"
        f"• BR Ranqueado: *Padrão*\n"
        f"• CS Ranqueado: *Padrão*\n\n"
        f"💰 *Valor Total: R$ {valor}*\n\n"
        f"Envie o pagamento via PIX para: `{pix}`\n\n"
        f"📲 Após pagar, envie o comprovante pelo *WhatsApp*:\n"
        f"*{ZAP_TXT}*\n"
        f"https://wa.me/{ZAP_NUM}\n\n"
        f"Informe o ID da guilda ({d['up_guilda_id']}) junto com o comprovante."
    )
    await update.message.reply_text(resumo, parse_mode='Markdown')
    try:
        u = update.effective_user
        aviso = (
            f"🆕 Novo pedido de UP de Guilda (comprovante vem pelo WhatsApp)\n\n"
            f"👤 {u.first_name} (@{u.username or 'sem_usuario'})\n"
            f"🆔 ID Telegram: {u.id}\n"
            f"📦 Plano: {plano} (R$ {valor})\n"
            f"🆔 ID Guilda: {d['up_guilda_id']}\n"
            f"📱 WhatsApp: {num} (wa.me/55{num})"
        )
        await context.bot.send_message(chat_id=_DONO["id"], text=aviso)
    except Exception:
        pass
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
            WHATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, up_whats_collect)],
        },
        fallbacks=[CommandHandler('cancel', up_cancel), CommandHandler('upguilda', up_start)],
        conversation_timeout=1800,
    )

#!/usr/bin/env python3
"""
🤖 Sistema Telegram Principal - FreqTrade Multi-Strategy
Integração completa de todos os módulos do sistema Telegram
"""

import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Importar todos os módulos do sistema
from telegram_bot_main import (
    bot_main, start_command, status_command, stats_command, help_command, button_callback
)
from telegram_trading_commands import (
    forcebuy_command, forcesell_command, adjust_command, 
    emergency_command, strategy_status_command, cleanup
)
from telegram_ai_predictor import (
    predict_command, ai_analysis_command, opportunities_command
)

# Configuração
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Handler global de erros"""
    logger.error(f"Erro no bot: {context.error}")
    
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Ocorreu um erro interno. Tente novamente em alguns segundos."
            )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {e}")

def main():
    """Função principal do sistema Telegram"""
    if not TOKEN or not CHAT_ID:
        logger.error("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados!")
        logger.error("Execute: python setup_credentials.py")
        return
    
    logger.info("🚀 Iniciando Sistema Telegram Completo...")
    
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # ========================================================================
    # COMANDOS PRINCIPAIS
    # ========================================================================
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # ========================================================================
    # COMANDOS DE TRADING MANUAL
    # ========================================================================
    application.add_handler(CommandHandler("forcebuy", forcebuy_command))
    application.add_handler(CommandHandler("forcesell", forcesell_command))
    application.add_handler(CommandHandler("adjust", adjust_command))
    application.add_handler(CommandHandler("emergency", emergency_command))
    application.add_handler(CommandHandler("strategy_status", strategy_status_command))
    
    # ========================================================================
    # COMANDOS DE IA PREDITIVA
    # ========================================================================
    application.add_handler(CommandHandler("predict", predict_command))
    application.add_handler(CommandHandler("ai_analysis", ai_analysis_command))
    application.add_handler(CommandHandler("opportunities", opportunities_command))
    
    # ========================================================================
    # HANDLERS DE BOTÕES E ERROS
    # ========================================================================
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # ========================================================================
    # INICIALIZAÇÃO
    # ========================================================================
    logger.info("✅ Sistema Telegram configurado com sucesso!")
    logger.info(f"🎯 Chat ID: {CHAT_ID}")
    logger.info("📱 Comandos disponíveis:")
    logger.info("   • /start - Menu principal")
    logger.info("   • /status - Status das estratégias")
    logger.info("   • /stats - Estatísticas detalhadas")
    logger.info("   • /predict - IA preditiva")
    logger.info("   • /forcebuy - Trading manual")
    logger.info("   • /emergency - Parada de emergência")
    logger.info("   • /help - Ajuda completa")
    
    # Enviar mensagem de inicialização
    async def send_startup_message():
        try:
            await bot_main.send_message(
                "🤖 <b>SISTEMA TELEGRAM ATIVO!</b>\n\n"
                "✅ Bot principal inicializado\n"
                "✅ Trading manual habilitado\n"
                "✅ IA preditiva ativa\n"
                "✅ Monitoramento 24/7\n\n"
                "Digite /start para começar!"
            )
        except Exception as e:
            logger.warning(f"Não foi possível enviar mensagem de inicialização: {e}")
    
    # Executar mensagem de inicialização
    asyncio.create_task(send_startup_message())
    
    # Iniciar bot
    logger.info("🤖 Sistema Telegram rodando...")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Sistema Telegram parado pelo usuário")
        asyncio.run(cleanup())
    except Exception as e:
        logger.error(f"🚨 Erro fatal: {e}")
        asyncio.run(cleanup())
#!/usr/bin/env python3
"""
Telegram Commander - Controle avançado via comandos Telegram
Permite controlar cada estratégia individualmente via comandos
"""
import os
import asyncio
import json
import logging
import subprocess
import docker
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from freqtrade_stats import FreqtradeStats
from strategy_controller import StrategyController

# Configuração
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ADMIN_USERS = [int(CHAT_ID)] if CHAT_ID else []

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Estratégias disponíveis
STRATEGIES = {
    'stratA': {
        'name': 'Strategy A',
        'container': 'ft-stratA',
        'config': 'user_data/configs/stratA.json',
        'description': 'RSI básico - 15m'
    },
    'stratB': {
        'name': 'Strategy B', 
        'container': 'ft-stratB',
        'config': 'user_data/configs/stratB.json',
        'description': 'RSI básico - 15m'
    },
    'waveHyperNW': {
        'name': 'WaveHyperNW Strategy',
        'container': 'ft-waveHyperNW', 
        'config': 'user_data/configs/waveHyperNW.json',
        'description': 'WaveTrend + Nadaraya-Watson - 5m'
    }
}

class TelegramCommander:
    def __init__(self):
        self.docker_client = self._init_docker_client()
        self.stats = FreqtradeStats()
        self.controller = StrategyController()
    
    def _init_docker_client(self):
        """Inicializa cliente Docker com tratamento de erro"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Tentar diferentes formas de conectar ao Docker
                if os.name == 'nt':  # Windows
                    try:
                        client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                    except:
                        client = docker.from_env()
                else:
                    client = docker.from_env()
                
                # Testar conexão
                client.ping()
                logger.info(f"✅ Docker conectado com sucesso (tentativa {attempt + 1})")
                return client
                
            except Exception as e:
                logger.warning(f"❌ Tentativa {attempt + 1} falhou: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error("🚨 Não foi possível conectar ao Docker. Usando comandos CLI como fallback.")
                    return None
        
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é administrador"""
        return user_id in ADMIN_USERS
    
    async def get_container_status(self, container_name: str) -> Dict:
        """Obter status de um container"""
        try:
            if self.docker_client:
                container = self.docker_client.containers.get(container_name)
                return {
                    'name': container_name,
                    'status': container.status,
                    'running': container.status == 'running',
                    'started_at': container.attrs['State'].get('StartedAt'),
                    'restart_count': container.attrs.get('RestartCount', 0)
                }
            else:
                # Fallback para comando CLI
                result = subprocess.run(['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', 'table {{.Names}}\t{{.Status}}'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and container_name in result.stdout:
                    status_line = [line for line in result.stdout.split('\n') if container_name in line]
                    if status_line:
                        status = 'running' if 'Up' in status_line[0] else 'stopped'
                        return {
                            'name': container_name,
                            'status': status,
                            'running': status == 'running',
                            'started_at': 'unknown',
                            'restart_count': 0
                        }
                return {'name': container_name, 'status': 'not_found', 'running': False}
        except docker.errors.NotFound:
            return {'name': container_name, 'status': 'not_found', 'running': False}
        except Exception as e:
            logger.error(f"Erro ao verificar container {container_name}: {e}")
            return {'name': container_name, 'status': 'error', 'running': False}

# Instância global
commander = TelegramCommander()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menu principal"""
    logger.info(f"📱 Comando /start recebido de {update.effective_user.id}")
    
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado. Usuário não autorizado.")
        logger.warning(f"🚫 Acesso negado para usuário {update.effective_user.id}")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
        [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
        [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu")],
        [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
        [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🤖 <b>FREQTRADE COMMANDER</b>

Bem-vindo ao sistema de controle avançado!

Escolha uma opção abaixo para começar:
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Status de todas as estratégias"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    message = "📊 <b>STATUS GERAL</b>\n\n"
    
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        status_emoji = "🟢" if status['running'] else "🔴"
        message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
        message += f"   Status: {status['status']}\n"
        message += f"   Container: {strategy_info['container']}\n\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ajuda"""
    message = """
🆘 <b>AJUDA - COMANDOS DISPONÍVEIS</b>

<b>Comandos Básicos:</b>
/start - Menu principal
/status - Status de todas as estratégias
/help - Esta ajuda

<b>Funcionalidades:</b>
• 📊 Status em tempo real
• 🎮 Controle individual de estratégias
• 📈 Estatísticas detalhadas
• ⚙️ Configurações avançadas

<b>Segurança:</b>
• Apenas usuários autorizados
• Todas as ações são logadas
    """
    
    await update.message.reply_text(message, parse_mode='HTML')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para botões inline"""
    query = update.callback_query
    await query.answer()
    
    if not commander.is_admin(query.from_user.id):
        await query.edit_message_text("❌ Acesso negado.")
        return
    
    data = query.data
    logger.info(f"🔘 Callback recebido: {data}")
    
    if data == "status_all":
        message = "📊 <b>STATUS DETALHADO</b>\n\n"
        
        for strategy_id, strategy_info in STRATEGIES.items():
            status = await commander.get_container_status(strategy_info['container'])
            status_emoji = "🟢" if status['running'] else "🔴"
            message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
            message += f"   Status: {status['status']}\n"
            message += f"   Container: {strategy_info['container']}\n"
            message += f"   Descrição: {strategy_info['description']}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
            [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
            [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu")],
            [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
            [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
🤖 <b>FREQTRADE COMMANDER</b>

Bem-vindo ao sistema de controle avançado!

Escolha uma opção abaixo para começar:
        """
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    else:
        await query.edit_message_text("🚧 Funcionalidade em desenvolvimento...")

def main():
    """Função principal"""
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN não configurado!")
        return
    
    if not CHAT_ID:
        logger.error("❌ TELEGRAM_CHAT_ID não configurado!")
        return
    
    logger.info(f"🔑 Token configurado: {TOKEN[:10]}...")
    logger.info(f"👤 Chat ID configurado: {CHAT_ID}")
    logger.info(f"👥 Usuários admin: {ADMIN_USERS}")
    
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Iniciar bot
    logger.info("🤖 Telegram Commander iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
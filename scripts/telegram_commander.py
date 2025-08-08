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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estratégias disponíveis
STRATEGIES = {
    'stratA': {
        'name': 'Sample Strategy A',
        'container': 'ft-stratA',
        'config': 'user_data/configs/stratA.json',
        'description': 'RSI básico - 15m'
    },
    'stratB': {
        'name': 'Sample Strategy B', 
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
        self.docker_client = docker.from_env()
        self.stats = FreqtradeStats()
        self.controller = StrategyController()
        
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é administrador"""
        return user_id in ADMIN_USERS
    
    async def get_container_status(self, container_name: str) -> Dict:
        """Obter status de um container"""
        try:
            container = self.docker_client.containers.get(container_name)
            return {
                'name': container_name,
                'status': container.status,
                'running': container.status == 'running',
                'started_at': container.attrs['State'].get('StartedAt'),
                'restart_count': container.attrs.get('RestartCount', 0)
            }
        except docker.errors.NotFound:
            return {'name': container_name, 'status': 'not_found', 'running': False}
        except Exception as e:
            logger.error(f"Erro ao verificar container {container_name}: {e}")
            return {'name': container_name, 'status': 'error', 'running': False}
    
    async def control_strategy(self, strategy_id: str, action: str) -> Dict:
        """Controlar uma estratégia específica"""
        if strategy_id not in STRATEGIES:
            return {'success': False, 'message': f'Estratégia {strategy_id} não encontrada'}
        
        container_name = STRATEGIES[strategy_id]['container']
        
        try:
            if action == 'start':
                result = subprocess.run(['docker', 'compose', 'start', strategy_id], 
                                      capture_output=True, text=True)
            elif action == 'stop':
                result = subprocess.run(['docker', 'compose', 'stop', strategy_id], 
                                      capture_output=True, text=True)
            elif action == 'restart':
                result = subprocess.run(['docker', 'compose', 'restart', strategy_id], 
                                      capture_output=True, text=True)
            else:
                return {'success': False, 'message': f'Ação {action} não reconhecida'}
            
            if result.returncode == 0:
                return {'success': True, 'message': f'Estratégia {strategy_id} {action} executado com sucesso'}
            else:
                return {'success': False, 'message': f'Erro ao executar {action}: {result.stderr}'}
                
        except Exception as e:
            logger.error(f"Erro ao controlar estratégia {strategy_id}: {e}")
            return {'success': False, 'message': f'Erro interno: {str(e)}'}
    
    async def get_strategy_stats(self, strategy_id: str) -> Dict:
        """Obter estatísticas de uma estratégia"""
        if strategy_id not in STRATEGIES:
            return {}
        
        strategy_name = STRATEGIES[strategy_id]['name']
        all_stats = self.stats.get_strategy_stats(hours=24)
        
        return all_stats.get(strategy_name, {
            'trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0,
            'avg_profit': 0.0
        })

# Instância global
commander = TelegramCommander()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menu principal"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado. Usuário não autorizado.")
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
    
    message = "📊 <b>STATUS DAS ESTRATÉGIAS</b>\n\n"
    
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        emoji = "🟢" if status['running'] else "🔴"
        
        message += f"{emoji} <b>{strategy_info['name']}</b>\n"
        message += f"   Status: {status['status']}\n"
        message += f"   Descrição: {strategy_info['description']}\n"
        
        if status['running']:
            stats = await commander.get_strategy_stats(strategy_id)
            message += f"   Trades: {stats.get('trades', 0)}\n"
            message += f"   P&L: {stats.get('total_profit', 0):.2f} USDT\n"
        
        message += "\n"
    
    message += f"🕐 Atualizado: {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def control_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /control - Menu de controle"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([InlineKeyboardButton(
            f"🎯 {strategy_info['name']}", 
            callback_data=f"strategy_{strategy_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🎮 <b>CONTROLE DE ESTRATÉGIAS</b>

Selecione uma estratégia para controlar:
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estatísticas detalhadas"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    message = "📈 <b>ESTATÍSTICAS DETALHADAS</b>\n\n"
    
    total_trades = 0
    total_profit = 0.0
    
    for strategy_id, strategy_info in STRATEGIES.items():
        stats = await commander.get_strategy_stats(strategy_id)
        
        if stats.get('trades', 0) > 0:
            message += f"📊 <b>{strategy_info['name']}</b>\n"
            message += f"   Trades: {stats['trades']}\n"
            message += f"   Win Rate: {stats.get('win_rate', 0):.1f}%\n"
            message += f"   P&L Total: {stats['total_profit']:.2f} USDT\n"
            message += f"   P&L Médio: {stats.get('avg_profit', 0):.2f} USDT\n\n"
            
            total_trades += stats['trades']
            total_profit += stats['total_profit']
    
    message += f"💰 <b>RESUMO GERAL</b>\n"
    message += f"Total Trades: {total_trades}\n"
    message += f"P&L Total: {total_profit:.2f} USDT\n"
    message += f"🕐 Últimas 24h"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões inline"""
    query = update.callback_query
    await query.answer()
    
    if not commander.is_admin(query.from_user.id):
        await query.edit_message_text("❌ Acesso negado.")
        return
    
    data = query.data
    
    if data == "main_menu":
        await show_main_menu(query)
    elif data == "status_all":
        await show_status_all(query)
    elif data == "control_menu":
        await show_control_menu(query)
    elif data == "stats_menu":
        await show_stats_menu(query)
    elif data.startswith("strategy_"):
        strategy_id = data.replace("strategy_", "")
        await show_strategy_control(query, strategy_id)
    elif data.startswith("action_"):
        parts = data.split("_")
        action = parts[1]
        strategy_id = parts[2]
        await execute_strategy_action(query, strategy_id, action)
    elif data.startswith("logs_"):
        strategy_id = data.replace("logs_", "")
        await show_strategy_logs(query, strategy_id)
    elif data.startswith("config_"):
        strategy_id = data.replace("config_", "")
        await show_strategy_config(query, strategy_id)
    elif data.startswith("toggle_dry_"):
        strategy_id = data.replace("toggle_dry_", "")
        await toggle_strategy_dry_run(query, strategy_id)
    elif data.startswith("stats_"):
        strategy_id = data.replace("stats_", "")
        await show_strategy_detailed_stats(query, strategy_id)

async def show_main_menu(query):
    """Mostrar menu principal"""
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

Escolha uma opção abaixo:
    """
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_control_menu(query):
    """Mostrar menu de controle"""
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        emoji = "🟢" if status['running'] else "🔴"
        
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {strategy_info['name']}", 
            callback_data=f"strategy_{strategy_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Menu Principal", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
🎮 <b>CONTROLE DE ESTRATÉGIAS</b>

Selecione uma estratégia para controlar:

🟢 = Rodando | 🔴 = Parada
    """
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_control(query, strategy_id: str):
    """Mostrar controles de uma estratégia específica"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    status = await commander.get_container_status(strategy_info['container'])
    stats = await commander.get_strategy_stats(strategy_id)
    
    emoji = "🟢" if status['running'] else "🔴"
    
    message = f"""
{emoji} <b>{strategy_info['name']}</b>

📋 <b>Informações:</b>
• Status: {status['status']}
• Descrição: {strategy_info['description']}
• Container: {strategy_info['container']}

📊 <b>Estatísticas (24h):</b>
• Trades: {stats.get('trades', 0)}
• P&L: {stats.get('total_profit', 0):.2f} USDT
• Win Rate: {stats.get('win_rate', 0):.1f}%
    """
    
    keyboard = []
    
    if status['running']:
        keyboard.append([
            InlineKeyboardButton("⏹️ Parar", callback_data=f"action_stop_{strategy_id}"),
            InlineKeyboardButton("🔄 Reiniciar", callback_data=f"action_restart_{strategy_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("▶️ Iniciar", callback_data=f"action_start_{strategy_id}")
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("📋 Logs", callback_data=f"logs_{strategy_id}"),
         InlineKeyboardButton("📊 Stats", callback_data=f"stats_{strategy_id}")],
        [InlineKeyboardButton("⚙️ Config", callback_data=f"config_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="control_menu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def execute_strategy_action(query, strategy_id: str, action: str):
    """Executar ação em uma estratégia"""
    strategy_info = STRATEGIES.get(strategy_id, {})
    strategy_name = strategy_info.get('name', strategy_id)
    
    # Mostrar mensagem de processamento
    await query.edit_message_text(f"⏳ Executando {action} em {strategy_name}...")
    
    # Executar ação
    result = await commander.control_strategy(strategy_id, action)
    
    if result['success']:
        emoji = "✅"
        message = f"{emoji} <b>Sucesso!</b>\n\n{result['message']}"
    else:
        emoji = "❌"
        message = f"{emoji} <b>Erro!</b>\n\n{result['message']}"
    
    # Adicionar botão para voltar
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ajuda"""
    message = """
🆘 <b>AJUDA - COMANDOS DISPONÍVEIS</b>

<b>Comandos Básicos:</b>
/start - Menu principal
/status - Status de todas as estratégias
/control - Menu de controle
/stats - Estatísticas detalhadas
/help - Esta ajuda

<b>Controle por Estratégia:</b>
• ▶️ Iniciar estratégia
• ⏹️ Parar estratégia  
• 🔄 Reiniciar estratégia
• 📋 Ver logs
• ⚙️ Ver configuração

<b>Informações:</b>
• 🟢 = Estratégia rodando
• 🔴 = Estratégia parada
• P&L = Profit & Loss (lucro/prejuízo)
• Win Rate = Taxa de acerto

<b>Segurança:</b>
• Apenas usuários autorizados podem usar
• Todas as ações são logadas
• Confirmação para ações críticas
    """
    
    await update.message.reply_text(message, parse_mode='HTML')

def main():
    """Função principal"""
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN não configurado!")
        return
    
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("control", control_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Iniciar bot
    logger.info("🤖 Telegram Commander iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
async
 def show_strategy_logs(query, strategy_id: str):
    """Mostrar logs de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    logs = commander.controller.get_strategy_logs(strategy_id, lines=20)
    
    message = f"📋 <b>LOGS - {strategy_info['name']}</b>\n\n"
    message += "<code>"
    
    # Mostrar apenas as últimas 10 linhas para não exceder limite do Telegram
    for line in logs[-10:]:
        if line.strip():
            message += line[:100] + "\n"  # Limitar tamanho da linha
    
    message += "</code>"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=f"logs_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_config(query, strategy_id: str):
    """Mostrar configuração de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    if 'error' in summary:
        await query.edit_message_text(f"❌ Erro: {summary['error']}")
        return
    
    mode_emoji = "🟡" if summary['dry_run'] else "🔴"
    mode_text = "DRY-RUN" if summary['dry_run'] else "LIVE"
    
    message = f"""
⚙️ <b>CONFIGURAÇÃO - {strategy_info['name']}</b>

📊 <b>Configurações Atuais:</b>
• Modo: {mode_emoji} {mode_text}
• Stake Amount: {summary['stake_amount']} {summary['stake_currency']}
• Max Trades: {summary['max_open_trades']}
• Timeframe: {summary['timeframe']}
• Container: {summary['container_status']}

⚠️ <b>Atenção:</b> Mudanças requerem reinicialização da estratégia.
    """
    
    keyboard = [
        [InlineKeyboardButton(f"🔄 Toggle {mode_text}", callback_data=f"toggle_dry_{strategy_id}")],
        [InlineKeyboardButton("💰 Alterar Stake", callback_data=f"edit_stake_{strategy_id}")],
        [InlineKeyboardButton("📊 Max Trades", callback_data=f"edit_trades_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def toggle_strategy_dry_run(query, strategy_id: str):
    """Alternar modo dry-run de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    
    # Mostrar confirmação para modo LIVE
    summary = commander.controller.get_strategy_summary(strategy_id)
    if summary.get('dry_run', True):  # Vai mudar para LIVE
        message = f"""
⚠️ <b>CONFIRMAÇÃO NECESSÁRIA</b>

Você está prestes a alterar <b>{strategy_info['name']}</b> para modo <b>LIVE</b>!

🚨 <b>ATENÇÃO:</b>
• Modo LIVE usa dinheiro real
• Trades serão executados na exchange
• Certifique-se de ter configurado as chaves da API
• Recomenda-se testar em dry-run primeiro

Tem certeza que deseja continuar?
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Sim, ativar LIVE", callback_data=f"confirm_live_{strategy_id}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"config_{strategy_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        # Mudança para dry-run é segura
        await execute_dry_run_toggle(query, strategy_id)

async def execute_dry_run_toggle(query, strategy_id: str):
    """Executar a mudança de modo dry-run"""
    strategy_info = STRATEGIES[strategy_id]
    
    await query.edit_message_text(f"⏳ Alterando modo de {strategy_info['name']}...")
    
    result = commander.controller.toggle_dry_run(strategy_id)
    
    if result['success']:
        message = f"✅ <b>Sucesso!</b>\n\n{result['message']}"
        
        if result.get('restart_required'):
            message += "\n\n⚠️ Reinicialização necessária para aplicar mudanças."
            
            keyboard = [
                [InlineKeyboardButton("🔄 Reiniciar Agora", callback_data=f"action_restart_{strategy_id}")],
                [InlineKeyboardButton("⏭️ Reiniciar Depois", callback_data=f"config_{strategy_id}")]
            ]
        else:
            keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]]
    else:
        message = f"❌ <b>Erro!</b>\n\n{result['message']}"
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_detailed_stats(query, strategy_id: str):
    """Mostrar estatísticas detalhadas de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    stats = await commander.get_strategy_stats(strategy_id)
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    # Estatísticas do container
    container_stats = commander.controller.get_container_stats(strategy_info['container'])
    
    message = f"""
📊 <b>ESTATÍSTICAS - {strategy_info['name']}</b>

💹 <b>Trading (24h):</b>
• Trades: {stats.get('trades', 0)}
• P&L Total: {stats.get('total_profit', 0):.2f} USDT
• P&L Médio: {stats.get('avg_profit', 0):.2f} USDT
• Win Rate: {stats.get('win_rate', 0):.1f}%
• Melhor Trade: {stats.get('max_profit', 0):.2f} USDT
• Pior Trade: {stats.get('min_profit', 0):.2f} USDT

⚙️ <b>Configuração:</b>
• Modo: {'DRY-RUN' if summary.get('dry_run') else 'LIVE'}
• Stake: {summary.get('stake_amount', 0)} USDT
• Max Trades: {summary.get('max_open_trades', 0)}

🖥️ <b>Sistema:</b>
• Status: {summary.get('container_status', 'unknown')}
    """
    
    if 'error' not in container_stats:
        message += f"• CPU: {container_stats.get('cpu_percent', 0):.1f}%\n"
        message += f"• RAM: {container_stats.get('memory_usage_mb', 0):.1f}MB ({container_stats.get('memory_percent', 0):.1f}%)"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=f"stats_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
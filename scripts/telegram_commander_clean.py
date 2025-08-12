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
from enhanced_stats import enhanced_stats
from trade_notifier import trade_notifier
from trading_commands import trading_commands

# Import trend_predictor with error handling
try:
    from trend_predictor import trend_predictor
except ImportError as e:
    logging.warning(f"Could not import trend_predictor: {e}")
    trend_predictor = None

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
                if os.name == 'nt':  # Windows
                    try:
                        client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                    except:
                        client = docker.from_env()
                else:
                    client = docker.from_env()
                
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
/start - Menu principal interativo
/status - Status detalhado de todas as estratégias
/help - Esta ajuda

<b>Comandos Rápidos:</b>
/control - Acesso direto ao menu de controle
/stats - Estatísticas gerais
/quick - Status rápido sem botões
/emergency - 🚨 Parar todas as estratégias

<b>Funcionalidades:</b>
• 📊 Status em tempo real
• 🎮 Controle individual de estratégias
• 📈 Estatísticas detalhadas
• ⚙️ Configurações avançadas
• 💰 Ajuste de stake amount
• 🔄 Toggle DRY-RUN ↔ LIVE

<b>Segurança:</b>
• Apenas usuários autorizados
• Confirmação para ações críticas
• Todas as ações são logadas
• Parada de emergência disponível
    """
    
    await update.message.reply_text(message, parse_mode='HTML')

async def show_status_all(query):
    """Mostrar status detalhado de todas as estratégias"""
    message = "📊 <b>STATUS DETALHADO</b>\n\n"
    
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        summary = commander.controller.get_strategy_summary(strategy_id)
        
        status_emoji = "🟢" if status['running'] else "🔴"
        mode_emoji = "🟡" if summary.get('dry_run', True) else "🔴"
        mode_text = "DRY" if summary.get('dry_run', True) else "LIVE"
        
        message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
        message += f"   Status: {status['status']}\n"
        message += f"   Modo: {mode_emoji} {mode_text}\n"
        message += f"   Stake: {summary.get('stake_amount', 0)} {summary.get('stake_currency', 'USDT')}\n"
        message += f"   Max Trades: {summary.get('max_open_trades', 0)}\n"
        message += f"   Timeframe: {summary.get('timeframe', '15m')}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="status_all")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_control_menu(query):
    """Mostrar menu de controle de estratégias"""
    message = "🎮 <b>CONTROLAR ESTRATÉGIAS</b>\n\nEscolha uma estratégia para controlar:\n\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        status_emoji = "🟢" if status['running'] else "🔴"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{status_emoji} {strategy_info['name']}", 
                callback_data=f"strategy_{strategy_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_stats_menu(query):
    """Mostrar menu de estatísticas"""
    message = "📈 <b>ESTATÍSTICAS</b>\n\nEscolha uma estratégia para ver estatísticas:\n\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"📊 {strategy_info['name']}", 
                callback_data=f"stats_{strategy_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("📈 Resumo Geral", callback_data="stats_general")
    ])
    keyboard.append([
        InlineKeyboardButton("📊 Stats Horárias", callback_data="hourly_stats"),
        InlineKeyboardButton("🔔 Notificações", callback_data="notifications_menu")
    ])
    keyboard.append([
        InlineKeyboardButton("🔮 Previsões", callback_data="predictions_menu")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_config_menu(query):
    """Mostrar menu de configurações"""
    message = "⚙️ <b>CONFIGURAÇÕES</b>\n\nEscolha uma estratégia para configurar:\n\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"⚙️ {strategy_info['name']}", 
                callback_data=f"config_{strategy_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_help_menu(query):
    """Mostrar menu de ajuda"""
    message = """
🆘 <b>AJUDA - FREQTRADE COMMANDER</b>

<b>📊 Status Geral:</b>
• Ver status de todas as estratégias
• Informações de modo (DRY/LIVE)
• Configurações atuais

<b>🎮 Controlar Estratégias:</b>
• ▶️ Iniciar estratégia
• ⏹️ Parar estratégia
• 🔄 Reiniciar estratégia
• 📋 Ver logs em tempo real

<b>📈 Estatísticas:</b>
• Performance individual
• Trades realizados
• P&L (Profit & Loss)
• Win Rate

<b>⚙️ Configurações:</b>
• Alternar DRY-RUN ↔ LIVE
• Modificar stake amount
• Ajustar max trades
• Ver configuração completa

<b>🔐 Segurança:</b>
• Apenas usuários autorizados
• Confirmação para ações críticas
• Todas as ações são logadas

<b>ℹ️ Símbolos:</b>
• 🟢 = Rodando • 🔴 = Parado
• 🟡 = DRY-RUN • 🔴 = LIVE
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

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

Escolha uma opção abaixo para começar:
    """
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_control(query, strategy_id: str):
    """Mostrar controles de uma estratégia específica"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    status = await commander.get_container_status(strategy_info['container'])
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    status_emoji = "🟢" if status['running'] else "🔴"
    mode_emoji = "🟡" if summary.get('dry_run', True) else "🔴"
    mode_text = "DRY-RUN" if summary.get('dry_run', True) else "LIVE"
    
    message = f"""
🎮 <b>CONTROLE - {strategy_info['name']}</b>

📊 <b>Status Atual:</b>
• Status: {status_emoji} {status['status']}
• Modo: {mode_emoji} {mode_text}
• Stake: {summary.get('stake_amount', 0)} {summary.get('stake_currency', 'USDT')}
• Max Trades: {summary.get('max_open_trades', 0)}
• Timeframe: {summary.get('timeframe', '15m')}

🎯 <b>Ações Disponíveis:</b>
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
        [
            InlineKeyboardButton("📋 Logs", callback_data=f"logs_{strategy_id}"),
            InlineKeyboardButton("⚙️ Config", callback_data=f"config_{strategy_id}")
        ],
        [
            InlineKeyboardButton("📈 Stats", callback_data=f"stats_{strategy_id}"),
            InlineKeyboardButton("🔄 DRY/LIVE", callback_data=f"toggle_{strategy_id}")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="control_menu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def execute_strategy_action(query, strategy_id: str, action: str):
    """Executar ação em uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    container_name = strategy_info['container']
    
    await query.edit_message_text(f"⏳ Executando {action} em {strategy_info['name']}...")
    
    try:
        if action == "start":
            result = subprocess.run(['docker', 'start', container_name], capture_output=True, text=True)
        elif action == "stop":
            result = subprocess.run(['docker', 'stop', container_name], capture_output=True, text=True)
        elif action == "restart":
            result = subprocess.run(['docker', 'restart', container_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            message = f"✅ <b>{action.upper()} executado com sucesso!</b>\n\n"
            message += f"Estratégia: {strategy_info['name']}\n"
            message += f"Container: {container_name}\n"
            message += f"Ação: {action}\n"
            
            await asyncio.sleep(3)
            
            status = await commander.get_container_status(container_name)
            status_emoji = "🟢" if status['running'] else "🔴"
            message += f"Novo status: {status_emoji} {status['status']}"
        else:
            message = f"❌ <b>Erro ao executar {action}!</b>\n\n"
            message += f"Erro: {result.stderr}\n"
            message += f"Output: {result.stdout}\n"
            
    except Exception as e:
        message = f"❌ <b>Erro interno!</b>\n\nDetalhes: {str(e)}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=f"strategy_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="control_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_logs(query, strategy_id: str):
    """Mostrar logs de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    container_name = strategy_info['container']
    
    try:
        result = subprocess.run(['docker', 'logs', '--tail', '15', container_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
        else:
            logs = [f"Erro ao obter logs: {result.stderr}"]
    except Exception as e:
        logs = [f"Erro interno: {str(e)}"]
    
    message = f"📋 <b>LOGS - {strategy_info['name']}</b>\n\n"
    message += "<code>"
    
    recent_logs = []
    for line in logs:
        if line.strip():
            clean_line = line
            if ' - ' in line:
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    clean_line = parts[2]
            
            if any(keyword in clean_line.lower() for keyword in ['error', 'info', 'warning', 'started', 'stopped', 'exchange', 'strategy']):
                clean_line = clean_line[:100]
                recent_logs.append(clean_line)
    
    if recent_logs:
        message += "\n".join(recent_logs[-8:])
    else:
        message += "Nenhum log relevante encontrado."
    
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
        [
            InlineKeyboardButton("🔄 DRY/LIVE", callback_data=f"toggle_{strategy_id}"),
            InlineKeyboardButton("💰 Stake", callback_data=f"stake_{strategy_id}")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_stats(query, strategy_id: str):
    """Mostrar estatísticas de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    
    try:
        stats = commander.stats.get_strategy_stats(strategy_id)
        
        message = f"""
📈 <b>ESTATÍSTICAS - {strategy_info['name']}</b>

📊 <b>Performance:</b>
• Total Trades: {stats.get('total_trades', 0)}
• Trades Ganhos: {stats.get('winning_trades', 0)}
• Trades Perdidos: {stats.get('losing_trades', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%

💰 <b>Financeiro:</b>
• P&L Total: {stats.get('total_profit', 0):.2f} USDT
• P&L Hoje: {stats.get('profit_today', 0):.2f} USDT
• Melhor Trade: {stats.get('best_trade', 0):.2f} USDT
• Pior Trade: {stats.get('worst_trade', 0):.2f} USDT

📅 <b>Período:</b>
• Primeiro Trade: {stats.get('first_trade_date', 'N/A')}
• Último Trade: {stats.get('last_trade_date', 'N/A')}
• Dias Ativos: {stats.get('active_days', 0)}
        """
        
    except Exception as e:
        message = f"""
📈 <b>ESTATÍSTICAS - {strategy_info['name']}</b>

❌ <b>Erro ao carregar estatísticas:</b>
{str(e)}

💡 <b>Possíveis causas:</b>
• Estratégia nunca foi executada
• Banco de dados não acessível
• Configuração incorreta
        """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=f"stats_{strategy_id}")],
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_general_stats(query):
    """Mostrar estatísticas gerais de todas as estratégias"""
    message = "📈 <b>ESTATÍSTICAS GERAIS</b>\n\n"
    
    total_trades = 0
    total_profit = 0
    total_winning = 0
    total_losing = 0
    
    for strategy_id, strategy_info in STRATEGIES.items():
        try:
            stats = commander.stats.get_strategy_stats(strategy_id)
            
            trades = stats.get('total_trades', 0)
            profit = stats.get('total_profit', 0)
            winning = stats.get('winning_trades', 0)
            losing = stats.get('losing_trades', 0)
            
            total_trades += trades
            total_profit += profit
            total_winning += winning
            total_losing += losing
            
            status = await commander.get_container_status(strategy_info['container'])
            status_emoji = "🟢" if status['running'] else "🔴"
            
            message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
            message += f"   Trades: {trades} | P&L: {profit:.2f} USDT\n"
            message += f"   Win Rate: {(winning/(trades or 1)*100):.1f}%\n\n"
            
        except Exception as e:
            message += f"🔴 <b>{strategy_info['name']}</b>\n"
            message += f"   Erro: Sem dados disponíveis\n\n"
    
    overall_win_rate = (total_winning / (total_trades or 1)) * 100
    
    message += f"📊 <b>RESUMO GERAL:</b>\n"
    message += f"• Total de Trades: {total_trades}\n"
    message += f"• P&L Total: {total_profit:.2f} USDT\n"
    message += f"• Win Rate Geral: {overall_win_rate:.1f}%\n"
    message += f"• Trades Ganhos: {total_winning}\n"
    message += f"• Trades Perdidos: {total_losing}\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="stats_general")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="stats_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_hourly_stats_menu(query):
    """Mostrar menu de estatísticas horárias"""
    message = "📊 <b>ESTATÍSTICAS HORÁRIAS</b>\n\nEscolha uma estratégia:\n\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"📊 {strategy_info['name']}", 
                callback_data=f"hourly_{strategy_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("📈 Todas as Estratégias", callback_data="hourly_all")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="stats_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_hourly_stats(query, strategy_id: str):
    """Mostrar estatísticas horárias de uma estratégia"""
    try:
        if strategy_id == "all":
            message = "📊 <b>ESTATÍSTICAS HORÁRIAS - TODAS</b>\n\n"
            
            for strat_id, strat_info in STRATEGIES.items():
                hourly_summary = enhanced_stats.format_hourly_summary(strat_id, 6)
                message += f"🔹 <b>{strat_info['name']}</b>\n"
                
                # Get last 6 hours summary
                hourly_data = enhanced_stats.get_hourly_stats(strat_id, 6)
                if hourly_data:
                    total_trades = sum(h['trades'] for h in hourly_data)
                    total_profit = sum(h['profit'] for h in hourly_data)
                    profit_emoji = "🟢" if total_profit > 0 else "🔴" if total_profit < 0 else "⚪"
                    
                    message += f"   {profit_emoji} {total_trades} trades | {total_profit:.4f} USDT\n\n"
                else:
                    message += f"   ⚪ Sem dados disponíveis\n\n"
        else:
            strategy_info = STRATEGIES.get(strategy_id)
            if not strategy_info:
                await query.edit_message_text("❌ Estratégia não encontrada.")
                return
            
            message = enhanced_stats.format_hourly_summary(strategy_id, 12)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data=f"hourly_{strategy_id}")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="hourly_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao obter estatísticas: {str(e)}")

async def show_notifications_menu(query):
    """Mostrar menu de notificações"""
    # Check if notifications are active
    notifications_status = "🟢 ATIVAS" if trade_notifier.monitoring else "🔴 INATIVAS"
    
    message = f"🔔 <b>NOTIFICAÇÕES DE TRADE</b>\n\n"
    message += f"Status: {notifications_status}\n\n"
    message += f"📱 <b>Funcionalidades:</b>\n"
    message += f"• Alertas de compra em tempo real\n"
    message += f"• Alertas de venda com P&L\n"
    message += f"• Resumo diário automático\n"
    message += f"• Monitoramento contínuo\n\n"
    
    if trade_notifier.monitoring:
        message += f"⚡ Monitorando todas as estratégias ativas"
    else:
        message += f"💤 Notificações desativadas"
    
    keyboard = []
    
    if trade_notifier.monitoring:
        keyboard.append([
            InlineKeyboardButton("🔴 Desativar Notificações", callback_data="notifications_stop")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🟢 Ativar Notificações", callback_data="notifications_start")
        ])
    
    keyboard.append([
        InlineKeyboardButton("📊 Enviar Resumo Diário", callback_data="send_daily_summary")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="stats_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def toggle_notifications(query, action: str):
    """Ativar/desativar notificações"""
    try:
        if action == "start":
            if not trade_notifier.monitoring:
                # Set up the notifier with current bot and chat
                trade_notifier.set_telegram_bot(query.bot, query.message.chat_id)
                
                # Start monitoring in background
                strategies = list(STRATEGIES.keys())
                asyncio.create_task(trade_notifier.start_monitoring(strategies))
                
                message = "🟢 <b>NOTIFICAÇÕES ATIVADAS!</b>\n\n"
                message += "✅ Monitoramento iniciado\n"
                message += "📱 Você receberá alertas de:\n"
                message += "• Compras realizadas\n"
                message += "• Vendas com resultado\n"
                message += "• Resumos diários\n\n"
                message += "🔔 Notificações ativas para todas as estratégias"
            else:
                message = "⚠️ Notificações já estão ativas!"
        
        elif action == "stop":
            if trade_notifier.monitoring:
                trade_notifier.stop_monitoring()
                message = "🔴 <b>NOTIFICAÇÕES DESATIVADAS</b>\n\n"
                message += "❌ Monitoramento parado\n"
                message += "💤 Você não receberá mais alertas automáticos\n\n"
                message += "💡 Pode reativar a qualquer momento"
            else:
                message = "⚠️ Notificações já estão inativas!"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Voltar", callback_data="notifications_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao configurar notificações: {str(e)}")

async def send_daily_summary_manual(query):
    """Enviar resumo diário manualmente"""
    try:
        strategies = list(STRATEGIES.keys())
        await trade_notifier.send_daily_summary(strategies)
        
        message = "📊 <b>RESUMO ENVIADO!</b>\n\n"
        message += "✅ Resumo diário enviado com sucesso\n"
        message += "📈 Verifique as mensagens acima\n\n"
        message += "💡 O resumo automático é enviado diariamente às 23:00"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Voltar", callback_data="notifications_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao enviar resumo: {str(e)}")

async def show_predictions_menu(query):
    """Mostrar menu de previsões de tendência"""
    message = "🔮 <b>PREVISÕES DE TENDÊNCIA</b>\n\n"
    message += "📈 <b>Análise Preditiva Avançada</b>\n"
    message += "Baseada em padrões históricos e indicadores técnicos\n\n"
    message += "🎯 <b>Funcionalidades:</b>\n"
    message += "• Previsão de tendências (alta/baixa/lateral)\n"
    message += "• Análise de confiança e força do sinal\n"
    message += "• Identificação de melhores horários\n"
    message += "• Recomendações de ação\n"
    message += "• Análise de risco\n\n"
    message += "Escolha uma estratégia para análise:\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"🔮 {strategy_info['name']}", 
                callback_data=f"predict_{strategy_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("📊 Análise Geral", callback_data="predict_all")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="stats_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_prediction(query, strategy_id: str):
    """Mostrar previsão detalhada de uma estratégia"""
    if not trend_predictor:
        await query.edit_message_text("❌ Sistema de previsão não disponível.")
        return
        
    try:
        if strategy_id == "all":
            message = "🔮 <b>ANÁLISE PREDITIVA GERAL</b>\n\n"
            
            total_bullish = 0
            total_bearish = 0
            total_sideways = 0
            high_confidence_predictions = []
            
            for strat_id, strat_info in STRATEGIES.items():
                try:
                    prediction = trend_predictor.generate_prediction(strat_id)
                    
                    if prediction['prediction'] == 'upward':
                        trend_emoji = "📈"
                        total_bullish += 1
                    elif prediction['prediction'] == 'downward':
                        trend_emoji = "📉"
                        total_bearish += 1
                    else:
                        trend_emoji = "➡️"
                        total_sideways += 1
                    
                    confidence = prediction['confidence']
                    conf_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
                    
                    message += f"{trend_emoji} <b>{strat_info['name']}</b>\n"
                    message += f"   {conf_emoji} Confiança: {confidence:.1%} | {prediction['signal_strength'].title()}\n"
                    message += f"   💡 {prediction['recommended_action']}\n\n"
                    
                    if confidence > 0.7:
                        high_confidence_predictions.append({
                            'strategy': strat_info['name'],
                            'prediction': prediction['prediction'],
                            'confidence': confidence
                        })
                        
                except Exception as e:
                    message += f"🔴 <b>{strat_info['name']}</b>\n"
                    message += f"   ❌ Erro na análise\n\n"
            
            # Market sentiment summary
            total_strategies = len(STRATEGIES)
            message += f"📊 <b>SENTIMENTO GERAL DO MERCADO:</b>\n"
            message += f"📈 Bullish: {total_bullish}/{total_strategies} ({total_bullish/total_strategies*100:.0f}%)\n"
            message += f"📉 Bearish: {total_bearish}/{total_strategies} ({total_bearish/total_strategies*100:.0f}%)\n"
            message += f"➡️ Lateral: {total_sideways}/{total_strategies} ({total_sideways/total_strategies*100:.0f}%)\n\n"
            
            if high_confidence_predictions:
                message += f"⭐ <b>SINAIS DE ALTA CONFIANÇA:</b>\n"
                for pred in high_confidence_predictions[:3]:
                    trend_emoji = "📈" if pred['prediction'] == 'upward' else "📉" if pred['prediction'] == 'downward' else "➡️"
                    message += f"{trend_emoji} {pred['strategy']} - {pred['confidence']:.1%}\n"
            else:
                message += f"⚠️ <b>Nenhum sinal de alta confiança detectado</b>\n"
            
        else:
            strategy_info = STRATEGIES.get(strategy_id)
            if not strategy_info:
                await query.edit_message_text("❌ Estratégia não encontrada.")
                return
            
            message = trend_predictor.format_prediction_message(strategy_id)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar Análise", callback_data=f"predict_{strategy_id}")],
            [InlineKeyboardButton("📊 Ver Estatísticas", callback_data=f"stats_{strategy_id}" if strategy_id != "all" else "stats_general")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="predictions_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao gerar previsão: {str(e)}")

async def send_prediction_alert(query, strategy_id: str):
    """Enviar alerta de previsão"""
    if not trend_predictor:
        await query.edit_message_text("❌ Sistema de previsão não disponível.")
        return
        
    try:
        prediction = trend_predictor.generate_prediction(strategy_id)
        
        if prediction['confidence'] > 0.7 and prediction['signal_strength'] == 'strong':
            strategy_info = STRATEGIES.get(strategy_id, {'name': strategy_id})
            
            if prediction['prediction'] == 'upward':
                alert_emoji = "🚀"
                alert_text = "SINAL DE ALTA FORTE"
            elif prediction['prediction'] == 'downward':
                alert_emoji = "⚠️"
                alert_text = "SINAL DE BAIXA FORTE"
            else:
                return  # Don't send alerts for sideways
            
            message = f"{alert_emoji} <b>ALERTA DE PREVISÃO</b>\n\n"
            message += f"📊 <b>Estratégia:</b> {strategy_info['name']}\n"
            message += f"🎯 <b>Sinal:</b> {alert_text}\n"
            message += f"🟢 <b>Confiança:</b> {prediction['confidence']:.1%}\n"
            message += f"💡 <b>Ação:</b> {prediction['recommended_action']}\n\n"
            message += f"⏰ <b>Gerado em:</b> {datetime.now().strftime('%H:%M:%S')}"
            
            # Send to current chat
            await query.bot.send_message(
                chat_id=query.message.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            confirmation = f"🚀 <b>Alerta enviado!</b>\n\n"
            confirmation += f"Sinal de alta confiança detectado para {strategy_info['name']}\n"
            confirmation += f"Confiança: {prediction['confidence']:.1%}"
            
        else:
            confirmation = f"📊 <b>Análise Concluída</b>\n\n"
            confirmation += f"Nenhum sinal de alta confiança detectado no momento.\n"
            confirmation += f"Confiança atual: {prediction['confidence']:.1%}\n"
            confirmation += f"Continue monitorando para oportunidades."
        
        keyboard = [
            [InlineKeyboardButton("🔙 Voltar", callback_data="predictions_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(confirmation, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao enviar alerta: {str(e)}")

async def show_trading_menu(query):
    """Mostrar menu de trading manual"""
    message = "💰 <b>TRADING MANUAL</b>\n\n"
    message += "🎯 <b>Controle Total de Trading</b>\n"
    message += "Execute operações manuais e ajuste estratégias\n\n"
    message += "🔧 <b>Funcionalidades:</b>\n"
    message += "• Compra/venda forçada de pares\n"
    message += "• Ajuste dinâmico de sensibilidade\n"
    message += "• Análise de posições abertas\n"
    message += "• Recomendações baseadas no mercado\n\n"
    message += "Escolha uma estratégia:\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"💰 {strategy_info['name']}", 
                callback_data=f"trading_{strategy_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("📊 Análise Geral", callback_data="trading_analysis")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_strategy_trading(query, strategy_id: str):
    """Mostrar opções de trading para uma estratégia"""
    try:
        strategy_info = STRATEGIES.get(strategy_id)
        if not strategy_info:
            await query.edit_message_text("❌ Estratégia não encontrada.")
            return
        
        # Get trading status
        status_message = trading_commands.format_trading_status(strategy_id)
        
        keyboard = [
            [
                InlineKeyboardButton("🟢 Compra Forçada", callback_data=f"forcebuy_{strategy_id}"),
                InlineKeyboardButton("🔴 Venda Forçada", callback_data=f"forcesell_{strategy_id}")
            ],
            [
                InlineKeyboardButton("🔥 Modo Agressivo", callback_data=f"adjust_{strategy_id}_aggressive"),
                InlineKeyboardButton("🛡️ Modo Conservador", callback_data=f"adjust_{strategy_id}_conservative")
            ],
            [
                InlineKeyboardButton("⚖️ Modo Equilibrado", callback_data=f"adjust_{strategy_id}_balanced")
            ],
            [
                InlineKeyboardButton("🔄 Atualizar Status", callback_data=f"trading_{strategy_id}"),
                InlineKeyboardButton("📊 Ver Estatísticas", callback_data=f"stats_{strategy_id}")
            ],
            [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(status_message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao obter status de trading: {str(e)}")

async def show_forcebuy_menu(query, strategy_id: str):
    """Mostrar menu de compra forçada"""
    message = f"🟢 <b>COMPRA FORÇADA - {strategy_id}</b>\n\n"
    message += "Selecione um par para compra forçada:\n\n"
    message += "⚠️ <b>Atenção:</b> Esta operação irá executar uma compra imediatamente, independente dos sinais da estratégia.\n\n"
    
    # Common trading pairs
    pairs = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", 
        "DOT/USDT", "LINK/USDT", "SOL/USDT", "MATIC/USDT"
    ]
    
    keyboard = []
    for i in range(0, len(pairs), 2):
        row = []
        for j in range(2):
            if i + j < len(pairs):
                pair = pairs[i + j]
                row.append(InlineKeyboardButton(
                    pair, 
                    callback_data=f"buy_{strategy_id}_{pair.replace('/', '_')}"
                ))
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("✏️ Par Personalizado", callback_data=f"custom_buy_{strategy_id}")
    ])
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data=f"trading_{strategy_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_forcesell_menu(query, strategy_id: str):
    """Mostrar menu de venda forçada"""
    try:
        success, trades = trading_commands.get_open_trades(strategy_id)
        
        message = f"🔴 <b>VENDA FORÇADA - {strategy_id}</b>\n\n"
        
        if success and trades:
            message += f"Posições abertas ({len(trades)}):\n\n"
            
            keyboard = []
            for trade in trades[:8]:  # Max 8 trades
                pair = trade['pair']
                amount = trade['amount']
                profit = trade.get('profit', 'N/A')
                
                button_text = f"{pair} ({amount}) - {profit}"
                keyboard.append([InlineKeyboardButton(
                    button_text, 
                    callback_data=f"sell_{strategy_id}_{pair.replace('/', '_')}"
                )])
            
            keyboard.append([
                InlineKeyboardButton("🔴 Vender TODAS", callback_data=f"sell_all_{strategy_id}")
            ])
        else:
            message += "💤 Nenhuma posição aberta para venda.\n\n"
            keyboard = []
        
        keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data=f"trading_{strategy_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro ao obter posições: {str(e)}")

async def execute_force_buy(query, strategy_id: str, pair: str):
    """Executar compra forçada"""
    try:
        pair = pair.replace('_', '/')
        
        # Show processing message
        await query.edit_message_text(f"⏳ Executando compra forçada...\n\nPar: {pair}\nEstratégia: {strategy_id}")
        
        success, message = trading_commands.force_buy(strategy_id, pair)
        
        if success:
            result_message = f"🟢 <b>COMPRA EXECUTADA COM SUCESSO!</b>\n\n{message}"
        else:
            result_message = f"❌ <b>ERRO NA COMPRA</b>\n\n{message}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Nova Compra", callback_data=f"forcebuy_{strategy_id}")],
            [InlineKeyboardButton("📊 Ver Status", callback_data=f"trading_{strategy_id}")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(result_message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro interno: {str(e)}")

async def execute_force_sell(query, strategy_id: str, pair: str):
    """Executar venda forçada"""
    try:
        if pair == "all":
            pair_text = "TODAS AS POSIÇÕES"
        else:
            pair = pair.replace('_', '/')
            pair_text = pair
        
        # Show processing message
        await query.edit_message_text(f"⏳ Executando venda forçada...\n\nPar: {pair_text}\nEstratégia: {strategy_id}")
        
        if pair == "TODAS AS POSIÇÕES":
            # Get all open trades and sell them
            success, trades = trading_commands.get_open_trades(strategy_id)
            if success and trades:
                results = []
                for trade in trades:
                    trade_pair = trade['pair']
                    sell_success, sell_message = trading_commands.force_sell(strategy_id, trade_pair)
                    results.append(f"• {trade_pair}: {'✅' if sell_success else '❌'}")
                
                result_message = f"🔴 <b>VENDA EM LOTE EXECUTADA</b>\n\n" + "\n".join(results)
            else:
                result_message = "❌ Nenhuma posição encontrada para venda"
        else:
            success, message = trading_commands.force_sell(strategy_id, pair)
            
            if success:
                result_message = f"🔴 <b>VENDA EXECUTADA COM SUCESSO!</b>\n\n{message}"
            else:
                result_message = f"❌ <b>ERRO NA VENDA</b>\n\n{message}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Nova Venda", callback_data=f"forcesell_{strategy_id}")],
            [InlineKeyboardButton("📊 Ver Status", callback_data=f"trading_{strategy_id}")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(result_message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro interno: {str(e)}")

async def adjust_strategy_mode(query, strategy_id: str, mode: str):
    """Ajustar modo da estratégia"""
    try:
        # Show processing message
        mode_names = {
            'aggressive': '🔥 AGRESSIVO',
            'conservative': '🛡️ CONSERVADOR', 
            'balanced': '⚖️ EQUILIBRADO'
        }
        
        await query.edit_message_text(f"⏳ Ajustando estratégia para modo {mode_names[mode]}...")
        
        success, message = trading_commands.adjust_strategy_sensitivity(strategy_id, mode)
        
        if success:
            result_message = f"✅ <b>ESTRATÉGIA AJUSTADA!</b>\n\n{message}"
        else:
            result_message = f"❌ <b>ERRO NO AJUSTE</b>\n\n{message}"
        
        keyboard = [
            [InlineKeyboardButton("📊 Ver Status", callback_data=f"trading_{strategy_id}")],
            [InlineKeyboardButton("🔄 Outro Ajuste", callback_data=f"trading_{strategy_id}")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(result_message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro interno: {str(e)}")

async def show_trading_analysis(query):
    """Mostrar análise geral de trading"""
    try:
        message = "📊 <b>ANÁLISE GERAL DE TRADING</b>\n\n"
        
        # Get market analysis
        analysis = trading_commands.get_market_analysis()
        
        message += f"📈 <b>Condições de Mercado:</b>\n"
        message += f"• Volatilidade: {analysis['volatility']:.1%}\n"
        message += f"• Tendência: {analysis['trend'].title()}\n"
        message += f"• Volume: {analysis['volume']:.1%}\n\n"
        
        message += f"💡 <b>Recomendação Geral:</b>\n"
        message += f"• Modo: {analysis['recommended_mode'].title()}\n"
        message += f"• Motivo: {analysis['reason']}\n\n"
        
        # Strategy recommendations
        message += f"🎯 <b>Recomendações por Estratégia:</b>\n"
        
        for strategy_id, strategy_info in STRATEGIES.items():
            try:
                status_msg = trading_commands.format_trading_status(strategy_id)
                # Extract key info (simplified)
                message += f"• {strategy_info['name']}: Modo {analysis['recommended_mode']}\n"
            except:
                message += f"• {strategy_info['name']}: Análise indisponível\n"
        
        message += f"\n⚠️ <b>Dicas de Trading:</b>\n"
        if analysis['volatility'] > 0.6:
            message += "• Alta volatilidade: Use stop-loss mais apertado\n"
            message += "• Considere reduzir tamanho das posições\n"
        elif analysis['trend'] == 'bullish':
            message += "• Tendência de alta: Considere posições longas\n"
            message += "• Aproveite pullbacks para entrar\n"
        else:
            message += "• Mercado lateral: Foque em scalping\n"
            message += "• Aguarde breakouts para posições maiores\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar Análise", callback_data="trading_analysis")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        await query.edit_message_text(f"❌ Erro na análise: {str(e)}")

async def toggle_strategy_dry_run(query, strategy_id: str):
    """Alternar modo dry-run de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    current_mode = "DRY-RUN" if summary.get('dry_run', True) else "LIVE"
    new_mode = "LIVE" if current_mode == "DRY-RUN" else "DRY-RUN"
    
    if new_mode == "LIVE":
        message = f"""
⚠️ <b>CONFIRMAÇÃO NECESSÁRIA</b>

Você está prestes a alterar a estratégia <b>{strategy_info['name']}</b> para modo <b>LIVE</b>.

🚨 <b>ATENÇÃO:</b>
• Modo LIVE usa dinheiro real
• Trades serão executados na exchange
• Certifique-se de que a estratégia está testada
• Verifique o stake amount: {summary.get('stake_amount', 0)} USDT

Tem certeza que deseja continuar?
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar LIVE", callback_data=f"confirm_live_{strategy_id}"),
                InlineKeyboardButton("❌ Cancelar", callback_data=f"strategy_{strategy_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await execute_mode_change(query, strategy_id, True)

async def execute_mode_change(query, strategy_id: str, dry_run: bool):
    """Executar mudança de modo"""
    strategy_info = STRATEGIES[strategy_id]
    mode_text = "DRY-RUN" if dry_run else "LIVE"
    
    await query.edit_message_text(f"⏳ Alterando modo de {strategy_info['name']} para {mode_text}...")
    
    try:
        result = commander.controller.toggle_dry_run(strategy_id)
        
        if result.get('success', False):
            message = f"✅ <b>Modo alterado com sucesso!</b>\n\n"
            message += f"Estratégia: {strategy_info['name']}\n"
            message += f"Novo modo: {result.get('new_mode', mode_text)}\n\n"
            message += "⚠️ <b>Reinicialização necessária</b>\n"
            message += "A estratégia precisa ser reiniciada para aplicar as mudanças."
            
            keyboard = [
                [InlineKeyboardButton("🔄 Reiniciar Agora", callback_data=f"action_restart_{strategy_id}")],
                [InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]
            ]
        else:
            message = f"❌ <b>Erro ao alterar modo!</b>\n\n{result.get('message', 'Erro desconhecido')}"
            keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]]
            
    except Exception as e:
        message = f"❌ <b>Erro interno!</b>\n\nDetalhes: {str(e)}"
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"strategy_{strategy_id}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_stake_config(query, strategy_id: str):
    """Mostrar configuração de stake amount"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    if 'error' in summary:
        await query.edit_message_text(f"❌ Erro: {summary['error']}")
        return
    
    current_stake = summary.get('stake_amount', 0)
    currency = summary.get('stake_currency', 'USDT')
    
    message = f"""
💰 <b>CONFIGURAÇÃO DE STAKE - {strategy_info['name']}</b>

📊 <b>Configuração Atual:</b>
• Stake Amount: {current_stake} {currency}
• Max Trades: {summary.get('max_open_trades', 0)}
• Modo: {"DRY-RUN" if summary.get('dry_run', True) else "LIVE"}

⚠️ <b>Opções de Stake:</b>
Selecione um novo valor de stake:
    """
    
    stake_options = [10, 20, 50, 100, 200, 500]
    
    keyboard = []
    row = []
    for i, stake in enumerate(stake_options):
        emoji = "✅" if stake == current_stake else "💰"
        row.append(InlineKeyboardButton(f"{emoji} {stake} {currency}", callback_data=f"set_stake_{strategy_id}_{stake}"))
        
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def set_stake_amount(query, strategy_id: str, stake_amount: int):
    """Definir novo stake amount"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    
    await query.edit_message_text(f"⏳ Alterando stake de {strategy_info['name']} para {stake_amount} USDT...")
    
    try:
        result = commander.controller.update_stake_amount(strategy_id, stake_amount)
        
        if result.get('success', False):
            message = f"✅ <b>Stake alterado com sucesso!</b>\n\n"
            message += f"Estratégia: {strategy_info['name']}\n"
            message += f"Novo stake: {stake_amount} USDT\n\n"
            message += "⚠️ <b>Reinicialização necessária</b>\n"
            message += "A estratégia precisa ser reiniciada para aplicar as mudanças."
            
            keyboard = [
                [InlineKeyboardButton("🔄 Reiniciar Agora", callback_data=f"action_restart_{strategy_id}")],
                [InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]
            ]
        else:
            message = f"❌ <b>Erro ao alterar stake!</b>\n\n{result.get('message', 'Erro desconhecido')}"
            keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]]
            
    except Exception as e:
        message = f"❌ <b>Erro interno!</b>\n\nDetalhes: {str(e)}"
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data=f"config_{strategy_id}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback para botões inline"""
    query = update.callback_query
    await query.answer()
    
    if not commander.is_admin(query.from_user.id):
        await query.edit_message_text("❌ Acesso negado.")
        return
    
    data = query.data
    logger.info(f"🔘 Callback recebido: {data}")
    
    if not data or data.strip() == "":
        await query.edit_message_text("❌ Comando inválido (callback vazio).")
        return
    
    try:
        if data == "status_all":
            await show_status_all(query)
        elif data == "control_menu":
            await show_control_menu(query)
        elif data == "stats_menu":
            await show_stats_menu(query)
        elif data == "config_menu":
            await show_config_menu(query)
        elif data == "help":
            await show_help_menu(query)
        elif data == "main_menu":
            await show_main_menu(query)
        elif data.startswith("strategy_"):
            strategy_id = data.replace("strategy_", "")
            await show_strategy_control(query, strategy_id)
        elif data.startswith("action_"):
            parts = data.split("_", 2)
            action = parts[1]
            strategy_id = parts[2]
            await execute_strategy_action(query, strategy_id, action)
        elif data.startswith("logs_"):
            strategy_id = data.replace("logs_", "")
            await show_strategy_logs(query, strategy_id)
        elif data.startswith("config_"):
            strategy_id = data.replace("config_", "")
            await show_strategy_config(query, strategy_id)
        elif data.startswith("stats_"):
            strategy_id = data.replace("stats_", "")
            await show_strategy_stats(query, strategy_id)
        elif data.startswith("toggle_"):
            strategy_id = data.replace("toggle_", "")
            await toggle_strategy_dry_run(query, strategy_id)
        elif data.startswith("confirm_live_"):
            strategy_id = data.replace("confirm_live_", "")
            await execute_mode_change(query, strategy_id, False)
        elif data.startswith("stake_"):
            strategy_id = data.replace("stake_", "")
            await show_stake_config(query, strategy_id)
        elif data.startswith("set_stake_"):
            parts = data.split("_", 3)
            strategy_id = parts[2]
            stake_amount = int(parts[3])
            await set_stake_amount(query, strategy_id, stake_amount)
        elif data == "stats_general":
            await show_general_stats(query)
        elif data == "hourly_stats":
            await show_hourly_stats_menu(query)
        elif data.startswith("hourly_"):
            strategy_id = data.replace("hourly_", "")
            await show_hourly_stats(query, strategy_id)
        elif data == "notifications_menu":
            await show_notifications_menu(query)
        elif data == "notifications_start":
            await toggle_notifications(query, "start")
        elif data == "notifications_stop":
            await toggle_notifications(query, "stop")
        elif data == "send_daily_summary":
            await send_daily_summary_manual(query)
        elif data == "predictions_menu":
            await show_predictions_menu(query)
        elif data.startswith("predict_"):
            strategy_id = data.replace("predict_", "")
            await show_strategy_prediction(query, strategy_id)
        elif data.startswith("alert_"):
            strategy_id = data.replace("alert_", "")
            await send_prediction_alert(query, strategy_id)
        elif data == "trading_menu":
            await show_trading_menu(query)
        elif data.startswith("trading_"):
            if data == "trading_analysis":
                await show_trading_analysis(query)
            else:
                strategy_id = data.replace("trading_", "")
                await show_strategy_trading(query, strategy_id)
        elif data.startswith("forcebuy_"):
            strategy_id = data.replace("forcebuy_", "")
            await show_forcebuy_menu(query, strategy_id)
        elif data.startswith("forcesell_"):
            strategy_id = data.replace("forcesell_", "")
            await show_forcesell_menu(query, strategy_id)
        elif data.startswith("buy_"):
            parts = data.split("_", 2)
            strategy_id = parts[1]
            pair = parts[2]
            await execute_force_buy(query, strategy_id, pair)
        elif data.startswith("sell_"):
            parts = data.split("_", 2)
            strategy_id = parts[1]
            pair = parts[2]
            await execute_force_sell(query, strategy_id, pair)
        elif data.startswith("sell_all_"):
            strategy_id = data.replace("sell_all_", "")
            await execute_force_sell(query, strategy_id, "all")
        elif data.startswith("adjust_"):
            parts = data.split("_", 2)
            strategy_id = parts[1]
            mode = parts[2]
            await adjust_strategy_mode(query, strategy_id, mode)
        else:
            await query.edit_message_text("❌ Comando não reconhecido.")
            
    except NameError as e:
        logger.error(f"🚨 NameError no callback {data}: {e}")
        await query.edit_message_text(f"❌ Erro interno: Função não encontrada.\n\nCallback: {data}\nErro: {str(e)}")
    except Exception as e:
        logger.error(f"🚨 Erro no callback {data}: {e}")
        await query.edit_message_text(f"❌ Erro interno: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para capturar erros"""
    logger.error(f"🚨 Erro capturado: {context.error}")
    logger.error(f"📍 Update: {update}")
    
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Ocorreu um erro interno. Por favor, tente novamente."
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de erro: {e}")

async def control_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /control - Acesso direto ao menu de controle"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    # Simular callback para mostrar menu de controle
    class FakeQuery:
        def __init__(self, chat_id):
            self.message = type('obj', (object,), {'chat_id': chat_id})()
        
        async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    fake_query = FakeQuery(update.effective_chat.id)
    await show_control_menu(fake_query)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Acesso direto às estatísticas"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    # Simular callback para mostrar estatísticas gerais
    class FakeQuery:
        def __init__(self, chat_id):
            self.message = type('obj', (object,), {'chat_id': chat_id})()
        
        async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    fake_query = FakeQuery(update.effective_chat.id)
    await show_general_stats(fake_query)

async def emergency_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /emergency - Parar todas as estratégias imediatamente"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("🚨 <b>PARADA DE EMERGÊNCIA INICIADA</b>\n\nParando todas as estratégias...", parse_mode='HTML')
    
    results = []
    for strategy_id, strategy_info in STRATEGIES.items():
        try:
            result = subprocess.run([
                'docker', 'stop', strategy_info['container']
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                results.append(f"✅ {strategy_info['name']}: Parada")
            else:
                results.append(f"❌ {strategy_info['name']}: Erro")
        except Exception as e:
            results.append(f"❌ {strategy_info['name']}: {str(e)}")
    
    message = "🚨 <b>PARADA DE EMERGÊNCIA CONCLUÍDA</b>\n\n"
    message += "\n".join(results)
    
    await update.message.reply_text(message, parse_mode='HTML')

async def quick_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /quick - Status rápido sem botões"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    message = "⚡ <b>STATUS RÁPIDO</b>\n\n"
    
    for strategy_id, strategy_info in STRATEGIES.items():
        status = await commander.get_container_status(strategy_info['container'])
        summary = commander.controller.get_strategy_summary(strategy_id)
        
        status_emoji = "🟢" if status['running'] else "🔴"
        mode_emoji = "🟡" if summary.get('dry_run', True) else "🔴"
        
        message += f"{status_emoji}{mode_emoji} {strategy_info['name']}: {status['status']}\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /predict - Previsões rápidas de todas as estratégias"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    message = "🔮 <b>PREVISÕES RÁPIDAS</b>\n\n"
    
    high_confidence_signals = []
    
    for strategy_id, strategy_info in STRATEGIES.items():
        try:
            prediction = trend_predictor.generate_prediction(strategy_id)
            
            if prediction['prediction'] == 'upward':
                trend_emoji = "📈"
                trend_text = "ALTA"
            elif prediction['prediction'] == 'downward':
                trend_emoji = "📉"
                trend_text = "BAIXA"
            else:
                trend_emoji = "➡️"
                trend_text = "LATERAL"
            
            confidence = prediction['confidence']
            conf_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
            
            message += f"{trend_emoji} <b>{strategy_info['name']}</b>\n"
            message += f"   {conf_emoji} {trend_text} - {confidence:.1%}\n"
            message += f"   💡 {prediction['recommended_action']}\n\n"
            
            if confidence > 0.7:
                high_confidence_signals.append({
                    'name': strategy_info['name'],
                    'prediction': trend_text,
                    'confidence': confidence
                })
                
        except Exception as e:
            message += f"🔴 <b>{strategy_info['name']}</b>\n"
            message += f"   ❌ Erro na análise\n\n"
    
    if high_confidence_signals:
        message += f"⭐ <b>SINAIS DE ALTA CONFIANÇA:</b>\n"
        for signal in high_confidence_signals:
            message += f"🚀 {signal['name']}: {signal['prediction']} ({signal['confidence']:.1%})\n"
    else:
        message += f"📊 <i>Nenhum sinal de alta confiança no momento</i>\n"
    
    message += f"\n💡 Use /stats → 🔮 Previsões para análise detalhada"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def forcebuy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcebuy - Compra forçada direta"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    # Parse arguments: /forcebuy strategy pair [amount]
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso incorreto.\n\n"
            "📝 <b>Formato:</b>\n"
            "<code>/forcebuy [estratégia] [par] [quantidade]</code>\n\n"
            "📋 <b>Exemplos:</b>\n"
            "<code>/forcebuy stratA BTC/USDT</code>\n"
            "<code>/forcebuy waveHyperNW ETH/USDT 0.1</code>\n\n"
            "🎯 <b>Estratégias disponíveis:</b>\n" + 
            "\n".join([f"• {sid}" for sid in STRATEGIES.keys()]),
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    pair = args[1]
    amount = float(args[2]) if len(args) > 2 else None
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    # Execute buy
    await update.message.reply_text(f"⏳ Executando compra forçada...\n\nPar: {pair}\nEstratégia: {strategy_id}")
    
    success, message = trading_commands.force_buy(strategy_id, pair, amount)
    
    if success:
        result = f"🟢 <b>COMPRA EXECUTADA!</b>\n\n{message}"
    else:
        result = f"❌ <b>ERRO NA COMPRA</b>\n\n{message}"
    
    await update.message.reply_text(result, parse_mode='HTML')

async def forcesell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcesell - Venda forçada direta"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    # Parse arguments: /forcesell strategy pair [amount]
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso incorreto.\n\n"
            "📝 <b>Formato:</b>\n"
            "<code>/forcesell [estratégia] [par] [quantidade]</code>\n\n"
            "📋 <b>Exemplos:</b>\n"
            "<code>/forcesell stratA BTC/USDT</code>\n"
            "<code>/forcesell waveHyperNW ETH/USDT 0.1</code>\n"
            "<code>/forcesell stratA all</code> (vender tudo)\n\n"
            "🎯 <b>Estratégias disponíveis:</b>\n" + 
            "\n".join([f"• {sid}" for sid in STRATEGIES.keys()]),
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    pair = args[1]
    amount = float(args[2]) if len(args) > 2 and args[2] != 'all' else None
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    # Execute sell
    if pair.lower() == 'all':
        await update.message.reply_text(f"⏳ Executando venda de todas as posições...\nEstratégia: {strategy_id}")
        
        success, trades = trading_commands.get_open_trades(strategy_id)
        if success and trades:
            results = []
            for trade in trades:
                trade_pair = trade['pair']
                sell_success, sell_message = trading_commands.force_sell(strategy_id, trade_pair)
                results.append(f"• {trade_pair}: {'✅' if sell_success else '❌'}")
            
            result = f"🔴 <b>VENDA EM LOTE EXECUTADA</b>\n\n" + "\n".join(results)
        else:
            result = "❌ Nenhuma posição encontrada para venda"
    else:
        await update.message.reply_text(f"⏳ Executando venda forçada...\n\nPar: {pair}\nEstratégia: {strategy_id}")
        
        success, message = trading_commands.force_sell(strategy_id, pair, amount)
        
        if success:
            result = f"🔴 <b>VENDA EXECUTADA!</b>\n\n{message}"
        else:
            result = f"❌ <b>ERRO NA VENDA</b>\n\n{message}"
    
    await update.message.reply_text(result, parse_mode='HTML')

async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adjust - Ajustar sensibilidade da estratégia"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    # Parse arguments: /adjust strategy mode
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso incorreto.\n\n"
            "📝 <b>Formato:</b>\n"
            "<code>/adjust [estratégia] [modo]</code>\n\n"
            "📋 <b>Modos disponíveis:</b>\n"
            "• <code>aggressive</code> - Mais trades, ROI menor\n"
            "• <code>conservative</code> - Menos trades, ROI maior\n"
            "• <code>balanced</code> - Equilibrado\n\n"
            "📋 <b>Exemplos:</b>\n"
            "<code>/adjust stratA aggressive</code>\n"
            "<code>/adjust waveHyperNW conservative</code>\n\n"
            "🎯 <b>Estratégias disponíveis:</b>\n" + 
            "\n".join([f"• {sid}" for sid in STRATEGIES.keys()]),
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    mode = args[1].lower()
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    if mode not in ['aggressive', 'conservative', 'balanced']:
        await update.message.reply_text("❌ Modo inválido. Use: aggressive, conservative, balanced")
        return
    
    # Execute adjustment
    mode_names = {
        'aggressive': '🔥 AGRESSIVO',
        'conservative': '🛡️ CONSERVADOR', 
        'balanced': '⚖️ EQUILIBRADO'
    }
    
    await update.message.reply_text(f"⏳ Ajustando estratégia para modo {mode_names[mode]}...")
    
    success, message = trading_commands.adjust_strategy_sensitivity(strategy_id, mode)
    
    if success:
        result = f"✅ <b>ESTRATÉGIA AJUSTADA!</b>\n\n{message}"
    else:
        result = f"❌ <b>ERRO NO AJUSTE</b>\n\n{message}"
    
    await update.message.reply_text(result, parse_mode='HTML')

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
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("control", control_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("emergency", emergency_stop_command))
    application.add_handler(CommandHandler("quick", quick_status_command))
    application.add_handler(CommandHandler("predict", predict_command))
    application.add_handler(CommandHandler("forcebuy", forcebuy_command))
    application.add_handler(CommandHandler("forcesell", forcesell_command))
    application.add_handler(CommandHandler("adjust", adjust_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Telegram Commander iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
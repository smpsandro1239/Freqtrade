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
    elif data == "stats_general":
        await show_general_stats(query)
    else:
        await query.edit_message_text("❌ Comando não reconhecido.")

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
    
    # Mostrar mensagem de processamento
    await query.edit_message_text(f"⏳ Executando {action} em {strategy_info['name']}...")
    
    try:
        # Usar docker diretamente em vez de docker compose para melhor controle
        if action == "start":
            result = subprocess.run([
                'docker', 'start', container_name
            ], capture_output=True, text=True)
            
        elif action == "stop":
            result = subprocess.run([
                'docker', 'stop', container_name
            ], capture_output=True, text=True)
            
        elif action == "restart":
            result = subprocess.run([
                'docker', 'restart', container_name
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            message = f"✅ <b>{action.upper()} executado com sucesso!</b>\n\n"
            message += f"Estratégia: {strategy_info['name']}\n"
            message += f"Container: {container_name}\n"
            message += f"Ação: {action}\n"
            
            # Aguardar um pouco para o container atualizar
            await asyncio.sleep(3)
            
            # Verificar novo status
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
        # Obter logs diretamente do container
        result = subprocess.run([
            'docker', 'logs', '--tail', '15', container_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout.split('\n')
        else:
            logs = [f"Erro ao obter logs: {result.stderr}"]
    except Exception as e:
        logs = [f"Erro interno: {str(e)}"]
    
    message = f"📋 <b>LOGS - {strategy_info['name']}</b>\n\n"
    message += "<code>"
    
    # Filtrar e formatar logs
    recent_logs = []
    for line in logs:
        if line.strip():
            # Remover timestamp e container name para economizar espaço
            clean_line = line
            if ' - ' in line:
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    clean_line = parts[2]  # Pegar apenas a mensagem
            
            # Limitar tamanho e filtrar logs importantes
            if any(keyword in clean_line.lower() for keyword in ['error', 'info', 'warning', 'started', 'stopped', 'exchange', 'strategy']):
                clean_line = clean_line[:100]  # Limitar tamanho
                recent_logs.append(clean_line)
    
    if recent_logs:
        message += "\n".join(recent_logs[-8:])  # Últimas 8 linhas relevantes
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
        # Obter estatísticas básicas
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

async def toggle_strategy_dry_run(query, strategy_id: str):
    """Alternar modo dry-run de uma estratégia"""
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    strategy_info = STRATEGIES[strategy_id]
    summary = commander.controller.get_strategy_summary(strategy_id)
    
    current_mode = "DRY-RUN" if summary.get('dry_run', True) else "LIVE"
    new_mode = "LIVE" if current_mode == "DRY-RUN" else "DRY-RUN"
    
    # Se mudando para LIVE, mostrar confirmação
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
        # Mudança para DRY-RUN é segura, executar diretamente
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
    
    # Resumo geral
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
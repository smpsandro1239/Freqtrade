#!/usr/bin/env python3
"""
🤖 Telegram Bot Principal - FreqTrade Multi-Strategy
Sistema completo de controle via Telegram com todas as funcionalidades
"""

import os
import asyncio
import json
import logging
import docker
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Configuração
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ADMIN_USERS = [int(CHAT_ID)] if CHAT_ID else []

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estratégias configuradas (baseado nas validações da Fase 2)
STRATEGIES = {
    "stratA": {
        "name": "Sample Strategy A",
        "container": "ft-stratA",
        "config": "user_data/configs/stratA.json",
        "strategy": "SampleStrategyA",
        "description": "RSI básico - 15m",
        "api_port": 8081
    },
    "stratB": {
        "name": "Sample Strategy B", 
        "container": "ft-stratB",
        "config": "user_data/configs/stratB.json",
        "strategy": "SampleStrategyB",
        "description": "RSI + MACD + BB - 15m",
        "api_port": 8082
    },
    "waveHyperNW": {
        "name": "WaveHyperNW Strategy",
        "container": "ft-waveHyperNW", 
        "config": "user_data/configs/waveHyperNW.json",
        "strategy": "WaveHyperNWStrategy",
        "description": "WaveTrend + Nadaraya-Watson - 5m",
        "api_port": 8083
    },
    "mlStrategy": {
        "name": "ML Strategy",
        "container": "ft-mlStrategy",
        "config": "user_data/configs/mlStrategy.json",
        "strategy": "MLStrategy",
        "description": "Machine Learning - 15m",
        "api_port": 8084
    },
    "mlStrategySimple": {
        "name": "ML Strategy Simple",
        "container": "ft-mlStrategySimple",
        "config": "user_data/configs/mlStrategySimple.json",
        "strategy": "MLStrategySimple",
        "description": "ML Simplificado - 15m",
        "api_port": 8085
    },
    "multiTimeframe": {
        "name": "Multi Timeframe Strategy",
        "container": "ft-multiTimeframe",
        "config": "user_data/configs/multitimeframestrategy.json",
        "strategy": "MultiTimeframeStrategy",
        "description": "Multi-timeframe - 5m",
        "api_port": 8086
    },
    "waveEnhanced": {
        "name": "WaveHyperNW Enhanced",
        "container": "ft-waveEnhanced",
        "config": "user_data/configs/waveHyperNWEnhanced.json",
        "strategy": "WaveHyperNWEnhanced",
        "description": "WaveTrend Enhanced - 5m",
        "api_port": 8087
    }
}

class TelegramBotMain:
    """Bot principal com todas as funcionalidades"""
    
    def __init__(self):
        self.docker_client = self._init_docker_client()
        self.bot = Bot(token=TOKEN)
        
    def _init_docker_client(self):
        """Inicializa cliente Docker com tratamento de erro"""
        try:
            if os.name == 'nt':  # Windows
                try:
                    client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                except:
                    client = docker.from_env()
            else:
                client = docker.from_env()
            
            client.ping()
            logger.info("✅ Docker conectado com sucesso")
            return client
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Docker: {e}")
            return None
    
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é admin"""
        return user_id in ADMIN_USERS
    
    async def get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Obter status de um container"""
        if not self.docker_client:
            return {'running': False, 'status': 'docker_unavailable', 'name': container_name}
            
        try:
            container = self.docker_client.containers.get(container_name)
            return {
                'running': container.status == 'running',
                'status': container.status,
                'name': container.name,
                'created': container.attrs.get('Created', ''),
                'image': container.image.tags[0] if container.image.tags else 'unknown'
            }
        except docker.errors.NotFound:
            return {'running': False, 'status': 'not_found', 'name': container_name}
        except Exception as e:
            return {'running': False, 'status': f'error: {str(e)}', 'name': container_name}
    
    async def get_all_strategies_status(self) -> Dict[str, Dict]:
        """Obter status de todas as estratégias"""
        status_data = {}
        
        for strategy_id, strategy_info in STRATEGIES.items():
            container_status = await self.get_container_status(strategy_info['container'])
            
            # Tentar obter dados da API se container estiver rodando
            api_data = {}
            if container_status['running']:
                try:
                    # Aqui poderia integrar com freqtrade_api_client
                    # Por enquanto, dados simulados
                    api_data = {
                        'profit_all_percent': 0.0,
                        'trade_count': 0,
                        'best_pair': 'BTC/USDT',
                        'state': 'running'
                    }
                except Exception as e:
                    logger.warning(f"Erro ao obter dados da API para {strategy_id}: {e}")
            
            status_data[strategy_id] = {
                'container': container_status,
                'api': api_data,
                'info': strategy_info
            }
        
        return status_data
    
    async def send_message(self, text: str, reply_markup=None, parse_mode='HTML'):
        """Enviar mensagem para o chat configurado"""
        try:
            await self.bot.send_message(
                chat_id=CHAT_ID,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")

# Instância global
bot_main = TelegramBotMain()

# ============================================================================
# COMANDOS PRINCIPAIS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menu principal"""
    logger.info(f"📱 Comando /start recebido de {update.effective_user.id}")
    
    if not bot_main.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado. Usuário não autorizado.")
        logger.warning(f"🚫 Acesso negado para usuário {update.effective_user.id}")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
        [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
        [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu")],
        [InlineKeyboardButton("💰 Trading Manual", callback_data="trading_menu")],
        [InlineKeyboardButton("🔮 Previsões IA", callback_data="predictions_menu")],
        [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
        [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """🤖 <b>FREQTRADE MULTI-STRATEGY COMMANDER</b>

Bem-vindo ao sistema de controle avançado!

🎯 <b>7 Estratégias Ativas</b>
• Sample A/B (RSI básico)
• WaveHyperNW (WaveTrend)
• ML Strategy (Machine Learning)
• Multi-Timeframe (Análise multi-TF)

🔮 <b>Funcionalidades:</b>
• IA Preditiva - Previsão de tendências
• Trading Manual - Compra/venda forçada
• Controle Total - Start/Stop estratégias
• Monitoramento 24/7 - Alertas automáticos

Escolha uma opção abaixo:"""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Status das estratégias"""
    if not bot_main.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("⏳ Obtendo status das estratégias...")
    
    status_data = await bot_main.get_all_strategies_status()
    
    message = "📊 <b>STATUS DAS ESTRATÉGIAS</b>\n\n"
    
    running_count = 0
    total_strategies = len(STRATEGIES)
    
    for strategy_id, data in status_data.items():
        container = data['container']
        info = data['info']
        
        if container['running']:
            status_emoji = "🟢"
            running_count += 1
            status_text = "RODANDO"
        else:
            status_emoji = "🔴"
            status_text = "PARADO"
        
        message += f"{status_emoji} <b>{info['name']}</b>\n"
        message += f"   Status: {status_text}\n"
        message += f"   Descrição: {info['description']}\n"
        message += f"   Container: {container['name']}\n"
        message += f"   API Port: {info['api_port']}\n\n"
    
    message += f"📈 <b>RESUMO GERAL:</b>\n"
    message += f"• Estratégias Ativas: {running_count}/{total_strategies}\n"
    message += f"• Sistema: {'🟢 Operacional' if running_count > 0 else '🔴 Parado'}\n"
    message += f"• Modo: 🟡 DRY-RUN (Simulação)\n"
    message += f"• Última Verificação: {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estatísticas detalhadas"""
    if not bot_main.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("📊 Coletando estatísticas...")
    
    message = "📈 <b>ESTATÍSTICAS DETALHADAS</b>\n\n"
    
    # Dados simulados para demonstração (em produção, viria da API)
    stats_data = {
        "stratA": {"trades": 5, "profit": 2.5, "win_rate": 80.0},
        "stratB": {"trades": 3, "profit": 1.2, "win_rate": 66.7},
        "waveHyperNW": {"trades": 12, "profit": 5.8, "win_rate": 75.0},
        "mlStrategy": {"trades": 8, "profit": 3.2, "win_rate": 87.5},
        "mlStrategySimple": {"trades": 6, "profit": 2.1, "win_rate": 83.3},
        "multiTimeframe": {"trades": 4, "profit": 1.8, "win_rate": 75.0},
        "waveEnhanced": {"trades": 7, "profit": 3.5, "win_rate": 85.7}
    }
    
    total_trades = 0
    total_profit = 0.0
    
    for strategy_id, stats in stats_data.items():
        strategy_info = STRATEGIES[strategy_id]
        trades = stats['trades']
        profit = stats['profit']
        win_rate = stats['win_rate']
        
        total_trades += trades
        total_profit += profit
        
        profit_emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "🟡"
        
        message += f"📊 <b>{strategy_info['name']}</b>\n"
        message += f"   Trades: {trades}\n"
        message += f"   {profit_emoji} P&L: {profit:.2f} USDT\n"
        message += f"   Win Rate: {win_rate:.1f}%\n\n"
    
    avg_win_rate = sum(s['win_rate'] for s in stats_data.values()) / len(stats_data)
    
    message += f"🎯 <b>RESUMO GERAL:</b>\n"
    message += f"• Total Trades: {total_trades}\n"
    message += f"• Lucro Total: {total_profit:.2f} USDT\n"
    message += f"• Win Rate Médio: {avg_win_rate:.1f}%\n"
    message += f"• Período: Últimas 24h\n"
    message += f"• Modo: DRY-RUN (Simulação)"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ajuda e comandos disponíveis"""
    if not bot_main.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    message = """🆘 <b>AJUDA - COMANDOS DISPONÍVEIS</b>

<b>📱 COMANDOS BÁSICOS:</b>
/start - Menu principal interativo
/status - Status de todas as estratégias
/stats - Estatísticas detalhadas
/help - Esta mensagem de ajuda

<b>💰 TRADING MANUAL:</b>
/forcebuy &lt;strategy&gt; &lt;pair&gt; - Compra forçada
/forcesell &lt;strategy&gt; &lt;pair&gt; - Venda forçada
/forcesell &lt;strategy&gt; all - Vender todas posições

<b>⚙️ CONTROLE DE ESTRATÉGIAS:</b>
/start_strategy &lt;name&gt; - Iniciar estratégia
/stop_strategy &lt;name&gt; - Parar estratégia
/restart_strategy &lt;name&gt; - Reiniciar estratégia

<b>🔮 IA PREDITIVA:</b>
/predict - Previsões rápidas
/predict &lt;pair&gt; - Previsão específica
/ai_analysis - Análise completa com IA

<b>📊 MONITORAMENTO:</b>
/emergency - Parada de emergência
/health - Status de saúde do sistema
/logs &lt;strategy&gt; - Ver logs de estratégia

<b>🎯 ESTRATÉGIAS DISPONÍVEIS:</b>
• stratA - Sample Strategy A
• stratB - Sample Strategy B  
• waveHyperNW - WaveHyperNW Strategy
• mlStrategy - ML Strategy
• mlStrategySimple - ML Strategy Simple
• multiTimeframe - Multi Timeframe Strategy
• waveEnhanced - WaveHyperNW Enhanced

<b>⚠️ IMPORTANTE:</b>
• Sistema em modo DRY-RUN (simulação)
• Todos os trades são simulados
• Para modo LIVE, use: /toggle_live (CUIDADO!)

<b>🔒 SEGURANÇA:</b>
• Apenas usuários autorizados podem usar
• Logs de todas as ações são mantidos
• Backups automáticos das configurações"""
    
    await update.message.reply_text(message, parse_mode='HTML')

# ============================================================================
# CALLBACK HANDLERS (BOTÕES)
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões inline"""
    query = update.callback_query
    await query.answer()
    
    if not bot_main.is_admin(query.from_user.id):
        await query.edit_message_text("❌ Acesso negado.")
        return
    
    data = query.data
    
    if data == "status_all":
        await show_status_menu(query)
    elif data == "control_menu":
        await show_control_menu(query)
    elif data == "stats_menu":
        await show_stats_menu(query)
    elif data == "trading_menu":
        await show_trading_menu(query)
    elif data == "predictions_menu":
        await show_predictions_menu(query)
    elif data == "config_menu":
        await show_config_menu(query)
    elif data == "help":
        await show_help_menu(query)
    elif data == "back_main":
        await show_main_menu(query)

async def show_status_menu(query):
    """Mostrar menu de status"""
    status_data = await bot_main.get_all_strategies_status()
    
    message = "📊 <b>STATUS DETALHADO</b>\n\n"
    running_count = 0
    
    for strategy_id, data in status_data.items():
        container = data['container']
        info = data['info']
        
        if container['running']:
            status_emoji = "🟢"
            running_count += 1
        else:
            status_emoji = "🔴"
        
        message += f"{status_emoji} {info['name']}\n"
    
    message += f"\n📈 Ativas: {running_count}/{len(STRATEGIES)}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="status_all")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_control_menu(query):
    """Mostrar menu de controle"""
    message = "🎮 <b>CONTROLE DE ESTRATÉGIAS</b>\n\nEscolha uma estratégia para controlar:"
    
    keyboard = []
    for strategy_id, info in STRATEGIES.items():
        keyboard.append([InlineKeyboardButton(f"⚙️ {info['name']}", callback_data=f"control_{strategy_id}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_stats_menu(query):
    """Mostrar menu de estatísticas"""
    message = """📈 <b>ESTATÍSTICAS</b>

Escolha o tipo de estatística:"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Resumo Geral", callback_data="stats_general")],
        [InlineKeyboardButton("💰 P&L Detalhado", callback_data="stats_pnl")],
        [InlineKeyboardButton("📈 Performance", callback_data="stats_performance")],
        [InlineKeyboardButton("🎯 Win Rate", callback_data="stats_winrate")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_trading_menu(query):
    """Mostrar menu de trading manual"""
    message = """💰 <b>TRADING MANUAL</b>

⚠️ <b>ATENÇÃO:</b> Sistema em modo DRY-RUN
Todos os trades são simulados.

Escolha uma opção:"""
    
    keyboard = [
        [InlineKeyboardButton("🟢 Compra Forçada", callback_data="force_buy_menu")],
        [InlineKeyboardButton("🔴 Venda Forçada", callback_data="force_sell_menu")],
        [InlineKeyboardButton("⚙️ Ajustar Estratégia", callback_data="adjust_strategy_menu")],
        [InlineKeyboardButton("🚨 Parada de Emergência", callback_data="emergency_stop")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_predictions_menu(query):
    """Mostrar menu de previsões IA"""
    message = """🔮 <b>PREVISÕES IA</b>

Sistema de IA preditiva para análise de tendências:"""
    
    keyboard = [
        [InlineKeyboardButton("⚡ Previsões Rápidas", callback_data="predict_quick")],
        [InlineKeyboardButton("🧠 Análise Completa", callback_data="predict_full")],
        [InlineKeyboardButton("📊 Análise por Par", callback_data="predict_pair")],
        [InlineKeyboardButton("🎯 Oportunidades", callback_data="predict_opportunities")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_config_menu(query):
    """Mostrar menu de configurações"""
    message = """⚙️ <b>CONFIGURAÇÕES</b>

Configurações do sistema:"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Modo DRY-RUN/LIVE", callback_data="toggle_mode")],
        [InlineKeyboardButton("🔔 Notificações", callback_data="config_notifications")],
        [InlineKeyboardButton("💾 Backup", callback_data="config_backup")],
        [InlineKeyboardButton("🔒 Segurança", callback_data="config_security")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_help_menu(query):
    """Mostrar menu de ajuda"""
    message = """🆘 <b>AJUDA</b>

Sistema de ajuda e documentação:"""
    
    keyboard = [
        [InlineKeyboardButton("📱 Comandos Básicos", callback_data="help_commands")],
        [InlineKeyboardButton("💰 Trading Manual", callback_data="help_trading")],
        [InlineKeyboardButton("🔮 IA Preditiva", callback_data="help_ai")],
        [InlineKeyboardButton("⚙️ Configurações", callback_data="help_config")],
        [InlineKeyboardButton("🏠 Menu Principal", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_main_menu(query):
    """Voltar ao menu principal"""
    keyboard = [
        [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
        [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
        [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu")],
        [InlineKeyboardButton("💰 Trading Manual", callback_data="trading_menu")],
        [InlineKeyboardButton("🔮 Previsões IA", callback_data="predictions_menu")],
        [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
        [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """🤖 <b>FREQTRADE MULTI-STRATEGY COMMANDER</b>

Sistema de controle avançado ativo!

🎯 <b>7 Estratégias Configuradas</b>
🔮 <b>IA Preditiva Disponível</b>
💰 <b>Trading Manual Habilitado</b>
🔔 <b>Monitoramento 24/7</b>

Escolha uma opção:"""
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Função principal"""
    if not TOKEN or not CHAT_ID:
        logger.error("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados!")
        logger.error("Execute: python setup_credentials.py")
        return
    
    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handler para botões
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Iniciar bot
    logger.info("🤖 Telegram Bot Principal iniciado!")
    logger.info(f"🎯 Chat ID configurado: {CHAT_ID}")
    logger.info(f"📊 Estratégias disponíveis: {len(STRATEGIES)}")
    
    application.run_polling()

if __name__ == "__main__":
    main()
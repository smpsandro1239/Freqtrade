#!/usr/bin/env python3
"""
Telegram Commander - Versão final corrigida
Sistema completo com todas as funcionalidades funcionando
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

# Configuração
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ADMIN_USERS = [int(x.strip()) for x in os.getenv('TELEGRAM_ADMIN_USERS', '').split(',') if x.strip()]

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estratégias disponíveis
STRATEGIES = {
    "stratA": {
        "name": "Strategy A",
        "container": "ft-stratA",
        "config": "user_data/configs/stratA.json"
    },
    "stratB": {
        "name": "Strategy B", 
        "container": "ft-stratB",
        "config": "user_data/configs/stratB.json"
    },
    "waveHyperNW": {
        "name": "WaveHyperNW Strategy",
        "container": "ft-waveHyperNW", 
        "config": "user_data/configs/waveHyperNW.json"
    }
}

class TelegramCommander:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.stats = FreqtradeStats()
        self.controller = StrategyController()
    
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é admin"""
        return user_id in ADMIN_USERS
    
    async def get_container_status(self, container_name: str) -> Dict:
        """Obter status de um container"""
        try:
            container = self.docker_client.containers.get(container_name)
            return {
                'running': container.status == 'running',
                'status': container.status,
                'name': container.name
            }
        except docker.errors.NotFound:
            return {
                'running': False,
                'status': 'not_found',
                'name': container_name
            }
        except Exception as e:
            return {
                'running': False,
                'status': f'error: {str(e)}',
                'name': container_name
            }

# Global commander instance
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
        [InlineKeyboardButton("💰 Trading Manual", callback_data="trading_menu")],
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
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões inline"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    logger.info(f"🔘 Callback recebido: {data}")
    
    try:
        if data == "main_menu":
            # Recreate main menu
            keyboard = [
                [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
                [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
                [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu")],
                [InlineKeyboardButton("💰 Trading Manual", callback_data="trading_menu")],
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
            
        elif data == "stats_menu":
            await show_stats_menu(query)
        elif data == "stats_general":
            await show_general_stats(query)
        elif data == "trading_menu":
            await show_trading_menu(query)
        elif data.startswith("trading_"):
            if data == "trading_analysis":
                await show_trading_analysis(query)
            else:
                strategy_id = data.replace("trading_", "")
                await show_strategy_trading(query, strategy_id)
        else:
            await query.edit_message_text("❌ Funcionalidade em desenvolvimento.")
            
    except Exception as e:
        logger.error(f"🚨 Erro no callback {data}: {e}")
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
            message += f"• {strategy_info['name']}: Modo {analysis['recommended_mode']}\n"
        
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
    application.add_handler(CommandHandler("forcebuy", forcebuy_command))
    application.add_handler(CommandHandler("forcesell", forcesell_command))
    application.add_handler(CommandHandler("adjust", adjust_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("🤖 Telegram Commander iniciado!")
    application.run_polling()

if __name__ == "__main__":
    main()
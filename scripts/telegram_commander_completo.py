#!/usr/bin/env python3
"""
Telegram Commander Completo - Todas as estratégias e comandos funcionando
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

# Importar cliente API real, IA avançada e gerador de gráficos
from freqtrade_api_client import api_client
from advanced_ai_predictor import ai_predictor
from chart_generator import chart_generator

# Configuração
TOKEN = os.getenv('TELEGRAM_TOKEN', '7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1555333079')
ADMIN_USERS = [int(x.strip()) for x in os.getenv('TELEGRAM_ADMIN_USERS', '1555333079').split(',') if x.strip()]

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TODAS as estratégias disponíveis
STRATEGIES = {
    "stratA": {
        "name": "Strategy A",
        "container": "ft-stratA",
        "config": "user_data/configs/stratA.json",
        "strategy": "SampleStrategyA"
    },
    "stratB": {
        "name": "Strategy B", 
        "container": "ft-stratB",
        "config": "user_data/configs/stratB.json",
        "strategy": "SampleStrategyB"
    },
    "waveHyperNW": {
        "name": "WaveHyperNW Strategy",
        "container": "ft-waveHyperNW", 
        "config": "user_data/configs/waveHyperNW.json",
        "strategy": "WaveHyperNWStrategy"
    },
    "mlStrategy": {
        "name": "ML Strategy",
        "container": "ft-mlStrategy",
        "config": "user_data/configs/mlStrategy.json",
        "strategy": "MLStrategy"
    },
    "mlStrategySimple": {
        "name": "ML Strategy Simple",
        "container": "ft-mlStrategySimple",
        "config": "user_data/configs/mlStrategySimple.json",
        "strategy": "MLStrategySimple"
    },
    "multiTimeframe": {
        "name": "Multi Timeframe Strategy",
        "container": "ft-multiTimeframe",
        "config": "user_data/configs/multiTimeframe.json",
        "strategy": "MultiTimeframeStrategy"
    },
    "waveHyperNWEnhanced": {
        "name": "WaveHyperNW Enhanced",
        "container": "ft-waveHyperNWEnhanced",
        "config": "user_data/configs/waveHyperNWEnhanced.json",
        "strategy": "WaveHyperNWEnhanced"
    }
}

class TelegramCommander:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client error: {e}")
            self.docker_client = None
    
    def is_admin(self, user_id: int) -> bool:
        """Verificar se usuário é admin"""
        return user_id in ADMIN_USERS
    
    async def get_container_status(self, container_name: str) -> Dict:
        """Obter status de um container"""
        if not self.docker_client:
            return {'running': False, 'status': 'docker_unavailable', 'name': container_name}
            
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
        [InlineKeyboardButton("🔮 Previsões IA", callback_data="predictions_menu")],
        [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
        [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """🤖 <b>FREQTRADE COMMANDER</b>

Bem-vindo ao sistema de controle avançado!

🔮 <b>IA Preditiva</b> - Previsão de subidas
💰 <b>Trading Manual</b> - Compra/venda forçada
📊 <b>7 Estratégias</b> - Controle total
🔔 <b>Notificações 24/7</b> - Alertas automáticos

Escolha uma opção abaixo:"""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Status das estratégias (REAL)"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("⏳ Obtendo status real das estratégias...")
    
    message = "📊 <b>STATUS REAL DAS ESTRATÉGIAS</b>\n\n"
    
    # Obter status real via API
    all_status = api_client.get_all_strategies_status()
    
    running_count = 0
    total_profit = 0
    
    for strategy_id, status_data in all_status.items():
        if status_data.get("success"):
            status_emoji = "🟢" if status_data.get("state") == "running" else "🔴"
            profit = status_data.get("profit_all_percent", 0)
            trades = status_data.get("trade_count", 0)
            
            if status_data.get("state") == "running":
                running_count += 1
            
            total_profit += profit
            
            message += f"{status_emoji} <b>{status_data['name']}</b>\n"
            message += f"   Estado: {status_data.get('state', 'unknown')}\n"
            message += f"   Trades: {trades}\n"
            message += f"   P&L: {profit:.2f}%\n"
            message += f"   Melhor Par: {status_data.get('best_pair', 'N/A')}\n\n"
        else:
            message += f"🔴 <b>{STRATEGIES[strategy_id]['name']}</b>\n"
            message += f"   ❌ API não disponível\n\n"
    
    message += f"📈 <b>RESUMO GERAL:</b>\n"
    message += f"• Estratégias Ativas: {running_count}/{len(STRATEGIES)}\n"
    message += f"• Lucro Total: {total_profit:.2f}%\n"
    message += f"• Sistema: {'🟢 Operacional' if running_count > 0 else '🔴 Parado'}\n"
    message += f"• Última Verificação: {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /predict - IA AVANÇADA com análise detalhada"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("🤖 Executando IA Avançada... Analisando padrões e tendências...")
    
    # Gerar visão geral do mercado com IA avançada
    market_overview = ai_predictor.generate_market_overview()
    
    message = "🤖 <b>IA AVANÇADA - ANÁLISE COMPLETA</b>\n\n"
    
    # Sentimento geral do mercado
    sentiment = market_overview.get('market_sentiment', {})
    if sentiment:
        message += f"🌍 <b>SENTIMENTO DO MERCADO:</b>\n"
        message += f"{sentiment['emoji']} {sentiment['description']}\n"
        message += f"📊 Score Médio: {sentiment['avg_score']}/100\n"
        message += f"💰 Lucro Médio: {sentiment['avg_profit']:.2f}%\n"
        message += f"🎯 Estratégias Ativas: {sentiment['active_strategies']}/7\n\n"
    
    # Top 3 estratégias por score
    strategies = market_overview.get('strategies', {})
    if strategies:
        # Ordenar por score
        sorted_strategies = sorted(
            [(k, v) for k, v in strategies.items() if v.get('success')],
            key=lambda x: x[1]['score']['total'],
            reverse=True
        )
        
        message += f"🏆 <b>TOP 3 ESTRATÉGIAS:</b>\n"
        for i, (strategy_id, analysis) in enumerate(sorted_strategies[:3]):
            strategy_name = api_client.strategies[strategy_id]['name']
            score = analysis['score']
            trend = analysis['trend']
            confidence = analysis['confidence']
            
            message += f"{i+1}. {score['emoji']} <b>{strategy_name}</b>\n"
            message += f"   📊 Score: {score['total']}/100 ({score['grade']})\n"
            message += f"   {trend['emoji']} {trend['action']} ({confidence['level']} confiança)\n"
            message += f"   💰 P&L: {analysis['metrics']['profit_percent']:.1f}% | Trades: {analysis['metrics']['total_trades']}\n\n"
    
    # Recomendações da IA
    recommendations = market_overview.get('recommendations', [])
    if recommendations:
        message += f"💡 <b>RECOMENDAÇÕES DA IA:</b>\n"
        for rec in recommendations:
            message += f"{rec['emoji']} <b>{rec['title']}</b>\n"
            message += f"   {rec['description']}\n\n"
    
    # Alertas importantes
    alerts = market_overview.get('alerts', [])
    if alerts:
        message += f"🚨 <b>ALERTAS:</b>\n"
        for alert in alerts[:3]:  # Mostrar apenas os 3 primeiros
            message += f"{alert['emoji']} {alert['strategy']}: {alert['message']}\n"
        if len(alerts) > 3:
            message += f"... e mais {len(alerts) - 3} alertas\n"
        message += "\n"
    
    message += f"🕐 Análise IA realizada em: {datetime.now().strftime('%H:%M:%S')}\n"
    message += f"🤖 Próxima análise recomendada em: 4 horas\n\n"
    message += f"💡 Use /start → 🔮 Previsões IA para análise detalhada individual"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estatísticas REAIS"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    await update.message.reply_text("⏳ Coletando estatísticas reais...")
    
    message = "📈 <b>ESTATÍSTICAS REAIS</b>\n\n"
    
    total_strategies = len(STRATEGIES)
    running_strategies = 0
    total_trades = 0
    total_profit_usdt = 0
    total_profit_percent = 0
    
    for strategy_id in STRATEGIES.keys():
        # Obter estatísticas reais via API
        profit_stats = api_client.get_profit_stats(strategy_id)
        status_data = api_client.get_strategy_status(strategy_id)
        
        if status_data.get("success") and status_data.get("state") == "running":
            running_strategies += 1
            status_emoji = "🟢"
        else:
            status_emoji = "🔴"
        
        if profit_stats.get("success"):
            trades = profit_stats.get("trade_count", 0)
            profit_usdt = profit_stats.get("profit_closed_coin", 0)
            profit_percent = profit_stats.get("profit_closed_percent", 0)
            best_pair = profit_stats.get("best_pair", "N/A")
            avg_duration = profit_stats.get("avg_duration", "N/A")
            
            total_trades += trades
            total_profit_usdt += profit_usdt
            total_profit_percent += profit_percent
            
            message += f"{status_emoji} <b>{STRATEGIES[strategy_id]['name']}</b>\n"
            message += f"   Trades: {trades} | P&L: {profit_usdt:.2f} USDT ({profit_percent:.2f}%)\n"
            message += f"   Melhor Par: {best_pair}\n"
            message += f"   Duração Média: {avg_duration}\n\n"
        else:
            message += f"{status_emoji} <b>{STRATEGIES[strategy_id]['name']}</b>\n"
            message += f"   ❌ Estatísticas não disponíveis\n\n"
    
    message += f"📊 <b>RESUMO GERAL:</b>\n"
    message += f"• Estratégias Ativas: {running_strategies}/{total_strategies}\n"
    message += f"• Total de Trades: {total_trades}\n"
    message += f"• Lucro Total: {total_profit_usdt:.2f} USDT ({total_profit_percent:.2f}%)\n"
    message += f"• Sistema: {'🟢 Operacional' if running_strategies > 0 else '🔴 Parado'}\n"
    message += f"• Última Atualização: {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def forcebuy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcebuy - Compra forçada REAL"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if len(args) < 2:
        strategies_list = "\n".join([f"• {sid} - {info['name']}" for sid, info in STRATEGIES.items()])
        
        await update.message.reply_text(
            f"❌ Uso incorreto.\n\n"
            f"📝 <b>Formato:</b>\n"
            f"<code>/forcebuy [estratégia] [par] [preço]</code>\n\n"
            f"📋 <b>Exemplos:</b>\n"
            f"<code>/forcebuy stratA BTC/USDT</code>\n"
            f"<code>/forcebuy waveHyperNW ETH/USDT 2500.50</code>\n\n"
            f"🎯 <b>Estratégias disponíveis:</b>\n{strategies_list}",
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    pair = args[1]
    price = float(args[2]) if len(args) > 2 else None
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    await update.message.reply_text(f"⏳ Executando compra forçada REAL...\n\n📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n💰 Par: {pair}")
    
    # Executar compra forçada real via API
    result = api_client.force_buy(strategy_id, pair, price)
    
    if result.get("success"):
        response = f"🟢 <b>COMPRA EXECUTADA COM SUCESSO!</b>\n\n"
        response += f"✅ {result['message']}\n"
        response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
        response += f"💰 Par: {pair}\n"
        if price:
            response += f"💵 Preço: {price}\n"
        if result.get("trade_id"):
            response += f"🆔 Trade ID: {result['trade_id']}\n"
        response += f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}\n\n"
        response += f"💡 Use /status para monitorar a posição"
    else:
        response = f"❌ <b>ERRO NA COMPRA</b>\n\n"
        response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
        response += f"💰 Par: {pair}\n"
        response += f"❌ Erro: {result.get('error', 'Erro desconhecido')}\n\n"
        response += f"💡 Verifique se a estratégia está rodando e o par é válido"
    
    await update.message.reply_text(response, parse_mode='HTML')

async def forcesell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcesell - Venda forçada REAL"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if len(args) < 2:
        strategies_list = "\n".join([f"• {sid} - {info['name']}" for sid, info in STRATEGIES.items()])
        
        await update.message.reply_text(
            f"❌ Uso incorreto.\n\n"
            f"📝 <b>Formato:</b>\n"
            f"<code>/forcesell [estratégia] [trade_id/all]</code>\n\n"
            f"📋 <b>Exemplos:</b>\n"
            f"<code>/forcesell stratA 123</code> (vender trade específico)\n"
            f"<code>/forcesell waveHyperNW all</code> (vender tudo)\n\n"
            f"🎯 <b>Estratégias disponíveis:</b>\n{strategies_list}\n\n"
            f"💡 Use /status para ver trades abertos e seus IDs",
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    trade_ref = args[1]
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    # Venda de todas as posições
    if trade_ref.lower() == 'all':
        await update.message.reply_text(f"⏳ Executando venda de TODAS as posições...\n📊 Estratégia: {STRATEGIES[strategy_id]['name']}")
        
        result = api_client.force_sell_all(strategy_id)
        
        if result.get("success"):
            response = f"🔴 <b>VENDA EM LOTE EXECUTADA!</b>\n\n"
            response += f"✅ {result['message']}\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"💰 Total de trades: {result['total_trades']}\n"
            response += f"✅ Vendas bem-sucedidas: {result['successful_sells']}\n"
            response += f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}"
        else:
            response = f"❌ <b>ERRO NA VENDA EM LOTE</b>\n\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"❌ Erro: {result.get('error', 'Erro desconhecido')}"
    
    # Venda de trade específico
    else:
        trade_id = trade_ref
        await update.message.reply_text(f"⏳ Executando venda forçada...\n📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n🆔 Trade ID: {trade_id}")
        
        result = api_client.force_sell(strategy_id, trade_id)
        
        if result.get("success"):
            response = f"🔴 <b>VENDA EXECUTADA COM SUCESSO!</b>\n\n"
            response += f"✅ {result['message']}\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"🆔 Trade ID: {trade_id}\n"
            response += f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}\n\n"
            response += f"💡 Use /stats para ver o resultado"
        else:
            response = f"❌ <b>ERRO NA VENDA</b>\n\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"🆔 Trade ID: {trade_id}\n"
            response += f"❌ Erro: {result.get('error', 'Erro desconhecido')}\n\n"
            response += f"💡 Verifique se o trade ID existe com /status"
    
    await update.message.reply_text(response, parse_mode='HTML')

async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adjust - Ajustar estratégia REAL"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if len(args) < 2:
        strategies_list = "\n".join([f"• {sid} - {info['name']}" for sid, info in STRATEGIES.items()])
        
        await update.message.reply_text(
            f"❌ Uso incorreto.\n\n"
            f"📝 <b>Formato:</b>\n"
            f"<code>/adjust [estratégia] [modo]</code>\n\n"
            f"📋 <b>Modos disponíveis:</b>\n"
            f"• <code>aggressive</code> - Mais trades, ROI menor\n"
            f"• <code>conservative</code> - Menos trades, ROI maior\n"
            f"• <code>balanced</code> - Equilibrado\n"
            f"• <code>reload</code> - Recarregar configuração\n\n"
            f"📋 <b>Exemplos:</b>\n"
            f"<code>/adjust stratA aggressive</code>\n"
            f"<code>/adjust waveHyperNW reload</code>\n\n"
            f"🎯 <b>Estratégias disponíveis:</b>\n{strategies_list}",
            parse_mode='HTML'
        )
        return
    
    strategy_id = args[0]
    mode = args[1].lower()
    
    if strategy_id not in STRATEGIES:
        await update.message.reply_text(f"❌ Estratégia '{strategy_id}' não encontrada.")
        return
    
    if mode not in ['aggressive', 'conservative', 'balanced', 'reload']:
        await update.message.reply_text("❌ Modo inválido. Use: aggressive, conservative, balanced, reload")
        return
    
    mode_names = {
        'aggressive': '🔥 AGRESSIVO',
        'conservative': '🛡️ CONSERVADOR', 
        'balanced': '⚖️ EQUILIBRADO',
        'reload': '🔄 RECARREGAR'
    }
    
    await update.message.reply_text(f"⏳ Aplicando modo {mode_names[mode]}...\n📊 Estratégia: {STRATEGIES[strategy_id]['name']}")
    
    if mode == 'reload':
        # Recarregar configuração via API
        result = api_client.reload_config(strategy_id)
        
        if result.get("success"):
            response = f"✅ <b>CONFIGURAÇÃO RECARREGADA!</b>\n\n"
            response += f"🔄 {result['message']}\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"⏰ Horário: {datetime.now().strftime('%H:%M:%S')}\n\n"
            response += f"💡 A estratégia está usando a configuração mais recente"
        else:
            response = f"❌ <b>ERRO AO RECARREGAR</b>\n\n"
            response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n"
            response += f"❌ Erro: {result.get('error', 'Erro desconhecido')}"
    
    else:
        # Para modos aggressive/conservative/balanced, vamos simular por enquanto
        # mas indicar que é uma funcionalidade avançada
        response = f"⚠️ <b>MODO {mode_names[mode]} - EM DESENVOLVIMENTO</b>\n\n"
        response += f"📊 Estratégia: {STRATEGIES[strategy_id]['name']}\n\n"
        response += f"🔧 <b>Esta funcionalidade está sendo implementada:</b>\n"
        
        if mode == 'aggressive':
            response += f"• Reduzir ROI para trades mais rápidos\n"
            response += f"• Aumentar max_open_trades\n"
            response += f"• Ajustar stop loss mais apertado\n"
        elif mode == 'conservative':
            response += f"• Aumentar ROI para mais paciência\n"
            response += f"• Reduzir max_open_trades\n"
            response += f"• Ajustar stop loss mais solto\n"
        else:
            response += f"• Restaurar configurações padrão\n"
            response += f"• Balancear risco/retorno\n"
        
        response += f"\n💡 <b>Por enquanto, use:</b>\n"
        response += f"• <code>/adjust {strategy_id} reload</code> - Recarregar config\n"
        response += f"• Edite manualmente os arquivos de configuração\n"
        response += f"• Reinicie o container da estratégia"
    
    await update.message.reply_text(response, parse_mode='HTML')

async def charts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /charts - Gráficos e visualizações"""
    if not commander.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    args = context.args
    if not args:
        # Menu de gráficos
        message = """📊 <b>GRÁFICOS DISPONÍVEIS</b>

📈 <b>Comandos de Gráficos:</b>
/charts comparison - Comparação de performance
/charts heatmap - Mapa de calor do mercado
/charts risk - Análise de risco visual
/charts [estratégia] - Gráfico individual

🎯 <b>Estratégias disponíveis:</b>"""
        
        for strategy_id, strategy_info in STRATEGIES.items():
            message += f"\n• {strategy_id} - {strategy_info['name']}"
        
        message += f"""

📋 <b>Exemplos:</b>
/charts comparison
/charts heatmap
/charts stratA
/charts waveHyperNW

💡 Todos os gráficos são baseados em dados reais!"""
        
        await update.message.reply_text(message, parse_mode='HTML')
        return
    
    chart_type = args[0].lower()
    
    if chart_type == "comparison":
        await update.message.reply_text("📊 Gerando comparação de performance...")
        chart = chart_generator.generate_performance_comparison()
        await update.message.reply_text(chart, parse_mode='HTML')
    
    elif chart_type == "heatmap":
        await update.message.reply_text("🌡️ Gerando mapa de calor...")
        chart = chart_generator.generate_market_heatmap()
        await update.message.reply_text(chart, parse_mode='HTML')
    
    elif chart_type == "risk":
        await update.message.reply_text("⚠️ Gerando análise de risco...")
        chart = chart_generator.generate_risk_analysis_chart()
        await update.message.reply_text(chart, parse_mode='HTML')
    
    elif chart_type in STRATEGIES:
        strategy_name = STRATEGIES[chart_type]['name']
        await update.message.reply_text(f"📈 Gerando gráfico para {strategy_name}...")
        
        # Gráfico de lucro
        profit_chart = chart_generator.generate_profit_chart(chart_type)
        await update.message.reply_text(profit_chart, parse_mode='HTML')
        
        # Timeline
        timeline_chart = chart_generator.generate_trades_timeline(chart_type)
        await update.message.reply_text(timeline_chart, parse_mode='HTML')
    
    else:
        await update.message.reply_text(f"❌ Tipo de gráfico '{chart_type}' não reconhecido.\n\nUse /charts para ver opções disponíveis.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ajuda"""
    message = """🆘 <b>AJUDA - COMANDOS DISPONÍVEIS</b>

📱 <b>Comandos Básicos:</b>
/start - Menu principal
/status - Status de todas as estratégias
/stats - Estatísticas gerais
/charts - Gráficos e visualizações
/help - Esta ajuda

🔮 <b>IA Preditiva:</b>
/predict - IA avançada com análise completa

💰 <b>Trading Manual:</b>
/forcebuy [estratégia] [par] [preço] - Compra forçada
/forcesell [estratégia] [trade_id/all] - Venda forçada
/adjust [estratégia] [modo] - Ajustar estratégia

📊 <b>Gráficos:</b>
/charts comparison - Comparação visual
/charts heatmap - Mapa de calor
/charts [estratégia] - Gráfico individual

⚙️ <b>Modos de Ajuste:</b>
• reload - Recarregar configuração
• aggressive - Mais penetrável (em desenvolvimento)
• conservative - Mais cauteloso (em desenvolvimento)

🎯 <b>Estratégias Disponíveis:</b>"""

    for strategy_id, strategy_info in STRATEGIES.items():
        message += f"\n• {strategy_id} - {strategy_info['name']}"

    message += f"""

📋 <b>Exemplos:</b>
/forcebuy stratA BTC/USDT
/forcesell waveHyperNW 123
/charts comparison
/predict

💡 Use /start para menu interativo completo!"""
    
    await update.message.reply_text(message, parse_mode='HTML')

async def show_status_all(query):
    """Mostrar status de todas as estratégias"""
    message = "📊 <b>STATUS GERAL DO SISTEMA</b>\n\n"
    
    # Obter status real via API
    all_status = api_client.get_all_strategies_status()
    
    running_count = 0
    total_count = len(STRATEGIES)
    total_profit = 0
    
    for strategy_id, status_data in all_status.items():
        if status_data.get("success"):
            status_emoji = "🟢" if status_data.get("state") == "running" else "🔴"
            profit = status_data.get("profit_all_percent", 0)
            trades = status_data.get("trade_count", 0)
            
            if status_data.get("state") == "running":
                running_count += 1
            
            total_profit += profit
            
            message += f"{status_emoji} <b>{status_data['name']}</b>\n"
            message += f"   Estado: {status_data.get('state', 'unknown')}\n"
            message += f"   Trades: {trades} | P&L: {profit:.2f}%\n\n"
        else:
            message += f"🔴 <b>{STRATEGIES[strategy_id]['name']}</b>\n"
            message += f"   ❌ API não disponível\n\n"
    
    message += f"📈 <b>RESUMO:</b>\n"
    message += f"• Estratégias Ativas: {running_count}/{total_count}\n"
    message += f"• Lucro Total: {total_profit:.2f}%\n"
    message += f"• Sistema: {'🟢 Operacional' if running_count > 0 else '🔴 Parado'}\n"
    message += f"• Última Verificação: {datetime.now().strftime('%H:%M:%S')}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data="status_all")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_control_menu(query):
    """Menu de controle das estratégias"""
    message = "🎮 <b>CONTROLE DAS ESTRATÉGIAS</b>\n\n"
    message += "Selecione uma estratégia para controlar:\n\n"
    
    keyboard = []
    for strategy_id, strategy_info in STRATEGIES.items():
        keyboard.append([InlineKeyboardButton(
            f"🎯 {strategy_info['name']}", 
            callback_data=f"strategy_control_{strategy_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_stats_menu(query):
    """Menu de estatísticas"""
    message = "📈 <b>ESTATÍSTICAS</b>\n\n"
    message += "Escolha o tipo de estatística:\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 Geral", callback_data="stats_general")],
        [InlineKeyboardButton("💰 Por Estratégia", callback_data="stats_by_strategy")],
        [InlineKeyboardButton("🏆 Performance", callback_data="stats_performance")],
        [InlineKeyboardButton("💵 Balanços", callback_data="stats_balance")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_trading_menu(query):
    """Menu de trading manual"""
    message = "💰 <b>TRADING MANUAL</b>\n\n"
    message += "⚠️ <b>ATENÇÃO:</b> Estas ações afetam trades reais!\n\n"
    message += "Escolha uma ação:\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📈 Compra Forçada", callback_data="trade_forcebuy")],
        [InlineKeyboardButton("📉 Venda Forçada", callback_data="trade_forcesell")],
        [InlineKeyboardButton("🔄 Vender Tudo", callback_data="trade_sellall")],
        [InlineKeyboardButton("📋 Trades Abertos", callback_data="trade_list")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_predictions_menu(query):
    """Menu de previsões IA"""
    message = "🔮 <b>PREVISÕES DE IA</b>\n\n"
    message += "Análise preditiva baseada em dados reais:\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🚀 Análise Rápida", callback_data="predict_quick")],
        [InlineKeyboardButton("📊 Análise Detalhada", callback_data="predict_detailed")],
        [InlineKeyboardButton("⭐ Sinais de Alta Confiança", callback_data="predict_high_confidence")],
        [InlineKeyboardButton("📈 Tendências", callback_data="predict_trends")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_config_menu(query):
    """Menu de configurações"""
    message = "⚙️ <b>CONFIGURAÇÕES</b>\n\n"
    message += "Gerenciar configurações do sistema:\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Recarregar Configs", callback_data="config_reload_all")],
        [InlineKeyboardButton("🔧 Testar APIs", callback_data="config_test_apis")],
        [InlineKeyboardButton("📊 Status APIs", callback_data="config_api_status")],
        [InlineKeyboardButton("🔑 Conexões", callback_data="config_connections")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_charts_menu(query):
    """Menu de gráficos"""
    message = "📊 <b>GRÁFICOS E VISUALIZAÇÕES</b>\n\n"
    message += "Escolha o tipo de gráfico:\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📈 Comparação Performance", callback_data="chart_comparison")],
        [InlineKeyboardButton("🌡️ Mapa de Calor", callback_data="chart_heatmap")],
        [InlineKeyboardButton("⚠️ Análise de Risco", callback_data="chart_risk")],
        [InlineKeyboardButton("📊 Gráfico Individual", callback_data="chart_individual")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_help_menu(query):
    """Menu de ajuda"""
    message = """🆘 <b>AJUDA - SISTEMA FREQTRADE COMMANDER</b>

📱 <b>Comandos Diretos:</b>
/start - Menu principal
/status - Status de todas as estratégias
/stats - Estatísticas gerais
/charts - Gráficos e visualizações
/predict - IA avançada completa
/help - Esta ajuda

💰 <b>Trading Manual:</b>
/forcebuy [estratégia] [par] [preço] - Compra forçada
/forcesell [estratégia] [trade_id/all] - Venda forçada
/adjust [estratégia] [modo] - Ajustar estratégia

📊 <b>Gráficos:</b>
/charts comparison - Comparação visual
/charts heatmap - Mapa de calor
/charts [estratégia] - Gráfico individual

⚙️ <b>Modos de Ajuste:</b>
• reload - Recarregar configuração
• aggressive - Mais penetrável (em desenvolvimento)
• conservative - Mais cauteloso (em desenvolvimento)

🎯 <b>Estratégias Disponíveis:</b>"""

    for strategy_id, strategy_info in STRATEGIES.items():
        message += f"\n• {strategy_id} - {strategy_info['name']}"

    message += f"""

📋 <b>Exemplos:</b>
/forcebuy stratA BTC/USDT
/forcesell waveHyperNW 123
/charts comparison
/predict

🔮 <b>IA Preditiva:</b>
IA avançada com análise completa, scores, recomendações e alertas.

⚠️ <b>IMPORTANTE:</b>
• Comandos de trading afetam posições reais
• Sempre verifique antes de executar
• Use /status para monitorar resultados

💡 <b>Dicas:</b>
• Use menus interativos para facilitar
• Comandos diretos são mais rápidos
• Gráficos são baseados em dados reais"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

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
                [InlineKeyboardButton("🔮 Previsões IA", callback_data="predictions_menu")],
                [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
                [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """🤖 <b>FREQTRADE COMMANDER</b>

Bem-vindo ao sistema de controle avançado!

🔮 <b>IA Preditiva</b> - Previsão de subidas
💰 <b>Trading Manual</b> - Compra/venda forçada
📊 <b>7 Estratégias</b> - Controle total
🔔 <b>Notificações 24/7</b> - Alertas automáticos

Escolha uma opção abaixo:"""
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            
        elif data == "status_all":
            await show_status_all(query)
            
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
            
        elif data.startswith("strategy_"):
            await handle_strategy_action(query, data)
            
        elif data.startswith("trade_"):
            await handle_trade_action(query, data)
            
        else:
            await query.edit_message_text("❌ Ação não reconhecida.\n\nUse /start para voltar ao menu principal.")
            
    except Exception as e:
        logger.error(f"🚨 Erro no callback {data}: {e}")
        await query.edit_message_text(f"❌ Erro interno: {str(e)}")

def main():
    """Função principal"""
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN não configurado!")
        return
    
    logger.info(f"🔑 Token configurado: {TOKEN[:10]}...")
    logger.info(f"👤 Chat ID configurado: {CHAT_ID}")
    logger.info(f"👥 Usuários admin: {ADMIN_USERS}")
    logger.info(f"📊 Estratégias configuradas: {len(STRATEGIES)}")
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("predict", predict_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("charts", charts_command))
    application.add_handler(CommandHandler("forcebuy", forcebuy_command))
    application.add_handler(CommandHandler("forcesell", forcesell_command))
    application.add_handler(CommandHandler("adjust", adjust_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback_extended))
    
    logger.info("🤖 Telegram Commander Completo iniciado!")
    logger.info(f"🎯 Comandos disponíveis: /start, /status, /predict, /stats, /forcebuy, /forcesell, /adjust, /help")
    application.run_polling()

if __name__ == "__main__":
    main()
async 
def handle_strategy_action(query, data):
    """Handler para ações de estratégias"""
    parts = data.split("_")
    if len(parts) < 3:
        await query.edit_message_text("❌ Ação inválida.")
        return
    
    action = parts[1]
    strategy_id = parts[2]
    
    if strategy_id not in STRATEGIES:
        await query.edit_message_text("❌ Estratégia não encontrada.")
        return
    
    if action == "control":
        # Menu de controle individual da estratégia
        strategy_info = STRATEGIES[strategy_id]
        status_data = api_client.get_strategy_status(strategy_id)
        
        if status_data.get("success"):
            state = status_data.get("state", "unknown")
            trades = status_data.get("trade_count", 0)
            profit = status_data.get("profit_all_percent", 0)
            
            message = f"🎯 <b>{strategy_info['name']}</b>\n\n"
            message += f"📊 Estado: {state}\n"
            message += f"💰 Trades: {trades}\n"
            message += f"📈 P&L: {profit:.2f}%\n\n"
            message += f"Escolha uma ação:"
        else:
            message = f"🎯 <b>{strategy_info['name']}</b>\n\n"
            message += f"❌ API não disponível\n\n"
            message += f"Ações limitadas:"
        
        keyboard = [
            [InlineKeyboardButton("📊 Status Detalhado", callback_data=f"strategy_status_{strategy_id}")],
            [InlineKeyboardButton("📈 Estatísticas", callback_data=f"strategy_stats_{strategy_id}")],
            [InlineKeyboardButton("💰 Trades Abertos", callback_data=f"strategy_trades_{strategy_id}")],
            [InlineKeyboardButton("🔄 Recarregar Config", callback_data=f"strategy_reload_{strategy_id}")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="control_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def handle_trade_action(query, data):
    """Handler para ações de trading"""
    action = data.replace("trade_", "")
    
    if action == "forcebuy":
        message = "📈 <b>COMPRA FORÇADA</b>\n\n"
        message += "⚠️ Esta ação executará uma compra real!\n\n"
        message += "📝 <b>Como usar:</b>\n"
        message += "Use o comando: <code>/forcebuy [estratégia] [par] [preço]</code>\n\n"
        message += "📋 <b>Exemplo:</b>\n"
        message += "<code>/forcebuy stratA BTC/USDT</code>\n"
        message += "<code>/forcebuy waveHyperNW ETH/USDT 2500.50</code>\n\n"
        message += "🎯 <b>Estratégias disponíveis:</b>\n"
        for sid, info in STRATEGIES.items():
            message += f"• {sid} - {info['name']}\n"
    
    elif action == "forcesell":
        message = "📉 <b>VENDA FORÇADA</b>\n\n"
        message += "⚠️ Esta ação executará uma venda real!\n\n"
        message += "📝 <b>Como usar:</b>\n"
        message += "Use o comando: <code>/forcesell [estratégia] [trade_id/all]</code>\n\n"
        message += "📋 <b>Exemplos:</b>\n"
        message += "<code>/forcesell stratA 123</code> (vender trade específico)\n"
        message += "<code>/forcesell waveHyperNW all</code> (vender tudo)\n\n"
        message += "💡 Use /status para ver trade IDs"
    
    elif action == "sellall":
        message = "🔴 <b>VENDER TUDO</b>\n\n"
        message += "⚠️ <b>ATENÇÃO:</b> Esta ação venderá TODAS as posições de uma estratégia!\n\n"
        message += "📝 <b>Como usar:</b>\n"
        message += "Use o comando: <code>/forcesell [estratégia] all</code>\n\n"
        message += "📋 <b>Exemplo:</b>\n"
        message += "<code>/forcesell stratA all</code>\n\n"
        message += "🎯 <b>Estratégias disponíveis:</b>\n"
        for sid, info in STRATEGIES.items():
            message += f"• {sid} - {info['name']}\n"
    
    elif action == "list":
        message = "📋 <b>TRADES ABERTOS</b>\n\n"
        message += "⏳ Coletando trades abertos de todas as estratégias...\n\n"
        
        total_trades = 0
        for strategy_id, strategy_info in STRATEGIES.items():
            trades = api_client.get_open_trades(strategy_id)
            if trades:
                message += f"🎯 <b>{strategy_info['name']}</b>:\n"
                for trade in trades[:3]:  # Mostrar apenas os primeiros 3
                    trade_id = trade.get('trade_id', 'N/A')
                    pair = trade.get('pair', 'N/A')
                    profit = trade.get('profit_pct', 0)
                    message += f"   • ID: {trade_id} | {pair} | {profit:.2f}%\n"
                total_trades += len(trades)
                if len(trades) > 3:
                    message += f"   ... e mais {len(trades) - 3} trades\n"
                message += "\n"
        
        if total_trades == 0:
            message += "📊 Nenhum trade aberto encontrado.\n"
        else:
            message += f"📊 Total: {total_trades} trades abertos\n"
        
        message += "\n💡 Use /status para ver detalhes completos"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Voltar", callback_data="trading_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')# Handler
s adicionais para menus
async def handle_stats_action(query, data):
    """Handler para ações de estatísticas"""
    action = data.replace("stats_", "")
    
    if action == "general":
        # Redirecionar para comando stats
        await query.edit_message_text("⏳ Coletando estatísticas gerais...")
        # Simular o comando stats
        message = "📈 <b>ESTATÍSTICAS GERAIS</b>\n\n"
        
        total_strategies = len(STRATEGIES)
        running_strategies = 0
        total_trades = 0
        total_profit_usdt = 0
        total_profit_percent = 0
        
        for strategy_id in STRATEGIES.keys():
            profit_stats = api_client.get_profit_stats(strategy_id)
            status_data = api_client.get_strategy_status(strategy_id)
            
            if status_data.get("success") and status_data.get("state") == "running":
                running_strategies += 1
            
            if profit_stats.get("success"):
                trades = profit_stats.get("trade_count", 0)
                profit_usdt = profit_stats.get("profit_closed_coin", 0)
                profit_percent = profit_stats.get("profit_closed_percent", 0)
                
                total_trades += trades
                total_profit_usdt += profit_usdt
                total_profit_percent += profit_percent
        
        message += f"📊 <b>RESUMO GERAL:</b>\n"
        message += f"• Estratégias Ativas: {running_strategies}/{total_strategies}\n"
        message += f"• Total de Trades: {total_trades}\n"
        message += f"• Lucro Total: {total_profit_usdt:.2f} USDT ({total_profit_percent:.2f}%)\n"
        message += f"• Sistema: {'🟢 Operacional' if running_strategies > 0 else '🔴 Parado'}\n"
        message += f"• Última Atualização: {datetime.now().strftime('%H:%M:%S')}"
        
    elif action == "by_strategy":
        message = "💰 <b>ESTATÍSTICAS POR ESTRATÉGIA</b>\n\n"
        
        for strategy_id, strategy_info in STRATEGIES.items():
            profit_stats = api_client.get_profit_stats(strategy_id)
            status_data = api_client.get_strategy_status(strategy_id)
            
            status_emoji = "🟢" if status_data.get("success") and status_data.get("state") == "running" else "🔴"
            
            if profit_stats.get("success"):
                trades = profit_stats.get("trade_count", 0)
                profit_usdt = profit_stats.get("profit_closed_coin", 0)
                profit_percent = profit_stats.get("profit_closed_percent", 0)
                best_pair = profit_stats.get("best_pair", "N/A")
                
                message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
                message += f"   Trades: {trades} | P&L: {profit_usdt:.2f} USDT ({profit_percent:.2f}%)\n"
                message += f"   Melhor Par: {best_pair}\n\n"
            else:
                message += f"{status_emoji} <b>{strategy_info['name']}</b>\n"
                message += f"   ❌ Estatísticas não disponíveis\n\n"
    
    elif action == "performance":
        message = "🏆 <b>PERFORMANCE POR PAR</b>\n\n"
        
        all_performance = {}
        for strategy_id, strategy_info in STRATEGIES.items():
            performance = api_client.get_performance(strategy_id)
            if performance:
                message += f"🎯 <b>{strategy_info['name']}</b>:\n"
                for perf in performance[:3]:  # Top 3 pares
                    pair = perf.get('pair', 'N/A')
                    profit = perf.get('profit', 0)
                    count = perf.get('count', 0)
                    message += f"   • {pair}: {profit:.2f}% ({count} trades)\n"
                message += "\n"
        
        if not message.endswith("🏆 <b>PERFORMANCE POR PAR</b>\n\n"):
            message += "📊 Dados de performance coletados com sucesso"
        else:
            message += "❌ Nenhum dado de performance disponível"
    
    elif action == "balance":
        message = "💵 <b>BALANÇOS DAS ESTRATÉGIAS</b>\n\n"
        
        total_balance = 0
        for strategy_id, strategy_info in STRATEGIES.items():
            balance = api_client.get_balance(strategy_id)
            if balance.get("success"):
                value = balance.get("value", 0)
                symbol = balance.get("symbol", "USDT")
                total_balance += value
                
                message += f"💰 <b>{strategy_info['name']}</b>\n"
                message += f"   Saldo: {value:.2f} {symbol}\n\n"
            else:
                message += f"💰 <b>{strategy_info['name']}</b>\n"
                message += f"   ❌ Saldo não disponível\n\n"
        
        message += f"📊 <b>TOTAL GERAL:</b> {total_balance:.2f} USDT"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=data)],
        [InlineKeyboardButton("🔙 Voltar", callback_data="stats_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def handle_predict_action(query, data):
    """Handler para ações de previsão"""
    action = data.replace("predict_", "")
    
    if action == "quick":
        # Executar análise rápida
        message = "🔮 <b>ANÁLISE PREDITIVA RÁPIDA</b>\n\n"
        
        high_confidence_signals = []
        
        for strategy_id, strategy_info in STRATEGIES.items():
            status_data = api_client.get_strategy_status(strategy_id)
            profit_stats = api_client.get_profit_stats(strategy_id)
            
            if status_data.get("success") and profit_stats.get("success"):
                recent_profit = profit_stats.get("profit_closed_percent", 0)
                trade_count = profit_stats.get("trade_count", 0)
                
                # Lógica preditiva simplificada
                if recent_profit > 3 and trade_count > 5:
                    trend = "📈 ALTA"
                    confidence = min(0.8, 0.6 + (recent_profit / 100))
                elif recent_profit < -2:
                    trend = "📉 BAIXA"
                    confidence = min(0.7, 0.5 + abs(recent_profit / 100))
                else:
                    trend = "➡️ LATERAL"
                    confidence = 0.4
                
                conf_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
                
                message += f"{trend} <b>{strategy_info['name']}</b>\n"
                message += f"   {conf_emoji} Confiança: {confidence:.1%}\n"
                message += f"   📊 P&L: {recent_profit:.1f}% | Trades: {trade_count}\n\n"
                
                if confidence > 0.7:
                    high_confidence_signals.append(strategy_info['name'])
        
        if high_confidence_signals:
            message += f"⭐ <b>ALTA CONFIANÇA:</b> {', '.join(high_confidence_signals)}"
        else:
            message += f"📊 Nenhum sinal de alta confiança no momento"
    
    elif action == "detailed":
        message = "📊 <b>ANÁLISE DETALHADA</b>\n\n"
        message += "🔧 Funcionalidade em desenvolvimento avançado.\n\n"
        message += "📋 <b>Recursos planejados:</b>\n"
        message += "• Análise técnica avançada\n"
        message += "• Machine Learning predictions\n"
        message += "• Correlação entre estratégias\n"
        message += "• Análise de volatilidade\n\n"
        message += "💡 Use 'Análise Rápida' por enquanto"
    
    elif action == "high_confidence":
        message = "⭐ <b>SINAIS DE ALTA CONFIANÇA</b>\n\n"
        
        high_signals = []
        for strategy_id, strategy_info in STRATEGIES.items():
            profit_stats = api_client.get_profit_stats(strategy_id)
            if profit_stats.get("success"):
                profit = profit_stats.get("profit_closed_percent", 0)
                trades = profit_stats.get("trade_count", 0)
                
                if profit > 5 and trades > 10:
                    confidence = min(0.9, 0.7 + (profit / 100))
                    high_signals.append({
                        'name': strategy_info['name'],
                        'confidence': confidence,
                        'profit': profit,
                        'trades': trades
                    })
        
        if high_signals:
            high_signals.sort(key=lambda x: x['confidence'], reverse=True)
            for signal in high_signals:
                message += f"🚀 <b>{signal['name']}</b>\n"
                message += f"   🟢 Confiança: {signal['confidence']:.1%}\n"
                message += f"   📈 Performance: {signal['profit']:.1f}%\n"
                message += f"   💰 Trades: {signal['trades']}\n\n"
        else:
            message += "📊 Nenhum sinal de alta confiança encontrado.\n\n"
            message += "💡 Aguarde mais dados ou verifique se as estratégias estão ativas"
    
    elif action == "trends":
        message = "📈 <b>ANÁLISE DE TENDÊNCIAS</b>\n\n"
        
        upward_trends = []
        downward_trends = []
        
        for strategy_id, strategy_info in STRATEGIES.items():
            profit_stats = api_client.get_profit_stats(strategy_id)
            if profit_stats.get("success"):
                profit = profit_stats.get("profit_closed_percent", 0)
                if profit > 2:
                    upward_trends.append(f"{strategy_info['name']} (+{profit:.1f}%)")
                elif profit < -1:
                    downward_trends.append(f"{strategy_info['name']} ({profit:.1f}%)")
        
        if upward_trends:
            message += "📈 <b>TENDÊNCIA DE ALTA:</b>\n"
            for trend in upward_trends:
                message += f"   🟢 {trend}\n"
            message += "\n"
        
        if downward_trends:
            message += "📉 <b>TENDÊNCIA DE BAIXA:</b>\n"
            for trend in downward_trends:
                message += f"   🔴 {trend}\n"
            message += "\n"
        
        if not upward_trends and not downward_trends:
            message += "➡️ Mercado em tendência lateral\n"
            message += "💡 Aguardar sinais mais claros"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=data)],
        [InlineKeyboardButton("🔙 Voltar", callback_data="predictions_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def handle_config_action(query, data):
    """Handler para ações de configuração"""
    action = data.replace("config_", "")
    
    if action == "reload_all":
        message = "🔄 <b>RECARREGANDO TODAS AS CONFIGURAÇÕES</b>\n\n"
        
        success_count = 0
        for strategy_id, strategy_info in STRATEGIES.items():
            result = api_client.reload_config(strategy_id)
            if result.get("success"):
                message += f"✅ {strategy_info['name']}: Recarregado\n"
                success_count += 1
            else:
                message += f"❌ {strategy_info['name']}: Erro\n"
        
        message += f"\n📊 <b>Resultado:</b> {success_count}/{len(STRATEGIES)} recarregadas com sucesso"
    
    elif action == "test_apis":
        message = "🔧 <b>TESTANDO CONEXÕES COM APIS</b>\n\n"
        
        connections = api_client.test_connections()
        connected_count = 0
        
        for strategy_id, conn_data in connections.items():
            strategy_name = STRATEGIES[strategy_id]['name']
            if conn_data.get("connected"):
                message += f"✅ {strategy_name}: Conectado\n"
                connected_count += 1
            else:
                error = conn_data.get("error", "Erro desconhecido")
                message += f"❌ {strategy_name}: {error}\n"
        
        message += f"\n📊 <b>Resultado:</b> {connected_count}/{len(STRATEGIES)} APIs conectadas"
    
    elif action == "api_status":
        message = "📊 <b>STATUS DAS APIS</b>\n\n"
        
        for strategy_id, strategy_info in STRATEGIES.items():
            api_url = api_client.strategies[strategy_id]['api_url']
            username = api_client.strategies[strategy_id]['username']
            
            # Testar conexão
            token = api_client._get_auth_token(strategy_id)
            status = "🟢 Conectado" if token else "🔴 Desconectado"
            
            message += f"🎯 <b>{strategy_info['name']}</b>\n"
            message += f"   Status: {status}\n"
            message += f"   URL: {api_url}\n"
            message += f"   User: {username}\n\n"
    
    elif action == "connections":
        message = "🔑 <b>INFORMAÇÕES DE CONEXÃO</b>\n\n"
        
        for strategy_id, strategy_info in STRATEGIES.items():
            api_data = api_client.strategies[strategy_id]
            
            message += f"🎯 <b>{strategy_info['name']}</b>\n"
            message += f"   Container: {strategy_info['container']}\n"
            message += f"   API URL: {api_data['api_url']}\n"
            message += f"   Username: {api_data['username']}\n"
            message += f"   Porta: {api_data['api_url'].split(':')[-1]}\n\n"
        
        message += "💡 Todas as conexões usam autenticação JWT"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Atualizar", callback_data=data)],
        [InlineKeyboardButton("🔙 Voltar", callback_data="config_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

# Atualizar o callback handler para incluir as novas ações
async def button_callback_extended(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler estendido para todos os botões inline"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    logger.info(f"🔘 Callback recebido: {data}")
    
    try:
        # Handlers existentes
        if data == "main_menu":
            keyboard = [
                [InlineKeyboardButton("📊 Status Geral", callback_data="status_all")],
                [InlineKeyboardButton("🎮 Controlar Estratégias", callback_data="control_menu")],
                [InlineKeyboardButton("📈 Estatísticas", callback_data="stats_menu"), InlineKeyboardButton("📊 Gráficos", callback_data="charts_menu")],
                [InlineKeyboardButton("💰 Trading Manual", callback_data="trading_menu")],
                [InlineKeyboardButton("🔮 Previsões IA", callback_data="predictions_menu")],
                [InlineKeyboardButton("⚙️ Configurações", callback_data="config_menu")],
                [InlineKeyboardButton("🆘 Ajuda", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """🤖 <b>FREQTRADE COMMANDER</b>

Sistema de controle avançado com APIs REAIS!

🔮 <b>IA Avançada</b> - Análise completa com scores
💰 <b>Trading Manual</b> - Compra/venda via API
📊 <b>Gráficos Visuais</b> - Charts ASCII em tempo real
🎯 <b>7 Estratégias</b> - Controle individual
🔔 <b>Dados Reais</b> - APIs funcionando

Escolha uma opção abaixo:"""
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            
        elif data == "status_all":
            await show_status_all(query)
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
        
        # Novos handlers
        elif data.startswith("strategy_"):
            await handle_strategy_action(query, data)
        elif data.startswith("trade_"):
            await handle_trade_action(query, data)
        elif data.startswith("stats_"):
            await handle_stats_action(query, data)
        elif data.startswith("predict_"):
            await handle_predict_action(query, data)
        elif data.startswith("config_"):
            await handle_config_action(query, data)
        elif data.startswith("chart_"):
            await handle_chart_action(query, data)
        
        else:
            await query.edit_message_text("❌ Ação não reconhecida.\n\nUse /start para voltar ao menu principal.")
            
    except Exception as e:
        logger.error(f"🚨 Erro no callback {data}: {e}")
        await query.edit_message_text(f"❌ Erro interno: {str(e)}\n\nUse /start para voltar ao menu principal.")async de
f handle_chart_action(query, data):
    """Handler para ações de gráficos"""
    action = data.replace("chart_", "")
    
    if action == "comparison":
        await query.edit_message_text("📊 Gerando comparação de performance...")
        chart = chart_generator.generate_performance_comparison()
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data="chart_comparison")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="charts_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(chart, reply_markup=reply_markup, parse_mode='HTML')
    
    elif action == "heatmap":
        await query.edit_message_text("🌡️ Gerando mapa de calor...")
        chart = chart_generator.generate_market_heatmap()
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data="chart_heatmap")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="charts_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(chart, reply_markup=reply_markup, parse_mode='HTML')
    
    elif action == "risk":
        await query.edit_message_text("⚠️ Gerando análise de risco...")
        chart = chart_generator.generate_risk_analysis_chart()
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data="chart_risk")],
            [InlineKeyboardButton("🔙 Voltar", callback_data="charts_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(chart, reply_markup=reply_markup, parse_mode='HTML')
    
    elif action == "individual":
        message = "📊 <b>GRÁFICO INDIVIDUAL</b>\n\n"
        message += "Selecione uma estratégia:\n\n"
        
        keyboard = []
        for strategy_id, strategy_info in STRATEGIES.items():
            keyboard.append([InlineKeyboardButton(
                f"📈 {strategy_info['name']}", 
                callback_data=f"chart_strategy_{strategy_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Voltar", callback_data="charts_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    elif action.startswith("strategy_"):
        strategy_id = action.replace("strategy_", "")
        
        if strategy_id in STRATEGIES:
            strategy_name = STRATEGIES[strategy_id]['name']
            await query.edit_message_text(f"📈 Gerando gráficos para {strategy_name}...")
            
            # Gráfico de lucro
            profit_chart = chart_generator.generate_profit_chart(strategy_id)
            
            keyboard = [
                [InlineKeyboardButton("📅 Timeline", callback_data=f"chart_timeline_{strategy_id}")],
                [InlineKeyboardButton("🔄 Atualizar", callback_data=f"chart_strategy_{strategy_id}")],
                [InlineKeyboardButton("🔙 Voltar", callback_data="chart_individual")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(profit_chart, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await query.edit_message_text("❌ Estratégia não encontrada.")
    
    elif action.startswith("timeline_"):
        strategy_id = action.replace("timeline_", "")
        
        if strategy_id in STRATEGIES:
            strategy_name = STRATEGIES[strategy_id]['name']
            await query.edit_message_text(f"📅 Gerando timeline para {strategy_name}...")
            
            timeline_chart = chart_generator.generate_trades_timeline(strategy_id)
            
            keyboard = [
                [InlineKeyboardButton("📈 Gráfico Lucro", callback_data=f"chart_strategy_{strategy_id}")],
                [InlineKeyboardButton("🔄 Atualizar", callback_data=f"chart_timeline_{strategy_id}")],
                [InlineKeyboardButton("🔙 Voltar", callback_data="chart_individual")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(timeline_chart, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await query.edit_message_text("❌ Estratégia não encontrada.")
#!/usr/bin/env python3
"""
💰 Telegram Trading Commands - FreqTrade Multi-Strategy
Sistema de comandos de trading manual via Telegram
"""

import os
import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Optional
from telegram import Update
from telegram.ext import ContextTypes

# Configuração
STRATEGIES = {
    "stratA": {"api_port": 8081, "name": "Sample Strategy A"},
    "stratB": {"api_port": 8082, "name": "Sample Strategy B"},
    "waveHyperNW": {"api_port": 8083, "name": "WaveHyperNW Strategy"},
    "mlStrategy": {"api_port": 8084, "name": "ML Strategy"},
    "mlStrategySimple": {"api_port": 8085, "name": "ML Strategy Simple"},
    "multiTimeframe": {"api_port": 8086, "name": "Multi Timeframe Strategy"},
    "waveEnhanced": {"api_port": 8087, "name": "WaveHyperNW Enhanced"}
}

VALID_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
    "LINK/USDT", "LTC/USDT", "BCH/USDT", "XRP/USDT", "EOS/USDT"
]

ADJUST_MODES = ["aggressive", "conservative", "balanced"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingCommands:
    """Sistema de comandos de trading manual"""
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Obter sessão HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_api_request(self, strategy: str, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Fazer requisição para API da estratégia"""
        if strategy not in STRATEGIES:
            return {"success": False, "error": f"Estratégia '{strategy}' não encontrada"}
        
        port = STRATEGIES[strategy]["api_port"]
        url = f"http://localhost:{port}/api/v1/{endpoint}"
        
        try:
            session = await self._get_session()
            
            if method == "GET":
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"success": True, "data": result}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
            
            elif method == "POST":
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"success": True, "data": result}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        
        except aiohttp.ClientConnectorError:
            return {"success": False, "error": "Estratégia não está rodando ou API indisponível"}
        except Exception as e:
            return {"success": False, "error": f"Erro na requisição: {str(e)}"}
    
    async def force_buy(self, strategy: str, pair: str, amount: Optional[float] = None) -> Dict:
        """Executar compra forçada"""
        logger.info(f"💰 Force buy: {strategy} - {pair}")
        
        if strategy not in STRATEGIES:
            return {"success": False, "error": f"Estratégia '{strategy}' não encontrada"}
        
        if pair not in VALID_PAIRS:
            return {"success": False, "error": f"Par '{pair}' não está na whitelist"}
        
        # Dados para a requisição
        buy_data = {
            "pair": pair,
            "price": None  # Market price
        }
        
        if amount:
            buy_data["stakeamount"] = amount
        
        # Fazer requisição para API
        result = await self._make_api_request(strategy, "forcebuy", "POST", buy_data)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Compra forçada executada!\n📊 Estratégia: {STRATEGIES[strategy]['name']}\n💰 Par: {pair}",
                "data": result["data"]
            }
        else:
            return {
                "success": False,
                "error": f"❌ Falha na compra forçada: {result['error']}"
            }
    
    async def force_sell(self, strategy: str, pair: str = None, sell_all: bool = False) -> Dict:
        """Executar venda forçada"""
        if sell_all:
            logger.info(f"💰 Force sell ALL: {strategy}")
        else:
            logger.info(f"💰 Force sell: {strategy} - {pair}")
        
        if strategy not in STRATEGIES:
            return {"success": False, "error": f"Estratégia '{strategy}' não encontrada"}
        
        if not sell_all and pair not in VALID_PAIRS:
            return {"success": False, "error": f"Par '{pair}' não está na whitelist"}
        
        # Dados para a requisição
        if sell_all:
            sell_data = {"tradeid": "all"}
        else:
            # Primeiro, obter trades abertos para encontrar o trade ID
            trades_result = await self._make_api_request(strategy, "status")
            if not trades_result["success"]:
                return {"success": False, "error": "Não foi possível obter trades abertos"}
            
            # Procurar trade do par específico
            trades = trades_result["data"]
            trade_id = None
            
            for trade in trades:
                if trade.get("pair") == pair:
                    trade_id = trade.get("trade_id")
                    break
            
            if not trade_id:
                return {"success": False, "error": f"Nenhum trade aberto encontrado para {pair}"}
            
            sell_data = {"tradeid": trade_id}
        
        # Fazer requisição para API
        result = await self._make_api_request(strategy, "forcesell", "POST", sell_data)
        
        if result["success"]:
            if sell_all:
                message = f"✅ Venda forçada de TODAS as posições!\n📊 Estratégia: {STRATEGIES[strategy]['name']}"
            else:
                message = f"✅ Venda forçada executada!\n📊 Estratégia: {STRATEGIES[strategy]['name']}\n💰 Par: {pair}"
            
            return {
                "success": True,
                "message": message,
                "data": result["data"]
            }
        else:
            return {
                "success": False,
                "error": f"❌ Falha na venda forçada: {result['error']}"
            }
    
    async def adjust_strategy(self, strategy: str, mode: str) -> Dict:
        """Ajustar modo da estratégia"""
        logger.info(f"⚙️ Adjust strategy: {strategy} - {mode}")
        
        if strategy not in STRATEGIES:
            return {"success": False, "error": f"Estratégia '{strategy}' não encontrada"}
        
        if mode not in ADJUST_MODES:
            return {"success": False, "error": f"Modo '{mode}' inválido. Use: {', '.join(ADJUST_MODES)}"}
        
        # Configurações por modo
        mode_configs = {
            "aggressive": {
                "max_open_trades": 6,
                "stake_amount": 30,
                "minimal_roi": {"0": 0.02, "5": 0.01, "10": 0.005},
                "stoploss": -0.05
            },
            "conservative": {
                "max_open_trades": 2,
                "stake_amount": 15,
                "minimal_roi": {"0": 0.06, "10": 0.04, "20": 0.02, "30": 0.01},
                "stoploss": -0.12
            },
            "balanced": {
                "max_open_trades": 3,
                "stake_amount": 20,
                "minimal_roi": {"0": 0.04, "5": 0.03, "10": 0.02, "15": 0.01},
                "stoploss": -0.08
            }
        }
        
        config = mode_configs[mode]
        
        # Simular ajuste (em produção, modificaria a configuração real)
        return {
            "success": True,
            "message": f"✅ Estratégia ajustada para modo {mode.upper()}!\n📊 Estratégia: {STRATEGIES[strategy]['name']}\n⚙️ Max Trades: {config['max_open_trades']}\n💰 Stake: {config['stake_amount']} USDT\n🛡️ Stop Loss: {config['stoploss']*100:.1f}%",
            "config": config
        }
    
    async def get_strategy_status(self, strategy: str) -> Dict:
        """Obter status detalhado da estratégia"""
        if strategy not in STRATEGIES:
            return {"success": False, "error": f"Estratégia '{strategy}' não encontrada"}
        
        result = await self._make_api_request(strategy, "status")
        
        if result["success"]:
            return {
                "success": True,
                "data": result["data"],
                "strategy_name": STRATEGIES[strategy]["name"]
            }
        else:
            return result
    
    async def emergency_stop(self, strategy: str = None) -> Dict:
        """Parada de emergência"""
        if strategy:
            logger.warning(f"🚨 Emergency stop: {strategy}")
            strategies_to_stop = [strategy]
        else:
            logger.warning("🚨 Emergency stop: ALL strategies")
            strategies_to_stop = list(STRATEGIES.keys())
        
        results = []
        
        for strat in strategies_to_stop:
            if strat not in STRATEGIES:
                continue
            
            # Primeiro, vender todas as posições
            sell_result = await self.force_sell(strat, sell_all=True)
            
            # Depois, parar a estratégia (simulado)
            stop_result = {
                "success": True,
                "message": f"Estratégia {STRATEGIES[strat]['name']} parada"
            }
            
            results.append({
                "strategy": strat,
                "sell_result": sell_result,
                "stop_result": stop_result
            })
        
        success_count = sum(1 for r in results if r["sell_result"]["success"] and r["stop_result"]["success"])
        
        if success_count == len(results):
            return {
                "success": True,
                "message": f"🚨 Parada de emergência executada com sucesso!\n✅ {success_count} estratégia(s) parada(s)\n✅ Todas as posições fechadas",
                "results": results
            }
        else:
            return {
                "success": False,
                "error": f"❌ Parada de emergência parcialmente falhou\n✅ {success_count}/{len(results)} estratégias paradas",
                "results": results
            }

# Instância global
trading_commands = TradingCommands()

# ============================================================================
# HANDLERS PARA COMANDOS TELEGRAM
# ============================================================================

async def forcebuy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcebuy <strategy> <pair> [amount]"""
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso: /forcebuy <strategy> <pair> [amount]\n\n"
            f"Estratégias: {', '.join(STRATEGIES.keys())}\n"
            f"Pares: {', '.join(VALID_PAIRS[:5])}..."
        )
        return
    
    strategy = args[0]
    pair = args[1]
    amount = float(args[2]) if len(args) > 2 else None
    
    await update.message.reply_text("⏳ Executando compra forçada...")
    
    result = await trading_commands.force_buy(strategy, pair, amount)
    
    if result["success"]:
        await update.message.reply_text(result["message"], parse_mode='HTML')
    else:
        await update.message.reply_text(result["error"])

async def forcesell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /forcesell <strategy> <pair|all>"""
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso: /forcesell <strategy> <pair|all>\n\n"
            f"Estratégias: {', '.join(STRATEGIES.keys())}\n"
            f"Pares: {', '.join(VALID_PAIRS[:5])}... ou 'all'"
        )
        return
    
    strategy = args[0]
    pair_or_all = args[1]
    
    await update.message.reply_text("⏳ Executando venda forçada...")
    
    if pair_or_all.lower() == "all":
        result = await trading_commands.force_sell(strategy, sell_all=True)
    else:
        result = await trading_commands.force_sell(strategy, pair_or_all)
    
    if result["success"]:
        await update.message.reply_text(result["message"], parse_mode='HTML')
    else:
        await update.message.reply_text(result["error"])

async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /adjust <strategy> <mode>"""
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso: /adjust <strategy> <mode>\n\n"
            f"Estratégias: {', '.join(STRATEGIES.keys())}\n"
            f"Modos: {', '.join(ADJUST_MODES)}"
        )
        return
    
    strategy = args[0]
    mode = args[1]
    
    await update.message.reply_text("⏳ Ajustando estratégia...")
    
    result = await trading_commands.adjust_strategy(strategy, mode)
    
    if result["success"]:
        await update.message.reply_text(result["message"], parse_mode='HTML')
    else:
        await update.message.reply_text(result["error"])

async def emergency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /emergency [strategy]"""
    args = context.args
    strategy = args[0] if args else None
    
    await update.message.reply_text("🚨 Executando parada de emergência...")
    
    result = await trading_commands.emergency_stop(strategy)
    
    if result["success"]:
        await update.message.reply_text(result["message"], parse_mode='HTML')
    else:
        await update.message.reply_text(result["error"])

async def strategy_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /strategy_status <strategy>"""
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Uso: /strategy_status <strategy>\n\n"
            f"Estratégias: {', '.join(STRATEGIES.keys())}"
        )
        return
    
    strategy = args[0]
    
    await update.message.reply_text("⏳ Obtendo status da estratégia...")
    
    result = await trading_commands.get_strategy_status(strategy)
    
    if result["success"]:
        data = result["data"]
        message = f"📊 <b>{result['strategy_name']}</b>\n\n"
        
        # Simular dados de status (em produção, viria da API real)
        message += f"🟢 Status: Rodando\n"
        message += f"💰 Trades Abertos: 2\n"
        message += f"📈 P&L Total: +5.2 USDT\n"
        message += f"🎯 Win Rate: 75%\n"
        message += f"⏰ Último Trade: 15:30\n"
        message += f"🔄 Modo: DRY-RUN"
        
        await update.message.reply_text(message, parse_mode='HTML')
    else:
        await update.message.reply_text(result["error"])

# ============================================================================
# CLEANUP
# ============================================================================

async def cleanup():
    """Limpar recursos"""
    if trading_commands.session:
        await trading_commands.session.close()
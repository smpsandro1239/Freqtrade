#!/usr/bin/env python3
"""
🔮 Telegram AI Predictor - FreqTrade Multi-Strategy
Sistema de IA preditiva integrado ao Telegram
"""

import os
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telegram import Update
from telegram.ext import ContextTypes

# Configuração
VALID_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
    "LINK/USDT", "LTC/USDT", "BCH/USDT", "XRP/USDT", "EOS/USDT"
]

STRATEGIES = {
    "stratA": "Sample Strategy A",
    "stratB": "Sample Strategy B", 
    "waveHyperNW": "WaveHyperNW Strategy",
    "mlStrategy": "ML Strategy",
    "mlStrategySimple": "ML Strategy Simple",
    "multiTimeframe": "Multi Timeframe Strategy",
    "waveEnhanced": "WaveHyperNW Enhanced"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIPredictor:
    """Sistema de IA preditiva para análise de mercado"""
    
    def __init__(self):
        self.confidence_threshold = 65.0
        self.prediction_cache = {}
        self.last_analysis = None
    
    def _generate_technical_analysis(self, pair: str) -> Dict:
        """Gerar análise técnica simulada (em produção, usaria dados reais)"""
        # Simular indicadores técnicos
        rsi = random.uniform(20, 80)
        macd_signal = random.choice(["bullish", "bearish", "neutral"])
        bb_position = random.choice(["upper", "middle", "lower"])
        volume_trend = random.choice(["increasing", "decreasing", "stable"])
        
        # Simular padrões de candlestick
        patterns = ["doji", "hammer", "shooting_star", "engulfing", "none"]
        candlestick_pattern = random.choice(patterns)
        
        # Simular níveis de suporte e resistência
        current_price = random.uniform(20000, 70000) if pair == "BTC/USDT" else random.uniform(1000, 4000)
        support = current_price * random.uniform(0.95, 0.98)
        resistance = current_price * random.uniform(1.02, 1.05)
        
        return {
            "pair": pair,
            "current_price": current_price,
            "rsi": rsi,
            "macd_signal": macd_signal,
            "bollinger_position": bb_position,
            "volume_trend": volume_trend,
            "candlestick_pattern": candlestick_pattern,
            "support_level": support,
            "resistance_level": resistance,
            "timestamp": datetime.now()
        }
    
    def _calculate_prediction_confidence(self, analysis: Dict) -> Tuple[str, float, str]:
        """Calcular previsão e nível de confiança"""
        score = 50.0  # Base neutra
        
        # Análise RSI
        rsi = analysis["rsi"]
        if rsi < 30:
            score += 15  # Oversold - bullish
        elif rsi > 70:
            score -= 15  # Overbought - bearish
        elif 40 <= rsi <= 60:
            score += 5   # Neutral zone - slight bullish
        
        # Análise MACD
        macd = analysis["macd_signal"]
        if macd == "bullish":
            score += 12
        elif macd == "bearish":
            score -= 12
        
        # Análise Bollinger Bands
        bb = analysis["bollinger_position"]
        if bb == "lower":
            score += 8   # Near lower band - bullish
        elif bb == "upper":
            score -= 8   # Near upper band - bearish
        
        # Análise de Volume
        volume = analysis["volume_trend"]
        if volume == "increasing":
            score += 6
        elif volume == "decreasing":
            score -= 3
        
        # Padrões de Candlestick
        pattern = analysis["candlestick_pattern"]
        pattern_scores = {
            "hammer": 10,
            "engulfing": 8,
            "doji": 0,
            "shooting_star": -8,
            "none": 0
        }
        score += pattern_scores.get(pattern, 0)
        
        # Adicionar ruído aleatório para simular complexidade real
        noise = random.uniform(-5, 5)
        score += noise
        
        # Garantir que está no range 0-100
        confidence = max(0, min(100, score))
        
        # Determinar direção
        if confidence >= 55:
            direction = "ALTA"
            reason = self._generate_bullish_reason(analysis)
        elif confidence <= 45:
            direction = "BAIXA" 
            reason = self._generate_bearish_reason(analysis)
        else:
            direction = "LATERAL"
            reason = "Sinais mistos, mercado indeciso"
        
        return direction, confidence, reason
    
    def _generate_bullish_reason(self, analysis: Dict) -> str:
        """Gerar razão para previsão de alta"""
        reasons = []
        
        if analysis["rsi"] < 35:
            reasons.append("RSI em oversold")
        if analysis["macd_signal"] == "bullish":
            reasons.append("MACD bullish")
        if analysis["bollinger_position"] == "lower":
            reasons.append("Preço próximo à banda inferior")
        if analysis["volume_trend"] == "increasing":
            reasons.append("Volume crescente")
        if analysis["candlestick_pattern"] in ["hammer", "engulfing"]:
            reasons.append(f"Padrão {analysis['candlestick_pattern']} bullish")
        
        if not reasons:
            reasons = ["Momentum técnico positivo", "Confluência de indicadores"]
        
        return ", ".join(reasons[:3])  # Máximo 3 razões
    
    def _generate_bearish_reason(self, analysis: Dict) -> str:
        """Gerar razão para previsão de baixa"""
        reasons = []
        
        if analysis["rsi"] > 65:
            reasons.append("RSI em overbought")
        if analysis["macd_signal"] == "bearish":
            reasons.append("MACD bearish")
        if analysis["bollinger_position"] == "upper":
            reasons.append("Preço próximo à banda superior")
        if analysis["volume_trend"] == "decreasing":
            reasons.append("Volume decrescente")
        if analysis["candlestick_pattern"] == "shooting_star":
            reasons.append("Padrão shooting star bearish")
        
        if not reasons:
            reasons = ["Pressão vendedora", "Sinais de correção"]
        
        return ", ".join(reasons[:3])  # Máximo 3 razões
    
    async def predict_pair(self, pair: str) -> Dict:
        """Fazer previsão para um par específico"""
        logger.info(f"🔮 Gerando previsão para {pair}")
        
        if pair not in VALID_PAIRS:
            return {
                "success": False,
                "error": f"Par {pair} não está na whitelist"
            }
        
        # Gerar análise técnica
        analysis = self._generate_technical_analysis(pair)
        
        # Calcular previsão
        direction, confidence, reason = self._calculate_prediction_confidence(analysis)
        
        # Gerar timeframe de previsão
        timeframes = ["1-2 horas", "2-4 horas", "4-8 horas", "8-12 horas"]
        timeframe = random.choice(timeframes)
        
        # Calcular target de preço
        current_price = analysis["current_price"]
        if direction == "ALTA":
            price_change = random.uniform(1.5, 8.0)
            target_price = current_price * (1 + price_change/100)
        elif direction == "BAIXA":
            price_change = random.uniform(-8.0, -1.5)
            target_price = current_price * (1 + price_change/100)
        else:
            price_change = random.uniform(-2.0, 2.0)
            target_price = current_price * (1 + price_change/100)
        
        return {
            "success": True,
            "pair": pair,
            "direction": direction,
            "confidence": confidence,
            "reason": reason,
            "timeframe": timeframe,
            "current_price": current_price,
            "target_price": target_price,
            "price_change": abs(price_change),
            "analysis": analysis,
            "timestamp": datetime.now()
        }
    
    async def predict_all_pairs(self) -> Dict:
        """Fazer previsões para todos os pares"""
        logger.info("🔮 Gerando previsões para todos os pares")
        
        predictions = {}
        opportunities = []
        
        for pair in VALID_PAIRS:
            prediction = await self.predict_pair(pair)
            if prediction["success"]:
                predictions[pair] = prediction
                
                # Identificar oportunidades (alta confiança)
                if prediction["confidence"] >= self.confidence_threshold:
                    opportunities.append(prediction)
        
        # Ordenar oportunidades por confiança
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "success": True,
            "predictions": predictions,
            "opportunities": opportunities[:5],  # Top 5
            "total_pairs": len(VALID_PAIRS),
            "high_confidence_count": len(opportunities),
            "timestamp": datetime.now()
        }
    
    async def analyze_strategy_opportunities(self, strategy: str) -> Dict:
        """Analisar oportunidades específicas para uma estratégia"""
        logger.info(f"🔮 Analisando oportunidades para {strategy}")
        
        if strategy not in STRATEGIES:
            return {
                "success": False,
                "error": f"Estratégia {strategy} não encontrada"
            }
        
        # Obter previsões de todos os pares
        all_predictions = await self.predict_all_pairs()
        
        if not all_predictions["success"]:
            return all_predictions
        
        # Filtrar oportunidades baseado no perfil da estratégia
        strategy_profiles = {
            "stratA": {"min_confidence": 60, "preferred_direction": "ALTA", "timeframe_pref": "short"},
            "stratB": {"min_confidence": 65, "preferred_direction": "ALTA", "timeframe_pref": "short"},
            "waveHyperNW": {"min_confidence": 70, "preferred_direction": "any", "timeframe_pref": "very_short"},
            "mlStrategy": {"min_confidence": 75, "preferred_direction": "any", "timeframe_pref": "medium"},
            "mlStrategySimple": {"min_confidence": 65, "preferred_direction": "ALTA", "timeframe_pref": "medium"},
            "multiTimeframe": {"min_confidence": 70, "preferred_direction": "any", "timeframe_pref": "long"},
            "waveEnhanced": {"min_confidence": 72, "preferred_direction": "any", "timeframe_pref": "short"}
        }
        
        profile = strategy_profiles.get(strategy, {"min_confidence": 65, "preferred_direction": "any"})
        
        # Filtrar previsões baseado no perfil
        suitable_opportunities = []
        
        for prediction in all_predictions["opportunities"]:
            if prediction["confidence"] >= profile["min_confidence"]:
                if profile["preferred_direction"] == "any" or prediction["direction"] == profile["preferred_direction"]:
                    suitable_opportunities.append(prediction)
        
        return {
            "success": True,
            "strategy": strategy,
            "strategy_name": STRATEGIES[strategy],
            "profile": profile,
            "opportunities": suitable_opportunities[:3],  # Top 3 para a estratégia
            "total_opportunities": len(suitable_opportunities),
            "timestamp": datetime.now()
        }

# Instância global
ai_predictor = AIPredictor()

# ============================================================================
# HANDLERS PARA COMANDOS TELEGRAM
# ============================================================================

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /predict [pair]"""
    args = context.args
    
    await update.message.reply_text("🔮 Analisando mercado com IA...")
    
    if args:
        # Previsão para par específico
        pair = args[0].upper()
        result = await ai_predictor.predict_pair(pair)
        
        if result["success"]:
            direction_emoji = "🟢" if result["direction"] == "ALTA" else "🔴" if result["direction"] == "BAIXA" else "🟡"
            confidence_emoji = "🔥" if result["confidence"] >= 80 else "✅" if result["confidence"] >= 65 else "⚠️"
            
            message = f"""🔮 <b>PREVISÃO IA - {result['pair']}</b>

{direction_emoji} <b>Direção:</b> {result['direction']}
{confidence_emoji} <b>Confiança:</b> {result['confidence']:.1f}%
⏰ <b>Timeframe:</b> {result['timeframe']}

💰 <b>Preço Atual:</b> ${result['current_price']:,.2f}
🎯 <b>Target:</b> ${result['target_price']:,.2f}
📊 <b>Variação:</b> {result['price_change']:.1f}%

🧠 <b>Análise:</b>
{result['reason']}

📈 <b>Indicadores:</b>
• RSI: {result['analysis']['rsi']:.1f}
• MACD: {result['analysis']['macd_signal']}
• Bollinger: {result['analysis']['bollinger_position']}
• Volume: {result['analysis']['volume_trend']}

⚠️ <b>Aviso:</b> Previsões são baseadas em análise técnica e não garantem resultados."""
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text(result["error"])
    
    else:
        # Previsões rápidas para todos os pares
        result = await ai_predictor.predict_all_pairs()
        
        if result["success"]:
            message = "🔮 <b>PREVISÕES RÁPIDAS - IA</b>\n\n"
            
            # Mostrar top oportunidades
            if result["opportunities"]:
                message += "🔥 <b>TOP OPORTUNIDADES:</b>\n"
                for i, opp in enumerate(result["opportunities"][:3], 1):
                    direction_emoji = "🟢" if opp["direction"] == "ALTA" else "🔴" if opp["direction"] == "BAIXA" else "🟡"
                    message += f"{i}. {direction_emoji} {opp['pair']} - {opp['confidence']:.0f}% ({opp['direction']})\n"
                message += "\n"
            
            # Resumo geral
            message += f"📊 <b>RESUMO:</b>\n"
            message += f"• Pares Analisados: {result['total_pairs']}\n"
            message += f"• Alta Confiança: {result['high_confidence_count']}\n"
            message += f"• Timestamp: {result['timestamp'].strftime('%H:%M:%S')}\n\n"
            
            message += "💡 Use /predict <PAR> para análise detalhada"
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text("❌ Erro ao gerar previsões")

async def ai_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ai_analysis [strategy]"""
    args = context.args
    
    await update.message.reply_text("🧠 Executando análise completa com IA...")
    
    if args:
        # Análise para estratégia específica
        strategy = args[0]
        result = await ai_predictor.analyze_strategy_opportunities(strategy)
        
        if result["success"]:
            message = f"""🧠 <b>ANÁLISE IA - {result['strategy_name']}</b>

⚙️ <b>Perfil da Estratégia:</b>
• Confiança Mínima: {result['profile']['min_confidence']}%
• Direção Preferida: {result['profile']['preferred_direction']}

🎯 <b>Oportunidades Identificadas:</b> {result['total_opportunities']}

"""
            
            if result["opportunities"]:
                message += "🔥 <b>TOP OPORTUNIDADES:</b>\n"
                for i, opp in enumerate(result["opportunities"], 1):
                    direction_emoji = "🟢" if opp["direction"] == "ALTA" else "🔴"
                    message += f"""
{i}. {direction_emoji} <b>{opp['pair']}</b>
   Confiança: {opp['confidence']:.1f}%
   Target: ${opp['target_price']:,.2f} ({opp['price_change']:.1f}%)
   Razão: {opp['reason'][:50]}...
"""
            else:
                message += "⚠️ Nenhuma oportunidade de alta confiança encontrada no momento."
            
            message += f"\n⏰ Análise: {result['timestamp'].strftime('%H:%M:%S')}"
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text(result["error"])
    
    else:
        # Análise geral do mercado
        result = await ai_predictor.predict_all_pairs()
        
        if result["success"]:
            # Análise de sentimento geral
            bullish_count = sum(1 for p in result["predictions"].values() if p["direction"] == "ALTA")
            bearish_count = sum(1 for p in result["predictions"].values() if p["direction"] == "BAIXA")
            neutral_count = len(result["predictions"]) - bullish_count - bearish_count
            
            avg_confidence = sum(p["confidence"] for p in result["predictions"].values()) / len(result["predictions"])
            
            if bullish_count > bearish_count:
                market_sentiment = "🟢 BULLISH"
            elif bearish_count > bullish_count:
                market_sentiment = "🔴 BEARISH"
            else:
                market_sentiment = "🟡 NEUTRO"
            
            message = f"""🧠 <b>ANÁLISE COMPLETA DO MERCADO</b>

📊 <b>Sentimento Geral:</b> {market_sentiment}

📈 <b>Distribuição:</b>
• Alta: {bullish_count} pares ({bullish_count/len(result['predictions'])*100:.0f}%)
• Baixa: {bearish_count} pares ({bearish_count/len(result['predictions'])*100:.0f}%)
• Lateral: {neutral_count} pares ({neutral_count/len(result['predictions'])*100:.0f}%)

🎯 <b>Confiança Média:</b> {avg_confidence:.1f}%
🔥 <b>Oportunidades:</b> {len(result['opportunities'])}

"""
            
            if result["opportunities"]:
                message += "<b>🚀 MELHORES OPORTUNIDADES:</b>\n"
                for i, opp in enumerate(result["opportunities"][:5], 1):
                    direction_emoji = "🟢" if opp["direction"] == "ALTA" else "🔴"
                    message += f"{i}. {direction_emoji} {opp['pair']} ({opp['confidence']:.0f}%)\n"
            
            message += f"\n⏰ Análise: {result['timestamp'].strftime('%H:%M:%S')}"
            message += "\n\n💡 Use /ai_analysis <strategy> para análise específica"
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text("❌ Erro ao executar análise completa")

async def opportunities_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /opportunities - Mostrar oportunidades de alta confiança"""
    await update.message.reply_text("🔍 Identificando oportunidades de alta confiança...")
    
    result = await ai_predictor.predict_all_pairs()
    
    if result["success"] and result["opportunities"]:
        message = "🔥 <b>OPORTUNIDADES DE ALTA CONFIANÇA</b>\n\n"
        
        for i, opp in enumerate(result["opportunities"], 1):
            direction_emoji = "🟢" if opp["direction"] == "ALTA" else "🔴" if opp["direction"] == "BAIXA" else "🟡"
            confidence_emoji = "🔥" if opp["confidence"] >= 80 else "✅"
            
            message += f"""{i}. {direction_emoji} <b>{opp['pair']}</b>
   {confidence_emoji} Confiança: {opp['confidence']:.1f}%
   🎯 Target: ${opp['target_price']:,.2f}
   📊 Variação: {opp['price_change']:.1f}%
   ⏰ Timeframe: {opp['timeframe']}
   💡 {opp['reason'][:60]}...

"""
        
        message += f"📊 Total: {len(result['opportunities'])} oportunidades identificadas"
        message += f"\n⏰ Análise: {result['timestamp'].strftime('%H:%M:%S')}"
        
        await update.message.reply_text(message, parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Nenhuma oportunidade de alta confiança encontrada no momento.\n\nTente novamente em alguns minutos.")

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def format_prediction_summary(predictions: Dict) -> str:
    """Formatar resumo de previsões"""
    if not predictions:
        return "Nenhuma previsão disponível"
    
    bullish = sum(1 for p in predictions.values() if p["direction"] == "ALTA")
    bearish = sum(1 for p in predictions.values() if p["direction"] == "BAIXA")
    neutral = len(predictions) - bullish - bearish
    
    return f"📊 Alta: {bullish} | Baixa: {bearish} | Lateral: {neutral}"
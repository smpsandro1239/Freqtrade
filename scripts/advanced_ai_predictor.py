#!/usr/bin/env python3
"""
Advanced AI Predictor - IA Preditiva Avançada e Fácil de Entender
Análise inteligente baseada em dados reais das estratégias
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from freqtrade_api_client import api_client

logger = logging.getLogger(__name__)

class AdvancedAIPredictor:
    """IA Preditiva Avançada para análise de estratégias"""
    
    def __init__(self):
        self.confidence_thresholds = {
            'very_high': 0.85,
            'high': 0.70,
            'medium': 0.55,
            'low': 0.40
        }
        
        self.trend_indicators = {
            'strong_bullish': {'emoji': '🚀', 'color': '🟢', 'action': 'COMPRAR FORTE'},
            'bullish': {'emoji': '📈', 'color': '🟢', 'action': 'COMPRAR'},
            'neutral': {'emoji': '➡️', 'color': '🟡', 'action': 'AGUARDAR'},
            'bearish': {'emoji': '📉', 'color': '🔴', 'action': 'VENDER'},
            'strong_bearish': {'emoji': '💥', 'color': '🔴', 'action': 'VENDER FORTE'}
        }
    
    def analyze_strategy_performance(self, strategy_id: str) -> Dict:
        """Análise completa de performance de uma estratégia"""
        try:
            # Obter dados da estratégia
            status_data = api_client.get_strategy_status(strategy_id)
            profit_stats = api_client.get_profit_stats(strategy_id)
            performance = api_client.get_performance(strategy_id)
            balance = api_client.get_balance(strategy_id)
            
            if not status_data.get("success") or not profit_stats.get("success"):
                return {
                    'success': False,
                    'error': 'Dados não disponíveis',
                    'strategy_id': strategy_id
                }
            
            # Métricas básicas
            total_trades = profit_stats.get("trade_count", 0)
            profit_percent = profit_stats.get("profit_closed_percent", 0)
            profit_coin = profit_stats.get("profit_closed_coin", 0)
            best_pair = profit_stats.get("best_pair", "N/A")
            avg_duration = profit_stats.get("avg_duration", "N/A")
            
            # Análise de tendência
            trend_analysis = self._analyze_trend(profit_percent, total_trades)
            
            # Análise de confiança
            confidence_analysis = self._calculate_confidence(
                profit_percent, total_trades, performance
            )
            
            # Recomendação de ação
            action_recommendation = self._get_action_recommendation(
                trend_analysis, confidence_analysis
            )
            
            # Score geral (0-100)
            overall_score = self._calculate_overall_score(
                profit_percent, total_trades, confidence_analysis['confidence']
            )
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'metrics': {
                    'total_trades': total_trades,
                    'profit_percent': profit_percent,
                    'profit_coin': profit_coin,
                    'best_pair': best_pair,
                    'avg_duration': avg_duration
                },
                'trend': trend_analysis,
                'confidence': confidence_analysis,
                'action': action_recommendation,
                'score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise da estratégia {strategy_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'strategy_id': strategy_id
            }
    
    def _analyze_trend(self, profit_percent: float, total_trades: int) -> Dict:
        """Análise de tendência baseada em performance"""
        
        # Lógica de tendência
        if profit_percent > 10 and total_trades > 20:
            trend = 'strong_bullish'
        elif profit_percent > 5 and total_trades > 10:
            trend = 'bullish'
        elif profit_percent > -2 and total_trades > 5:
            trend = 'neutral'
        elif profit_percent > -5:
            trend = 'bearish'
        else:
            trend = 'strong_bearish'
        
        trend_info = self.trend_indicators[trend]
        
        # Explicação da tendência
        explanations = {
            'strong_bullish': f"Excelente performance! {profit_percent:.1f}% de lucro com {total_trades} trades",
            'bullish': f"Boa performance. {profit_percent:.1f}% de lucro com {total_trades} trades",
            'neutral': f"Performance estável. {profit_percent:.1f}% com {total_trades} trades",
            'bearish': f"Performance negativa. {profit_percent:.1f}% com {total_trades} trades",
            'strong_bearish': f"Performance muito negativa. {profit_percent:.1f}% com {total_trades} trades"
        }
        
        return {
            'trend': trend,
            'emoji': trend_info['emoji'],
            'color': trend_info['color'],
            'action': trend_info['action'],
            'explanation': explanations[trend],
            'strength': self._calculate_trend_strength(profit_percent, total_trades)
        }
    
    def _calculate_confidence(self, profit_percent: float, total_trades: int, performance: List) -> Dict:
        """Calcular nível de confiança da análise"""
        
        base_confidence = 0.3  # Confiança base
        
        # Ajustar confiança baseada no número de trades
        if total_trades >= 50:
            trade_confidence = 0.4
        elif total_trades >= 20:
            trade_confidence = 0.3
        elif total_trades >= 10:
            trade_confidence = 0.2
        elif total_trades >= 5:
            trade_confidence = 0.1
        else:
            trade_confidence = 0.05
        
        # Ajustar confiança baseada na consistência
        consistency_confidence = 0.1
        if performance and len(performance) > 0:
            # Analisar consistência entre pares
            profits = [p.get('profit', 0) for p in performance if 'profit' in p]
            if profits:
                std_dev = np.std(profits)
                if std_dev < 2:  # Baixa volatilidade = mais consistente
                    consistency_confidence = 0.2
                elif std_dev < 5:
                    consistency_confidence = 0.15
        
        # Ajustar confiança baseada na magnitude do lucro
        profit_confidence = min(0.3, abs(profit_percent) / 100)
        
        # Confiança total
        total_confidence = min(0.95, base_confidence + trade_confidence + consistency_confidence + profit_confidence)
        
        # Determinar nível
        if total_confidence >= self.confidence_thresholds['very_high']:
            level = 'MUITO ALTA'
            emoji = '🟢'
        elif total_confidence >= self.confidence_thresholds['high']:
            level = 'ALTA'
            emoji = '🟢'
        elif total_confidence >= self.confidence_thresholds['medium']:
            level = 'MÉDIA'
            emoji = '🟡'
        else:
            level = 'BAIXA'
            emoji = '🔴'
        
        return {
            'confidence': total_confidence,
            'level': level,
            'emoji': emoji,
            'factors': {
                'trades': f"{total_trades} trades (peso: {trade_confidence:.2f})",
                'consistency': f"Consistência (peso: {consistency_confidence:.2f})",
                'magnitude': f"Magnitude {profit_percent:.1f}% (peso: {profit_confidence:.2f})"
            }
        }
    
    def _get_action_recommendation(self, trend_analysis: Dict, confidence_analysis: Dict) -> Dict:
        """Gerar recomendação de ação"""
        
        trend = trend_analysis['trend']
        confidence = confidence_analysis['confidence']
        
        # Recomendações baseadas em tendência e confiança
        if trend in ['strong_bullish', 'bullish'] and confidence > 0.7:
            action = 'AUMENTAR_POSICAO'
            priority = 'ALTA'
            explanation = "Tendência positiva com alta confiança - considere aumentar exposição"
            risk_level = 'BAIXO' if trend == 'strong_bullish' else 'MÉDIO'
        
        elif trend == 'neutral' and confidence > 0.6:
            action = 'MANTER_POSICAO'
            priority = 'MÉDIA'
            explanation = "Performance estável - manter posições atuais"
            risk_level = 'MÉDIO'
        
        elif trend in ['bearish', 'strong_bearish'] and confidence > 0.6:
            action = 'REDUZIR_POSICAO'
            priority = 'ALTA'
            explanation = "Tendência negativa - considere reduzir exposição"
            risk_level = 'ALTO'
        
        else:
            action = 'AGUARDAR'
            priority = 'BAIXA'
            explanation = "Dados insuficientes ou baixa confiança - aguardar mais informações"
            risk_level = 'MÉDIO'
        
        return {
            'action': action,
            'priority': priority,
            'explanation': explanation,
            'risk_level': risk_level,
            'confidence_required': confidence,
            'next_review': (datetime.now() + timedelta(hours=4)).strftime('%H:%M')
        }
    
    def _calculate_overall_score(self, profit_percent: float, total_trades: int, confidence: float) -> Dict:
        """Calcular score geral da estratégia (0-100)"""
        
        # Score baseado em lucro (0-40 pontos)
        if profit_percent > 10:
            profit_score = 40
        elif profit_percent > 5:
            profit_score = 30
        elif profit_percent > 0:
            profit_score = 20
        elif profit_percent > -5:
            profit_score = 10
        else:
            profit_score = 0
        
        # Score baseado em atividade (0-30 pontos)
        if total_trades > 50:
            activity_score = 30
        elif total_trades > 20:
            activity_score = 25
        elif total_trades > 10:
            activity_score = 20
        elif total_trades > 5:
            activity_score = 15
        else:
            activity_score = max(0, total_trades * 2)
        
        # Score baseado em confiança (0-30 pontos)
        confidence_score = confidence * 30
        
        total_score = profit_score + activity_score + confidence_score
        
        # Classificação
        if total_score >= 80:
            grade = 'A+'
            emoji = '🏆'
            description = 'EXCELENTE'
        elif total_score >= 70:
            grade = 'A'
            emoji = '🥇'
            description = 'MUITO BOM'
        elif total_score >= 60:
            grade = 'B'
            emoji = '🥈'
            description = 'BOM'
        elif total_score >= 50:
            grade = 'C'
            emoji = '🥉'
            description = 'REGULAR'
        else:
            grade = 'D'
            emoji = '⚠️'
            description = 'PRECISA MELHORAR'
        
        return {
            'total': round(total_score, 1),
            'grade': grade,
            'emoji': emoji,
            'description': description,
            'breakdown': {
                'profit': profit_score,
                'activity': activity_score,
                'confidence': round(confidence_score, 1)
            }
        }
    
    def _calculate_trend_strength(self, profit_percent: float, total_trades: int) -> float:
        """Calcular força da tendência (0-1)"""
        
        # Força baseada na magnitude do lucro
        profit_strength = min(1.0, abs(profit_percent) / 20)
        
        # Força baseada no número de trades
        trade_strength = min(1.0, total_trades / 50)
        
        # Força combinada
        return (profit_strength + trade_strength) / 2
    
    def generate_market_overview(self) -> Dict:
        """Gerar visão geral do mercado com todas as estratégias"""
        
        overview = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'strategies': {},
            'market_sentiment': {},
            'recommendations': [],
            'alerts': []
        }
        
        all_scores = []
        all_profits = []
        high_confidence_signals = []
        
        # Analisar cada estratégia
        for strategy_id, strategy_info in api_client.strategies.items():
            analysis = self.analyze_strategy_performance(strategy_id)
            
            if analysis.get('success'):
                overview['strategies'][strategy_id] = analysis
                all_scores.append(analysis['score']['total'])
                all_profits.append(analysis['metrics']['profit_percent'])
                
                # Coletar sinais de alta confiança
                if analysis['confidence']['confidence'] > 0.7:
                    high_confidence_signals.append({
                        'strategy': strategy_info['name'],
                        'action': analysis['action']['action'],
                        'confidence': analysis['confidence']['confidence'],
                        'trend': analysis['trend']['trend']
                    })
        
        # Calcular sentimento geral do mercado
        if all_scores:
            avg_score = np.mean(all_scores)
            avg_profit = np.mean(all_profits)
            
            if avg_score > 70 and avg_profit > 3:
                market_sentiment = 'MUITO_POSITIVO'
                sentiment_emoji = '🚀'
                sentiment_desc = 'Mercado muito favorável'
            elif avg_score > 60 and avg_profit > 1:
                market_sentiment = 'POSITIVO'
                sentiment_emoji = '📈'
                sentiment_desc = 'Mercado favorável'
            elif avg_score > 50:
                market_sentiment = 'NEUTRO'
                sentiment_emoji = '➡️'
                sentiment_desc = 'Mercado estável'
            elif avg_score > 40:
                market_sentiment = 'NEGATIVO'
                sentiment_emoji = '📉'
                sentiment_desc = 'Mercado desfavorável'
            else:
                market_sentiment = 'MUITO_NEGATIVO'
                sentiment_emoji = '💥'
                sentiment_desc = 'Mercado muito desfavorável'
            
            overview['market_sentiment'] = {
                'sentiment': market_sentiment,
                'emoji': sentiment_emoji,
                'description': sentiment_desc,
                'avg_score': round(avg_score, 1),
                'avg_profit': round(avg_profit, 2),
                'active_strategies': len([s for s in overview['strategies'].values() if s.get('success')])
            }
        
        # Gerar recomendações gerais
        overview['recommendations'] = self._generate_general_recommendations(high_confidence_signals, overview['market_sentiment'])
        
        # Gerar alertas
        overview['alerts'] = self._generate_alerts(overview['strategies'])
        
        return overview
    
    def _generate_general_recommendations(self, high_confidence_signals: List, market_sentiment: Dict) -> List:
        """Gerar recomendações gerais"""
        recommendations = []
        
        if market_sentiment.get('sentiment') == 'MUITO_POSITIVO':
            recommendations.append({
                'type': 'OPORTUNIDADE',
                'emoji': '🚀',
                'title': 'Mercado Muito Favorável',
                'description': 'Considere aumentar exposição nas estratégias de melhor performance'
            })
        
        elif market_sentiment.get('sentiment') == 'MUITO_NEGATIVO':
            recommendations.append({
                'type': 'ALERTA',
                'emoji': '⚠️',
                'title': 'Mercado Desfavorável',
                'description': 'Considere reduzir exposição e revisar configurações'
            })
        
        if len(high_confidence_signals) > 3:
            recommendations.append({
                'type': 'ACAO',
                'emoji': '🎯',
                'title': 'Múltiplos Sinais de Alta Confiança',
                'description': f'{len(high_confidence_signals)} estratégias com sinais confiáveis'
            })
        
        return recommendations
    
    def _generate_alerts(self, strategies: Dict) -> List:
        """Gerar alertas importantes"""
        alerts = []
        
        for strategy_id, analysis in strategies.items():
            if not analysis.get('success'):
                continue
            
            # Alerta de performance muito negativa
            if analysis['metrics']['profit_percent'] < -10:
                alerts.append({
                    'type': 'CRITICO',
                    'emoji': '🚨',
                    'strategy': api_client.strategies[strategy_id]['name'],
                    'message': f"Perda significativa: {analysis['metrics']['profit_percent']:.1f}%"
                })
            
            # Alerta de alta performance
            elif analysis['metrics']['profit_percent'] > 15:
                alerts.append({
                    'type': 'SUCESSO',
                    'emoji': '🎉',
                    'strategy': api_client.strategies[strategy_id]['name'],
                    'message': f"Excelente performance: {analysis['metrics']['profit_percent']:.1f}%"
                })
            
            # Alerta de baixa atividade
            elif analysis['metrics']['total_trades'] < 3:
                alerts.append({
                    'type': 'AVISO',
                    'emoji': '⏰',
                    'strategy': api_client.strategies[strategy_id]['name'],
                    'message': f"Baixa atividade: apenas {analysis['metrics']['total_trades']} trades"
                })
        
        return alerts

# Instância global do preditor
ai_predictor = AdvancedAIPredictor()
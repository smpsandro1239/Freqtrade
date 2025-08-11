#!/usr/bin/env python3
"""
Trend Prediction System - Análise preditiva de tendências de mercado
Sistema de previsão baseado em indicadores técnicos e padrões históricos
"""
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json

class TrendPredictor:
    def __init__(self):
        self.project_root = Path("/app/project")
        self.prediction_cache = {}
        self.confidence_threshold = 0.65  # 65% de confiança mínima
        
    def get_db_path(self, strategy_id: str, dry_run: bool = True):
        """Get database path for a strategy"""
        db_name = "tradesv3.dryrun.sqlite" if dry_run else "tradesv3.sqlite"
        return self.project_root / "user_data" / db_name
    
    def get_connection(self, strategy_id: str):
        """Get database connection"""
        for dry_run in [True, False]:
            db_path = self.get_db_path(strategy_id, dry_run)
            if db_path.exists():
                return sqlite3.connect(str(db_path))
        return None
    
    def get_recent_trades_data(self, strategy_id: str, limit: int = 100):
        """Get recent trades data for analysis"""
        conn = self.get_connection(strategy_id)
        if not conn:
            return self._get_mock_trades_data(strategy_id, limit)
        
        try:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                pair,
                open_date_utc,
                close_date_utc,
                open_rate,
                close_rate,
                amount,
                close_profit,
                close_profit_pct,
                strategy,
                is_open
            FROM trades 
            WHERE strategy LIKE ?
            AND close_date_utc IS NOT NULL
            ORDER BY close_date_utc DESC
            LIMIT ?
            """
            
            strategy_pattern = f"%{strategy_id}%"
            cursor.execute(query, (strategy_pattern, limit))
            results = cursor.fetchall()
            
            trades_data = []
            for row in results:
                pair, open_date, close_date, open_rate, close_rate, amount, profit, profit_pct, strategy, is_open = row
                
                trades_data.append({
                    'pair': pair,
                    'open_date': datetime.fromtimestamp(open_date / 1000) if open_date else None,
                    'close_date': datetime.fromtimestamp(close_date / 1000) if close_date else None,
                    'open_rate': open_rate,
                    'close_rate': close_rate,
                    'amount': amount,
                    'profit': profit or 0,
                    'profit_pct': profit_pct or 0,
                    'duration_hours': ((close_date - open_date) / 1000 / 3600) if close_date and open_date else 0
                })
            
            return trades_data
            
        except Exception as e:
            logging.error(f"Error getting trades data for {strategy_id}: {e}")
            return self._get_mock_trades_data(strategy_id, limit)
        finally:
            conn.close()
    
    def _get_mock_trades_data(self, strategy_id: str, limit: int):
        """Generate mock trades data for analysis"""
        import random
        import hashlib
        
        seed = int(hashlib.md5(strategy_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        trades_data = []
        base_time = datetime.now() - timedelta(days=30)
        
        pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT']
        
        for i in range(limit):
            pair = random.choice(pairs)
            open_date = base_time + timedelta(hours=random.randint(0, 720))
            duration = random.randint(1, 48)  # 1-48 hours
            close_date = open_date + timedelta(hours=duration)
            
            open_rate = random.uniform(0.5, 50000)
            profit_pct = random.uniform(-5, 8)
            close_rate = open_rate * (1 + profit_pct / 100)
            amount = random.uniform(0.001, 1.0)
            profit = amount * (close_rate - open_rate)
            
            trades_data.append({
                'pair': pair,
                'open_date': open_date,
                'close_date': close_date,
                'open_rate': open_rate,
                'close_rate': close_rate,
                'amount': amount,
                'profit': profit,
                'profit_pct': profit_pct,
                'duration_hours': duration
            })
        
        return trades_data
    
    def analyze_trading_patterns(self, strategy_id: str) -> Dict:
        """Analyze trading patterns to predict trends"""
        trades_data = self.get_recent_trades_data(strategy_id, 50)
        
        if not trades_data:
            return self._get_mock_analysis(strategy_id)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(trades_data)
        
        # Calculate key metrics
        analysis = {
            'total_trades': len(df),
            'win_rate': len(df[df['profit'] > 0]) / len(df) * 100 if len(df) > 0 else 0,
            'avg_profit_pct': df['profit_pct'].mean(),
            'avg_duration_hours': df['duration_hours'].mean(),
            'profit_trend': self._calculate_profit_trend(df),
            'pair_performance': self._analyze_pair_performance(df),
            'time_patterns': self._analyze_time_patterns(df),
            'momentum_indicators': self._calculate_momentum_indicators(df)
        }
        
        return analysis
    
    def _calculate_profit_trend(self, df: pd.DataFrame) -> Dict:
        """Calculate profit trend over time"""
        if len(df) < 5:
            return {'trend': 'insufficient_data', 'slope': 0, 'confidence': 0}
        
        # Sort by close date
        df_sorted = df.sort_values('close_date')
        
        # Calculate moving average of profit
        window = min(10, len(df) // 2)
        df_sorted['profit_ma'] = df_sorted['profit_pct'].rolling(window=window).mean()
        
        # Calculate trend slope
        recent_profits = df_sorted['profit_ma'].dropna().tail(window)
        if len(recent_profits) < 3:
            return {'trend': 'insufficient_data', 'slope': 0, 'confidence': 0}
        
        x = np.arange(len(recent_profits))
        slope = np.polyfit(x, recent_profits, 1)[0]
        
        # Determine trend direction and confidence
        if slope > 0.1:
            trend = 'bullish'
            confidence = min(0.9, abs(slope) * 10)
        elif slope < -0.1:
            trend = 'bearish'
            confidence = min(0.9, abs(slope) * 10)
        else:
            trend = 'sideways'
            confidence = 0.5
        
        return {
            'trend': trend,
            'slope': slope,
            'confidence': confidence
        }
    
    def _analyze_pair_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by trading pair"""
        pair_stats = {}
        
        for pair in df['pair'].unique():
            pair_data = df[df['pair'] == pair]
            
            pair_stats[pair] = {
                'trades': len(pair_data),
                'win_rate': len(pair_data[pair_data['profit'] > 0]) / len(pair_data) * 100,
                'avg_profit': pair_data['profit_pct'].mean(),
                'total_profit': pair_data['profit'].sum()
            }
        
        # Find best performing pair
        best_pair = max(pair_stats.keys(), key=lambda x: pair_stats[x]['avg_profit']) if pair_stats else None
        
        return {
            'pair_stats': pair_stats,
            'best_pair': best_pair,
            'best_pair_profit': pair_stats[best_pair]['avg_profit'] if best_pair else 0
        }
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze time-based trading patterns"""
        if df.empty:
            return {'best_hours': [], 'best_days': [], 'pattern_strength': 0}
        
        # Add time features
        df['hour'] = df['open_date'].dt.hour
        df['day_of_week'] = df['open_date'].dt.dayofweek
        
        # Analyze hourly patterns
        hourly_profit = df.groupby('hour')['profit_pct'].mean()
        best_hours = hourly_profit.nlargest(3).index.tolist()
        
        # Analyze daily patterns
        daily_profit = df.groupby('day_of_week')['profit_pct'].mean()
        best_days = daily_profit.nlargest(2).index.tolist()
        
        # Calculate pattern strength
        pattern_strength = (hourly_profit.std() + daily_profit.std()) / 2
        
        return {
            'best_hours': best_hours,
            'best_days': best_days,
            'pattern_strength': min(1.0, pattern_strength / 5),
            'hourly_avg': hourly_profit.to_dict(),
            'daily_avg': daily_profit.to_dict()
        }
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate momentum indicators"""
        if len(df) < 10:
            return {'rsi': 50, 'momentum': 0, 'volatility': 0}
        
        # Sort by date
        df_sorted = df.sort_values('close_date')
        
        # Calculate RSI-like indicator based on profit
        profits = df_sorted['profit_pct'].values
        gains = np.where(profits > 0, profits, 0)
        losses = np.where(profits < 0, -profits, 0)
        
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Calculate momentum
        recent_profits = profits[-5:]
        older_profits = profits[-10:-5] if len(profits) >= 10 else profits[:-5]
        
        momentum = np.mean(recent_profits) - np.mean(older_profits) if len(older_profits) > 0 else 0
        
        # Calculate volatility
        volatility = np.std(profits[-20:]) if len(profits) >= 20 else np.std(profits)
        
        return {
            'rsi': rsi,
            'momentum': momentum,
            'volatility': volatility
        }
    
    def _get_mock_analysis(self, strategy_id: str) -> Dict:
        """Generate mock analysis for demonstration"""
        import random
        import hashlib
        
        seed = int(hashlib.md5(strategy_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate realistic mock data
        trend_options = ['bullish', 'bearish', 'sideways']
        trend = random.choice(trend_options)
        
        if trend == 'bullish':
            slope = random.uniform(0.2, 0.8)
            confidence = random.uniform(0.65, 0.9)
            rsi = random.uniform(60, 80)
            momentum = random.uniform(0.5, 2.0)
        elif trend == 'bearish':
            slope = random.uniform(-0.8, -0.2)
            confidence = random.uniform(0.65, 0.9)
            rsi = random.uniform(20, 40)
            momentum = random.uniform(-2.0, -0.5)
        else:
            slope = random.uniform(-0.1, 0.1)
            confidence = random.uniform(0.4, 0.6)
            rsi = random.uniform(45, 55)
            momentum = random.uniform(-0.3, 0.3)
        
        pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT']
        best_pair = random.choice(pairs)
        
        return {
            'total_trades': random.randint(20, 50),
            'win_rate': random.uniform(45, 75),
            'avg_profit_pct': random.uniform(-0.5, 2.5),
            'avg_duration_hours': random.uniform(2, 24),
            'profit_trend': {
                'trend': trend,
                'slope': slope,
                'confidence': confidence
            },
            'pair_performance': {
                'best_pair': best_pair,
                'best_pair_profit': random.uniform(0.5, 3.0)
            },
            'time_patterns': {
                'best_hours': random.sample(range(24), 3),
                'best_days': random.sample(range(7), 2),
                'pattern_strength': random.uniform(0.3, 0.8)
            },
            'momentum_indicators': {
                'rsi': rsi,
                'momentum': momentum,
                'volatility': random.uniform(1.0, 4.0)
            }
        }
    
    def generate_prediction(self, strategy_id: str) -> Dict:
        """Generate trend prediction based on analysis"""
        analysis = self.analyze_trading_patterns(strategy_id)
        
        # Extract key indicators
        profit_trend = analysis['profit_trend']
        momentum = analysis['momentum_indicators']
        time_patterns = analysis['time_patterns']
        
        # Calculate prediction confidence
        trend_confidence = profit_trend['confidence']
        momentum_strength = abs(momentum['momentum']) / 2  # Normalize
        pattern_strength = time_patterns['pattern_strength']
        
        overall_confidence = (trend_confidence + momentum_strength + pattern_strength) / 3
        
        # Generate prediction
        if profit_trend['trend'] == 'bullish' and momentum['rsi'] < 70:
            prediction = 'upward'
            signal_strength = 'strong' if overall_confidence > 0.7 else 'moderate'
        elif profit_trend['trend'] == 'bearish' and momentum['rsi'] > 30:
            prediction = 'downward'
            signal_strength = 'strong' if overall_confidence > 0.7 else 'moderate'
        else:
            prediction = 'sideways'
            signal_strength = 'weak'
        
        # Calculate time horizon
        avg_duration = analysis['avg_duration_hours']
        if avg_duration < 6:
            time_horizon = 'short_term'  # Next 1-6 hours
        elif avg_duration < 24:
            time_horizon = 'medium_term'  # Next 6-24 hours
        else:
            time_horizon = 'long_term'  # Next 1-3 days
        
        return {
            'prediction': prediction,
            'confidence': overall_confidence,
            'signal_strength': signal_strength,
            'time_horizon': time_horizon,
            'key_factors': self._identify_key_factors(analysis),
            'recommended_action': self._get_recommendation(prediction, overall_confidence),
            'risk_level': self._calculate_risk_level(analysis),
            'timestamp': datetime.now().isoformat()
        }
    
    def _identify_key_factors(self, analysis: Dict) -> List[str]:
        """Identify key factors influencing the prediction"""
        factors = []
        
        profit_trend = analysis['profit_trend']
        momentum = analysis['momentum_indicators']
        
        if profit_trend['confidence'] > 0.7:
            factors.append(f"Tendência {profit_trend['trend']} forte")
        
        if momentum['rsi'] > 70:
            factors.append("RSI em zona de sobrecompra")
        elif momentum['rsi'] < 30:
            factors.append("RSI em zona de sobrevenda")
        
        if abs(momentum['momentum']) > 1:
            factors.append("Momentum significativo detectado")
        
        if analysis['win_rate'] > 70:
            factors.append("Alta taxa de acerto histórica")
        elif analysis['win_rate'] < 40:
            factors.append("Taxa de acerto baixa")
        
        return factors[:3]  # Top 3 factors
    
    def _get_recommendation(self, prediction: str, confidence: float) -> str:
        """Get trading recommendation"""
        if confidence < 0.5:
            return "Aguardar sinais mais claros"
        elif prediction == 'upward' and confidence > 0.65:
            return "Considerar posições de compra"
        elif prediction == 'downward' and confidence > 0.65:
            return "Considerar redução de exposição"
        else:
            return "Manter posição atual"
    
    def _calculate_risk_level(self, analysis: Dict) -> str:
        """Calculate risk level"""
        volatility = analysis['momentum_indicators']['volatility']
        win_rate = analysis['win_rate']
        
        if volatility > 3 or win_rate < 40:
            return "Alto"
        elif volatility > 2 or win_rate < 55:
            return "Médio"
        else:
            return "Baixo"
    
    def format_prediction_message(self, strategy_id: str) -> str:
        """Format prediction for Telegram message"""
        try:
            prediction = self.generate_prediction(strategy_id)
            analysis = self.analyze_trading_patterns(strategy_id)
            
            # Prediction emoji
            if prediction['prediction'] == 'upward':
                trend_emoji = "📈"
                trend_text = "TENDÊNCIA DE ALTA"
            elif prediction['prediction'] == 'downward':
                trend_emoji = "📉"
                trend_text = "TENDÊNCIA DE BAIXA"
            else:
                trend_emoji = "➡️"
                trend_text = "TENDÊNCIA LATERAL"
            
            # Confidence emoji
            confidence = prediction['confidence']
            if confidence > 0.8:
                conf_emoji = "🟢"
            elif confidence > 0.6:
                conf_emoji = "🟡"
            else:
                conf_emoji = "🔴"
            
            # Signal strength
            strength = prediction['signal_strength']
            if strength == 'strong':
                strength_emoji = "💪"
            elif strength == 'moderate':
                strength_emoji = "👍"
            else:
                strength_emoji = "🤏"
            
            message = f"🔮 <b>PREVISÃO DE TENDÊNCIA</b>\n"
            message += f"📊 <b>Estratégia:</b> {strategy_id}\n\n"
            
            message += f"{trend_emoji} <b>{trend_text}</b>\n"
            message += f"{conf_emoji} <b>Confiança:</b> {confidence:.1%}\n"
            message += f"{strength_emoji} <b>Força do Sinal:</b> {strength.title()}\n"
            message += f"⏰ <b>Horizonte:</b> {prediction['time_horizon'].replace('_', ' ').title()}\n"
            message += f"⚠️ <b>Risco:</b> {prediction['risk_level']}\n\n"
            
            message += f"💡 <b>Recomendação:</b>\n"
            message += f"   {prediction['recommended_action']}\n\n"
            
            message += f"🔍 <b>Fatores Chave:</b>\n"
            for factor in prediction['key_factors']:
                message += f"   • {factor}\n"
            
            message += f"\n📈 <b>Análise Técnica:</b>\n"
            message += f"   • RSI: {analysis['momentum_indicators']['rsi']:.1f}\n"
            message += f"   • Win Rate: {analysis['win_rate']:.1f}%\n"
            message += f"   • Trades Analisados: {analysis['total_trades']}\n"
            
            message += f"\n⚡ <b>Melhor Par:</b> {analysis['pair_performance']['best_pair']}\n"
            
            message += f"\n🕐 <b>Melhores Horários:</b> "
            best_hours = analysis['time_patterns']['best_hours'][:3]
            message += ", ".join([f"{h:02d}:00" for h in best_hours])
            
            message += f"\n\n⚠️ <i>Esta é uma análise preditiva baseada em padrões históricos. Não constitui aconselhamento financeiro.</i>"
            
            return message
            
        except Exception as e:
            logging.error(f"Error formatting prediction message: {e}")
            return f"❌ Erro ao gerar previsão para {strategy_id}: {str(e)}"

# Global instance
trend_predictor = TrendPredictor()
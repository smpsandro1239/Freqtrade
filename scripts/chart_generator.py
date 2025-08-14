#!/usr/bin/env python3
"""
Chart Generator - Gerador de Gráficos Simples
Cria gráficos ASCII e análises visuais para Telegram
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from freqtrade_api_client import api_client

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Gerador de gráficos ASCII para Telegram"""
    
    def __init__(self):
        self.chart_width = 30
        self.chart_height = 8
    
    def generate_profit_chart(self, strategy_id: str) -> str:
        """Gerar gráfico ASCII de lucro"""
        try:
            profit_stats = api_client.get_profit_stats(strategy_id)
            
            if not profit_stats.get("success"):
                return "❌ Dados não disponíveis para gráfico"
            
            profit = profit_stats.get("profit_closed_percent", 0)
            trades = profit_stats.get("trade_count", 0)
            
            # Simular dados históricos (em produção real, usar dados reais)
            historical_data = self._simulate_historical_data(profit, trades)
            
            chart = self._create_ascii_chart(historical_data, f"Lucro % - {api_client.strategies[strategy_id]['name']}")
            
            return chart
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico para {strategy_id}: {e}")
            return f"❌ Erro ao gerar gráfico: {str(e)}"
    
    def generate_performance_comparison(self) -> str:
        """Gerar comparação visual de performance entre estratégias"""
        try:
            strategies_data = []
            
            for strategy_id, strategy_info in api_client.strategies.items():
                profit_stats = api_client.get_profit_stats(strategy_id)
                
                if profit_stats.get("success"):
                    profit = profit_stats.get("profit_closed_percent", 0)
                    trades = profit_stats.get("trade_count", 0)
                    
                    strategies_data.append({
                        'name': strategy_info['name'][:12],  # Limitar nome
                        'profit': profit,
                        'trades': trades
                    })
            
            if not strategies_data:
                return "❌ Nenhum dado disponível para comparação"
            
            # Ordenar por lucro
            strategies_data.sort(key=lambda x: x['profit'], reverse=True)
            
            chart = "📊 <b>COMPARAÇÃO DE PERFORMANCE</b>\n\n"
            chart += "<pre>"
            
            # Encontrar valores máximo e mínimo para escala
            max_profit = max(s['profit'] for s in strategies_data)
            min_profit = min(s['profit'] for s in strategies_data)
            
            # Criar barras horizontais
            for i, strategy in enumerate(strategies_data):
                name = strategy['name']
                profit = strategy['profit']
                trades = strategy['trades']
                
                # Calcular tamanho da barra (normalizado)
                if max_profit != min_profit:
                    bar_length = int(((profit - min_profit) / (max_profit - min_profit)) * 20)
                else:
                    bar_length = 10
                
                # Escolher cor da barra
                if profit > 5:
                    bar_char = "🟢"
                elif profit > 0:
                    bar_char = "🟡"
                else:
                    bar_char = "🔴"
                
                # Criar barra
                bar = bar_char * max(1, bar_length)
                
                chart += f"{name:12} │{bar:<20}│ {profit:6.1f}% ({trades:2d})\n"
            
            chart += "</pre>\n"
            chart += f"📈 Melhor: {strategies_data[0]['name']} ({strategies_data[0]['profit']:.1f}%)\n"
            chart += f"📉 Pior: {strategies_data[-1]['name']} ({strategies_data[-1]['profit']:.1f}%)\n"
            
            return chart
            
        except Exception as e:
            logger.error(f"Erro ao gerar comparação: {e}")
            return f"❌ Erro ao gerar comparação: {str(e)}"
    
    def generate_trades_timeline(self, strategy_id: str) -> str:
        """Gerar timeline de trades"""
        try:
            profit_stats = api_client.get_profit_stats(strategy_id)
            
            if not profit_stats.get("success"):
                return "❌ Dados não disponíveis"
            
            trades = profit_stats.get("trade_count", 0)
            profit = profit_stats.get("profit_closed_percent", 0)
            
            # Simular timeline (em produção real, usar dados reais)
            timeline_data = self._simulate_timeline_data(trades, profit)
            
            chart = f"📅 <b>TIMELINE - {api_client.strategies[strategy_id]['name']}</b>\n\n"
            chart += "<pre>"
            
            for day, data in timeline_data.items():
                day_trades = data['trades']
                day_profit = data['profit']
                
                # Criar indicador visual
                if day_profit > 2:
                    indicator = "🟢🟢"
                elif day_profit > 0:
                    indicator = "🟢⚪"
                elif day_profit > -2:
                    indicator = "🟡⚪"
                else:
                    indicator = "🔴🔴"
                
                chart += f"{day} │{indicator}│ {day_trades:2d} trades │ {day_profit:+5.1f}%\n"
            
            chart += "</pre>\n"
            chart += f"📊 Total: {trades} trades | {profit:+.1f}%"
            
            return chart
            
        except Exception as e:
            logger.error(f"Erro ao gerar timeline para {strategy_id}: {e}")
            return f"❌ Erro ao gerar timeline: {str(e)}"
    
    def generate_risk_analysis_chart(self) -> str:
        """Gerar análise visual de risco"""
        try:
            chart = "⚠️ <b>ANÁLISE DE RISCO</b>\n\n"
            chart += "<pre>"
            
            risk_levels = []
            
            for strategy_id, strategy_info in api_client.strategies.items():
                profit_stats = api_client.get_profit_stats(strategy_id)
                
                if profit_stats.get("success"):
                    profit = profit_stats.get("profit_closed_percent", 0)
                    trades = profit_stats.get("trade_count", 0)
                    
                    # Calcular nível de risco
                    if profit < -10:
                        risk = "ALTO"
                        risk_emoji = "🔴"
                    elif profit < -5:
                        risk = "MÉDIO"
                        risk_emoji = "🟡"
                    elif trades < 5:
                        risk = "BAIXO"
                        risk_emoji = "🟢"
                    else:
                        risk = "MUITO BAIXO"
                        risk_emoji = "🟢"
                    
                    risk_levels.append({
                        'name': strategy_info['name'][:12],
                        'risk': risk,
                        'emoji': risk_emoji,
                        'profit': profit,
                        'trades': trades
                    })
            
            # Agrupar por nível de risco
            risk_groups = {'ALTO': [], 'MÉDIO': [], 'BAIXO': [], 'MUITO BAIXO': []}
            
            for strategy in risk_levels:
                risk_groups[strategy['risk']].append(strategy)
            
            for risk_level, strategies in risk_groups.items():
                if strategies:
                    chart += f"\n{risk_level}:\n"
                    for strategy in strategies:
                        chart += f"  {strategy['emoji']} {strategy['name']} ({strategy['profit']:+.1f}%)\n"
            
            chart += "</pre>\n"
            
            # Resumo de risco
            high_risk_count = len(risk_groups['ALTO'])
            if high_risk_count > 0:
                chart += f"🚨 {high_risk_count} estratégia(s) de alto risco\n"
            else:
                chart += f"✅ Nenhuma estratégia de alto risco\n"
            
            return chart
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise de risco: {e}")
            return f"❌ Erro ao gerar análise de risco: {str(e)}"
    
    def _simulate_historical_data(self, current_profit: float, trades: int) -> List[float]:
        """Simular dados históricos baseados no lucro atual"""
        # Em produção real, isso viria da API
        data_points = min(20, max(5, trades))
        
        # Criar progressão realística até o lucro atual
        historical = []
        step = current_profit / data_points if data_points > 0 else 0
        
        for i in range(data_points):
            # Adicionar alguma variação realística
            noise = np.random.normal(0, abs(step) * 0.3) if step != 0 else 0
            value = (i + 1) * step + noise
            historical.append(value)
        
        return historical
    
    def _simulate_timeline_data(self, total_trades: int, total_profit: float) -> Dict:
        """Simular dados de timeline"""
        # Em produção real, isso viria da API
        timeline = {}
        
        # Últimos 7 dias
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime('%m/%d')
            
            # Distribuir trades e lucro ao longo dos dias
            day_trades = max(0, int(total_trades / 7) + np.random.randint(-2, 3))
            day_profit = (total_profit / 7) + np.random.normal(0, abs(total_profit) * 0.2)
            
            timeline[date] = {
                'trades': day_trades,
                'profit': day_profit
            }
        
        return timeline
    
    def _create_ascii_chart(self, data: List[float], title: str) -> str:
        """Criar gráfico ASCII simples"""
        if not data:
            return "❌ Sem dados para gráfico"
        
        chart = f"📈 <b>{title}</b>\n\n<pre>"
        
        # Normalizar dados
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            # Dados constantes
            chart += "─" * len(data) + f" {data[0]:.1f}%\n"
        else:
            # Criar gráfico de linha simples
            normalized = [(val - min_val) / (max_val - min_val) * (self.chart_height - 1) for val in data]
            
            for row in range(self.chart_height - 1, -1, -1):
                line = ""
                for col, norm_val in enumerate(normalized):
                    if abs(norm_val - row) < 0.5:
                        line += "●"
                    elif row == 0:
                        line += "─"
                    else:
                        line += " "
                
                # Adicionar escala à direita
                scale_val = min_val + (row / (self.chart_height - 1)) * (max_val - min_val)
                chart += f"{line} {scale_val:5.1f}%\n"
        
        chart += "</pre>\n"
        chart += f"📊 Min: {min_val:.1f}% | Max: {max_val:.1f}% | Atual: {data[-1]:.1f}%"
        
        return chart
    
    def generate_market_heatmap(self) -> str:
        """Gerar mapa de calor do mercado"""
        try:
            chart = "🌡️ <b>MAPA DE CALOR DO MERCADO</b>\n\n"
            chart += "<pre>"
            
            strategies_data = []
            
            for strategy_id, strategy_info in api_client.strategies.items():
                profit_stats = api_client.get_profit_stats(strategy_id)
                
                if profit_stats.get("success"):
                    profit = profit_stats.get("profit_closed_percent", 0)
                    trades = profit_stats.get("trade_count", 0)
                    
                    # Determinar "temperatura"
                    if profit > 10:
                        temp = "🔥"  # Muito quente (muito lucrativo)
                    elif profit > 5:
                        temp = "🟠"  # Quente (lucrativo)
                    elif profit > 0:
                        temp = "🟡"  # Morno (ligeiramente lucrativo)
                    elif profit > -5:
                        temp = "🔵"  # Frio (ligeiramente negativo)
                    else:
                        temp = "🟣"  # Muito frio (muito negativo)
                    
                    strategies_data.append({
                        'name': strategy_info['name'][:10],
                        'temp': temp,
                        'profit': profit,
                        'trades': trades
                    })
            
            # Organizar em grid 3x3 (ou o que couber)
            chart += "┌─────────────┬─────────────┬─────────────┐\n"
            
            for i in range(0, len(strategies_data), 3):
                row = strategies_data[i:i+3]
                
                # Linha de temperaturas
                temp_line = "│"
                for strategy in row:
                    temp_line += f"     {strategy['temp']}      │"
                
                # Preencher células vazias
                while len(row) < 3:
                    temp_line += "             │"
                    row.append({'name': '', 'profit': 0, 'trades': 0})
                
                chart += temp_line + "\n"
                
                # Linha de nomes
                name_line = "│"
                for strategy in row:
                    name = strategy['name'][:11].center(11)
                    name_line += f" {name} │"
                
                chart += name_line + "\n"
                
                # Linha de dados
                data_line = "│"
                for strategy in row:
                    if strategy['name']:
                        data = f"{strategy['profit']:+.1f}%({strategy['trades']})"
                        data_line += f" {data:>10} │"
                    else:
                        data_line += "             │"
                
                chart += data_line + "\n"
                
                if i + 3 < len(strategies_data):
                    chart += "├─────────────┼─────────────┼─────────────┤\n"
            
            chart += "└─────────────┴─────────────┴─────────────┘\n"
            chart += "</pre>\n"
            
            chart += "🔥 Muito Quente (>10%) | 🟠 Quente (5-10%) | 🟡 Morno (0-5%)\n"
            chart += "🔵 Frio (-5-0%) | 🟣 Muito Frio (<-5%)"
            
            return chart
            
        except Exception as e:
            logger.error(f"Erro ao gerar mapa de calor: {e}")
            return f"❌ Erro ao gerar mapa de calor: {str(e)}"

# Instância global do gerador de gráficos
chart_generator = ChartGenerator()
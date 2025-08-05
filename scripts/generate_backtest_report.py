#!/usr/bin/env python3
"""
Generate and send daily backtest report via Telegram
"""
import json
import os
import re
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from telegram import Bot
from typing import Dict, List

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RESULTS_DIR = Path("backtest_results")

class BacktestReporter:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
    
    async def send_message(self, message: str):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            print(f"Message sent: {len(message)} characters")
        except Exception as e:
            print(f"Failed to send message: {e}")
    
    def parse_backtest_output(self, output_file: Path) -> Dict:
        """Parse freqtrade backtest output"""
        if not output_file.exists():
            return {'error': 'Output file not found'}
        
        try:
            with open(output_file, 'r') as f:
                content = f.read()
            
            # Extract key metrics using regex
            metrics = {}
            
            # Total profit
            profit_match = re.search(r'Total profit\s+([+-]?\d+\.?\d*)\s+USDT', content)
            if profit_match:
                metrics['total_profit'] = float(profit_match.group(1))
            
            # Total profit percentage
            profit_pct_match = re.search(r'Total profit %\s+([+-]?\d+\.?\d*)%', content)
            if profit_pct_match:
                metrics['total_profit_pct'] = float(profit_pct_match.group(1))
            
            # Number of trades
            trades_match = re.search(r'Total trades\s+(\d+)', content)
            if trades_match:
                metrics['total_trades'] = int(trades_match.group(1))
            
            # Win rate
            win_rate_match = re.search(r'Winrate\s+(\d+\.?\d*)%', content)
            if win_rate_match:
                metrics['win_rate'] = float(win_rate_match.group(1))
            
            # Best trade
            best_trade_match = re.search(r'Best trade\s+([+-]?\d+\.?\d*)\s+USDT', content)
            if best_trade_match:
                metrics['best_trade'] = float(best_trade_match.group(1))
            
            # Worst trade
            worst_trade_match = re.search(r'Worst trade\s+([+-]?\d+\.?\d*)\s+USDT', content)
            if worst_trade_match:
                metrics['worst_trade'] = float(worst_trade_match.group(1))
            
            # Max drawdown
            drawdown_match = re.search(r'Max drawdown\s+([+-]?\d+\.?\d*)\s+USDT', content)
            if drawdown_match:
                metrics['max_drawdown'] = float(drawdown_match.group(1))
            
            # Max drawdown percentage
            drawdown_pct_match = re.search(r'Max drawdown %\s+([+-]?\d+\.?\d*)%', content)
            if drawdown_pct_match:
                metrics['max_drawdown_pct'] = float(drawdown_pct_match.group(1))
            
            # Sharpe ratio
            sharpe_match = re.search(r'Sharpe\s+([+-]?\d+\.?\d*)', content)
            if sharpe_match:
                metrics['sharpe_ratio'] = float(sharpe_match.group(1))
            
            # Profit factor
            profit_factor_match = re.search(r'Profit factor\s+([+-]?\d+\.?\d*)', content)
            if profit_factor_match:
                metrics['profit_factor'] = float(profit_factor_match.group(1))
            
            return metrics
            
        except Exception as e:
            return {'error': f'Failed to parse output: {str(e)}'}
    
    def format_strategy_report(self, strategy_name: str, metrics: Dict) -> str:
        """Format individual strategy report"""
        if 'error' in metrics:
            return f"❌ <b>{strategy_name}</b>\n   Erro: {metrics['error']}\n"
        
        # Determine overall performance emoji
        profit = metrics.get('total_profit', 0)
        win_rate = metrics.get('win_rate', 0)
        
        if profit > 0 and win_rate > 50:
            emoji = "🟢"
        elif profit > 0 or win_rate > 45:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        report = f"{emoji} <b>{strategy_name}</b>\n"
        
        # Key metrics
        if 'total_profit' in metrics:
            report += f"   💰 Lucro: {metrics['total_profit']:.2f} USDT ({metrics.get('total_profit_pct', 0):.2f}%)\n"
        
        if 'total_trades' in metrics:
            report += f"   📊 Trades: {metrics['total_trades']}"
            if 'win_rate' in metrics:
                report += f" (Win: {metrics['win_rate']:.1f}%)"
            report += "\n"
        
        if 'max_drawdown' in metrics:
            report += f"   📉 Max DD: {metrics['max_drawdown']:.2f} USDT ({metrics.get('max_drawdown_pct', 0):.2f}%)\n"
        
        if 'sharpe_ratio' in metrics:
            report += f"   📈 Sharpe: {metrics['sharpe_ratio']:.2f}\n"
        
        if 'best_trade' in metrics and 'worst_trade' in metrics:
            report += f"   🎯 Melhor/Pior: {metrics['best_trade']:.2f} / {metrics['worst_trade']:.2f} USDT\n"
        
        return report + "\n"
    
    def calculate_portfolio_metrics(self, all_metrics: Dict) -> Dict:
        """Calculate combined portfolio metrics"""
        portfolio = {
            'total_profit': 0,
            'total_trades': 0,
            'winning_strategies': 0,
            'total_strategies': 0
        }
        
        for strategy, metrics in all_metrics.items():
            if 'error' not in metrics:
                portfolio['total_strategies'] += 1
                portfolio['total_profit'] += metrics.get('total_profit', 0)
                portfolio['total_trades'] += metrics.get('total_trades', 0)
                
                if metrics.get('total_profit', 0) > 0:
                    portfolio['winning_strategies'] += 1
        
        if portfolio['total_strategies'] > 0:
            portfolio['win_rate'] = (portfolio['winning_strategies'] / portfolio['total_strategies']) * 100
        
        return portfolio
    
    async def generate_and_send_report(self):
        """Generate complete backtest report and send via Telegram"""
        print("Generating backtest report...")
        
        # Collect all strategy results
        all_metrics = {}
        
        for output_file in RESULTS_DIR.glob("*_output.txt"):
            strategy_name = output_file.stem.replace("_output", "")
            metrics = self.parse_backtest_output(output_file)
            all_metrics[strategy_name] = metrics
        
        if not all_metrics:
            await self.send_message("❌ <b>BACKTEST DIÁRIO</b>\n\nNenhum resultado encontrado.")
            return
        
        # Build report
        report = "📊 <b>RELATÓRIO BACKTEST DIÁRIO</b>\n"
        report += f"📅 Período: Últimos 30 dias\n"
        report += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}\n\n"
        
        # Individual strategy reports
        report += "📈 <b>PERFORMANCE POR ESTRATÉGIA:</b>\n\n"
        
        for strategy_name, metrics in all_metrics.items():
            report += self.format_strategy_report(strategy_name, metrics)
        
        # Portfolio summary
        portfolio = self.calculate_portfolio_metrics(all_metrics)
        
        report += "💼 <b>RESUMO DO PORTFÓLIO:</b>\n"
        report += f"💰 Lucro Total: {portfolio['total_profit']:.2f} USDT\n"
        report += f"📊 Total de Trades: {portfolio['total_trades']}\n"
        report += f"🎯 Estratégias Lucrativas: {portfolio['winning_strategies']}/{portfolio['total_strategies']}\n"
        report += f"📈 Taxa de Sucesso: {portfolio.get('win_rate', 0):.1f}%\n\n"
        
        # Recommendations
        if portfolio['total_profit'] > 0:
            report += "✅ <b>RECOMENDAÇÃO:</b> Performance positiva - considere manter configurações atuais\n"
        elif portfolio['total_profit'] > -50:
            report += "⚠️ <b>RECOMENDAÇÃO:</b> Performance neutra - monitore de perto\n"
        else:
            report += "🚨 <b>RECOMENDAÇÃO:</b> Performance negativa - revise estratégias\n"
        
        report += "\n📋 Resultados completos disponíveis nos artifacts do GitHub Actions"
        
        # Send report (split if too long)
        if len(report) > 4000:
            # Split into multiple messages
            parts = []
            current_part = ""
            
            for line in report.split('\n'):
                if len(current_part + line + '\n') > 4000:
                    parts.append(current_part)
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part)
            
            for i, part in enumerate(parts):
                if i == 0:
                    await self.send_message(part)
                else:
                    await self.send_message(f"📊 <b>BACKTEST DIÁRIO (cont. {i+1})</b>\n\n{part}")
                await asyncio.sleep(1)  # Small delay between messages
        else:
            await self.send_message(report)

async def main():
    reporter = BacktestReporter()
    await reporter.generate_and_send_report()

if __name__ == "__main__":
    asyncio.run(main())
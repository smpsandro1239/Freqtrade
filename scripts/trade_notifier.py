#!/usr/bin/env python3
"""
Trade notification system for Telegram alerts
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

from enhanced_stats import enhanced_stats

class TradeNotifier:
    def __init__(self, telegram_bot=None):
        self.bot = telegram_bot
        self.chat_id = None
        self.monitoring = False
        self.check_interval = 30  # seconds
        self.last_check = {}
        
    def set_telegram_bot(self, bot, chat_id):
        """Set Telegram bot and chat ID for notifications"""
        self.bot = bot
        self.chat_id = chat_id
        
    async def start_monitoring(self, strategies: List[str]):
        """Start monitoring trades for notifications"""
        if not self.bot or not self.chat_id:
            logging.error("Telegram bot not configured for notifications")
            return
            
        self.monitoring = True
        logging.info(f"Started trade monitoring for strategies: {strategies}")
        
        while self.monitoring:
            try:
                await self.check_all_strategies(strategies)
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logging.error(f"Error in trade monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop trade monitoring"""
        self.monitoring = False
        logging.info("Stopped trade monitoring")
    
    async def check_all_strategies(self, strategies: List[str]):
        """Check all strategies for new trades"""
        for strategy_id in strategies:
            try:
                await self.check_strategy_trades(strategy_id)
            except Exception as e:
                logging.error(f"Error checking trades for {strategy_id}: {e}")
    
    async def check_strategy_trades(self, strategy_id: str):
        """Check for new trades in a specific strategy"""
        new_trades = enhanced_stats.check_new_trades(strategy_id)
        
        for trade in new_trades:
            if trade['is_open']:
                await self.send_buy_notification(strategy_id, trade)
            else:
                await self.send_sell_notification(strategy_id, trade)
    
    async def send_buy_notification(self, strategy_id: str, trade: Dict):
        """Send buy notification"""
        if not self.bot or not self.chat_id:
            return
            
        try:
            pair = trade['pair']
            amount = trade['amount']
            open_rate = trade['open_rate']
            open_date = trade['open_date'].strftime('%H:%M:%S') if trade['open_date'] else 'N/A'
            
            message = f"🟢 <b>COMPRA REALIZADA</b>\n\n"
            message += f"📊 <b>Estratégia:</b> {strategy_id}\n"
            message += f"💰 <b>Par:</b> {pair}\n"
            message += f"📈 <b>Quantidade:</b> {amount:.6f}\n"
            message += f"💵 <b>Preço:</b> {open_rate:.8f}\n"
            message += f"⏰ <b>Horário:</b> {open_date}\n"
            message += f"💎 <b>Valor:</b> {amount * open_rate:.4f} USDT"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logging.info(f"Sent buy notification for {strategy_id}: {pair}")
            
        except Exception as e:
            logging.error(f"Error sending buy notification: {e}")
    
    async def send_sell_notification(self, strategy_id: str, trade: Dict):
        """Send sell notification"""
        if not self.bot or not self.chat_id:
            return
            
        try:
            pair = trade['pair']
            amount = trade['amount']
            open_rate = trade['open_rate']
            close_rate = trade['close_rate']
            profit = trade['profit']
            profit_pct = trade['profit_pct']
            close_date = trade['close_date'].strftime('%H:%M:%S') if trade['close_date'] else 'N/A'
            
            # Determine profit emoji and color
            if profit > 0:
                profit_emoji = "🟢"
                result_text = "LUCRO"
            elif profit < 0:
                profit_emoji = "🔴"
                result_text = "PREJUÍZO"
            else:
                profit_emoji = "⚪"
                result_text = "EMPATE"
            
            message = f"{profit_emoji} <b>VENDA REALIZADA - {result_text}</b>\n\n"
            message += f"📊 <b>Estratégia:</b> {strategy_id}\n"
            message += f"💰 <b>Par:</b> {pair}\n"
            message += f"📈 <b>Quantidade:</b> {amount:.6f}\n"
            message += f"💵 <b>Preço Compra:</b> {open_rate:.8f}\n"
            message += f"💵 <b>Preço Venda:</b> {close_rate:.8f}\n"
            message += f"⏰ <b>Horário:</b> {close_date}\n"
            message += f"💎 <b>P&L:</b> {profit:.4f} USDT ({profit_pct:.2f}%)"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logging.info(f"Sent sell notification for {strategy_id}: {pair} - P&L: {profit:.4f}")
            
        except Exception as e:
            logging.error(f"Error sending sell notification: {e}")
    
    async def send_daily_summary(self, strategies: List[str]):
        """Send daily summary of all strategies"""
        if not self.bot or not self.chat_id:
            return
            
        try:
            message = f"📊 <b>RESUMO DIÁRIO</b>\n"
            message += f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
            
            total_trades = 0
            total_profit = 0
            total_strategies = 0
            
            for strategy_id in strategies:
                try:
                    # Get today's stats
                    hourly_data = enhanced_stats.get_hourly_stats(strategy_id, 24)
                    
                    if hourly_data:
                        day_trades = sum(h['trades'] for h in hourly_data)
                        day_profit = sum(h['profit'] for h in hourly_data)
                        day_winning = sum(h['winning_trades'] for h in hourly_data)
                        
                        if day_trades > 0:
                            win_rate = (day_winning / day_trades) * 100
                            profit_emoji = "🟢" if day_profit > 0 else "🔴" if day_profit < 0 else "⚪"
                            
                            message += f"{profit_emoji} <b>{strategy_id}</b>\n"
                            message += f"   Trades: {day_trades} | Win: {win_rate:.1f}%\n"
                            message += f"   P&L: {day_profit:.4f} USDT\n\n"
                            
                            total_trades += day_trades
                            total_profit += day_profit
                            total_strategies += 1
                        else:
                            message += f"⚪ <b>{strategy_id}</b>\n"
                            message += f"   Sem trades hoje\n\n"
                            total_strategies += 1
                            
                except Exception as e:
                    message += f"🔴 <b>{strategy_id}</b>\n"
                    message += f"   Erro ao obter dados\n\n"
            
            # Overall summary
            overall_win_rate = 0
            if total_trades > 0:
                # This is approximate since we don't have exact winning trades across all strategies
                overall_win_rate = 60  # Default estimate
            
            message += f"📈 <b>TOTAL GERAL:</b>\n"
            message += f"• Estratégias: {total_strategies}\n"
            message += f"• Total Trades: {total_trades}\n"
            message += f"• P&L Total: {total_profit:.4f} USDT\n"
            message += f"• Média por Estratégia: {total_profit/total_strategies:.4f} USDT\n"
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logging.info("Sent daily summary")
            
        except Exception as e:
            logging.error(f"Error sending daily summary: {e}")

# Global instance
trade_notifier = TradeNotifier()
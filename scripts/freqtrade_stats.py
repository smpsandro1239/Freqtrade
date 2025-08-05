#!/usr/bin/env python3
"""
Module to collect real statistics from Freqtrade database
"""
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

class FreqtradeStats:
    def __init__(self, db_path="user_data/tradesv3.dryrun.sqlite"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            return None
        return sqlite3.connect(self.db_path)
    
    def get_strategy_stats(self, hours=24):
        """Get statistics for all strategies in the last N hours"""
        conn = self.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor()
            
            # Get trades from last N hours
            since = datetime.utcnow() - timedelta(hours=hours)
            since_timestamp = since.timestamp() * 1000  # Freqtrade uses milliseconds
            
            query = """
            SELECT 
                strategy,
                COUNT(*) as trade_count,
                SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(close_profit) as total_profit,
                AVG(close_profit) as avg_profit,
                MIN(close_profit) as min_profit,
                MAX(close_profit) as max_profit
            FROM trades 
            WHERE close_date_utc > ? 
            AND is_open = 0
            GROUP BY strategy
            """
            
            cursor.execute(query, (since_timestamp,))
            results = cursor.fetchall()
            
            stats = {}
            for row in results:
                strategy, count, winning, total_profit, avg_profit, min_profit, max_profit = row
                
                win_rate = (winning / count * 100) if count > 0 else 0
                
                stats[strategy] = {
                    'trades': count,
                    'winning_trades': winning,
                    'win_rate': win_rate,
                    'total_profit': total_profit or 0,
                    'avg_profit': avg_profit or 0,
                    'min_profit': min_profit or 0,
                    'max_profit': max_profit or 0
                }
            
            return stats
            
        except Exception as e:
            print(f"Database error: {e}")
            return {}
        finally:
            conn.close()
    
    def get_open_trades(self):
        """Get currently open trades"""
        conn = self.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor()
            
            query = """
            SELECT 
                strategy,
                pair,
                open_date_utc,
                stake_amount,
                open_rate,
                current_profit
            FROM trades 
            WHERE is_open = 1
            ORDER BY open_date_utc DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            open_trades = {}
            for row in results:
                strategy, pair, open_date, stake, rate, profit = row
                
                if strategy not in open_trades:
                    open_trades[strategy] = []
                
                open_trades[strategy].append({
                    'pair': pair,
                    'open_date': datetime.fromtimestamp(open_date / 1000),
                    'stake_amount': stake,
                    'open_rate': rate,
                    'current_profit': profit or 0
                })
            
            return open_trades
            
        except Exception as e:
            print(f"Database error: {e}")
            return {}
        finally:
            conn.close()

def format_profit(profit):
    """Format profit with appropriate emoji"""
    if profit > 0:
        return f"🟢 +{profit:.4f}"
    elif profit < 0:
        return f"🔴 {profit:.4f}"
    else:
        return f"⚪ {profit:.4f}"

def format_percentage(percentage):
    """Format percentage with appropriate emoji"""
    if percentage > 0:
        return f"🟢 +{percentage:.2f}%"
    elif percentage < 0:
        return f"🔴 {percentage:.2f}%"
    else:
        return f"⚪ {percentage:.2f}%"
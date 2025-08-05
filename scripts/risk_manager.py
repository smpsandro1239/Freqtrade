#!/usr/bin/env python3
"""
Dynamic Risk & Position Sizing Manager
Automatically adjusts stake amounts based on performance metrics
"""
import json
import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from freqtrade_stats import FreqtradeStats
from telegram import Bot

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CONFIG_DIR = Path("user_data/configs")
BACKUP_DIR = Path("backups/risk_adjustments")

# Risk management parameters
RISK_PARAMS = {
    'max_drawdown_threshold': 0.15,  # 15% max drawdown
    'min_win_rate': 0.40,  # 40% minimum win rate
    'max_stake_increase': 1.5,  # Max 50% increase
    'min_stake_decrease': 0.5,  # Max 50% decrease
    'base_stake_amount': 20,  # Base stake in USDT
    'evaluation_period_hours': 24,  # Look back 24 hours
    'adjustment_cooldown_hours': 6,  # Wait 6h between adjustments
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.stats = FreqtradeStats()
        self.last_adjustments = {}
        
        # Ensure backup directory exists
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    async def send_notification(self, message: str):
        """Send notification to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Notification sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def load_config(self, config_path: Path) -> Dict:
        """Load strategy configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self, config_path: Path, config: Dict):
        """Save strategy configuration with backup"""
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"{config_path.stem}_{timestamp}.json"
        
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save new config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Config saved: {config_path}, backup: {backup_path}")
    
    def calculate_performance_score(self, stats: Dict) -> float:
        """Calculate performance score (0-1, higher is better)"""
        if not stats or stats.get('trades', 0) == 0:
            return 0.5  # Neutral score for no data
        
        # Factors for scoring
        win_rate = stats.get('win_rate', 0) / 100
        total_profit = stats.get('total_profit', 0)
        avg_profit = stats.get('avg_profit', 0)
        trades_count = stats.get('trades', 0)
        
        # Normalize profit (assuming reasonable range)
        profit_score = max(0, min(1, (total_profit + 100) / 200))  # -100 to +100 USDT range
        
        # Win rate score
        win_rate_score = max(0, min(1, win_rate / 0.8))  # 80% win rate = perfect
        
        # Activity score (more trades = more confidence in metrics)
        activity_score = min(1, trades_count / 20)  # 20+ trades = full confidence
        
        # Average profit per trade score
        avg_profit_score = max(0, min(1, (avg_profit + 5) / 10))  # -5 to +5 USDT range
        
        # Weighted combination
        score = (
            profit_score * 0.4 +
            win_rate_score * 0.3 +
            activity_score * 0.2 +
            avg_profit_score * 0.1
        )
        
        return score
    
    def calculate_new_stake(self, current_stake: float, performance_score: float, stats: Dict) -> float:
        """Calculate new stake amount based on performance"""
        base_stake = RISK_PARAMS['base_stake_amount']
        
        # Risk adjustment based on performance score
        if performance_score > 0.7:
            # Good performance - increase stake
            multiplier = 1 + (performance_score - 0.7) * 1.67  # 0.7->1.0 maps to 1.0->1.5
            multiplier = min(multiplier, RISK_PARAMS['max_stake_increase'])
        elif performance_score < 0.3:
            # Poor performance - decrease stake
            multiplier = 0.5 + performance_score * 1.67  # 0.0->0.3 maps to 0.5->1.0
            multiplier = max(multiplier, RISK_PARAMS['min_stake_decrease'])
        else:
            # Neutral performance - gradual adjustment toward base
            if current_stake > base_stake:
                multiplier = max(1.0, current_stake / base_stake * 0.9)
            else:
                multiplier = min(1.0, current_stake / base_stake * 1.1)
        
        new_stake = base_stake * multiplier
        
        # Additional safety checks
        total_profit = stats.get('total_profit', 0)
        if total_profit < -50:  # Large losses
            new_stake = min(new_stake, base_stake * 0.7)
        
        win_rate = stats.get('win_rate', 50)
        if win_rate < RISK_PARAMS['min_win_rate'] * 100:
            new_stake = min(new_stake, base_stake * 0.8)
        
        return round(new_stake, 2)
    
    def should_adjust_strategy(self, strategy_name: str) -> bool:
        """Check if enough time has passed since last adjustment"""
        last_adjustment = self.last_adjustments.get(strategy_name)
        if not last_adjustment:
            return True
        
        cooldown = timedelta(hours=RISK_PARAMS['adjustment_cooldown_hours'])
        return datetime.now() - last_adjustment > cooldown
    
    async def adjust_strategy_risk(self, config_path: Path) -> Dict:
        """Adjust risk parameters for a single strategy"""
        strategy_name = config_path.stem
        
        # Check cooldown
        if not self.should_adjust_strategy(strategy_name):
            logger.info(f"Skipping {strategy_name} - still in cooldown period")
            return {'action': 'skipped', 'reason': 'cooldown'}
        
        # Load current config
        config = self.load_config(config_path)
        current_stake = config.get('stake_amount', RISK_PARAMS['base_stake_amount'])
        
        # Get performance stats
        all_stats = self.stats.get_strategy_stats(hours=RISK_PARAMS['evaluation_period_hours'])
        strategy_stats = all_stats.get(config.get('strategy', ''), {})
        
        if not strategy_stats or strategy_stats.get('trades', 0) < 3:
            logger.info(f"Insufficient data for {strategy_name} (need at least 3 trades)")
            return {'action': 'skipped', 'reason': 'insufficient_data'}
        
        # Calculate performance score and new stake
        performance_score = self.calculate_performance_score(strategy_stats)
        new_stake = self.calculate_new_stake(current_stake, performance_score, strategy_stats)
        
        # Check if adjustment is significant enough
        change_pct = abs(new_stake - current_stake) / current_stake
        if change_pct < 0.05:  # Less than 5% change
            logger.info(f"No significant adjustment needed for {strategy_name}")
            return {'action': 'skipped', 'reason': 'minimal_change'}
        
        # Apply adjustment
        config['stake_amount'] = new_stake
        self.save_config(config_path, config)
        self.last_adjustments[strategy_name] = datetime.now()
        
        # Prepare result
        result = {
            'action': 'adjusted',
            'strategy': strategy_name,
            'old_stake': current_stake,
            'new_stake': new_stake,
            'change_pct': (new_stake - current_stake) / current_stake * 100,
            'performance_score': performance_score,
            'stats': strategy_stats
        }
        
        logger.info(f"Adjusted {strategy_name}: {current_stake} -> {new_stake} USDT ({result['change_pct']:+.1f}%)")
        return result
    
    async def run_risk_assessment(self) -> List[Dict]:
        """Run risk assessment for all strategies"""
        logger.info("Starting risk assessment...")
        
        results = []
        config_files = list(CONFIG_DIR.glob("*.json"))
        
        for config_path in config_files:
            try:
                result = await self.adjust_strategy_risk(config_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error adjusting {config_path.name}: {e}")
                results.append({
                    'action': 'error',
                    'strategy': config_path.stem,
                    'error': str(e)
                })
        
        return results
    
    async def send_risk_report(self, results: List[Dict]):
        """Send risk management report to Telegram"""
        adjustments = [r for r in results if r['action'] == 'adjusted']
        
        if not adjustments:
            # No adjustments made
            message = "📊 <b>RISK MANAGEMENT</b>\n\n"
            message += "✅ Nenhum ajuste necessário\n"
            message += "📈 Todas as estratégias dentro dos parâmetros\n\n"
            message += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        else:
            # Adjustments were made
            message = "⚖️ <b>AJUSTES DE RISCO APLICADOS</b>\n\n"
            
            for adj in adjustments:
                emoji = "📈" if adj['change_pct'] > 0 else "📉"
                message += f"{emoji} <b>{adj['strategy']}</b>\n"
                message += f"   💰 Stake: {adj['old_stake']} → {adj['new_stake']} USDT\n"
                message += f"   📊 Mudança: {adj['change_pct']:+.1f}%\n"
                message += f"   🎯 Score: {adj['performance_score']:.2f}\n"
                message += f"   📈 Trades: {adj['stats']['trades']} (Win: {adj['stats']['win_rate']:.1f}%)\n\n"
            
            message += "🔄 <b>Reinicie os containers para aplicar:</b>\n"
            message += "<code>docker compose restart</code>\n\n"
            message += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        await self.send_notification(message)
    
    async def start_monitoring(self):
        """Start risk monitoring loop"""
        logger.info("Starting risk management monitoring...")
        
        await self.send_notification("⚖️ <b>RISK MANAGER INICIADO</b>\n\nMonitorando performance e ajustando stakes automaticamente...")
        
        while True:
            try:
                # Run risk assessment every 6 hours
                results = await self.run_risk_assessment()
                await self.send_risk_report(results)
                
                # Sleep for 6 hours
                await asyncio.sleep(6 * 3600)
                
            except Exception as e:
                logger.error(f"Error in risk monitoring loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retrying

async def main():
    risk_manager = RiskManager()
    await risk_manager.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
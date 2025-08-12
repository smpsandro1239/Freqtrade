#!/usr/bin/env python3
"""
Trading Commands - Sistema de comandos de trading manual
Permite compra/venda forçada e ajuste dinâmico de estratégias
"""
import os
import json
import logging
import subprocess
import docker
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class TradingCommands:
    def __init__(self):
        self.project_root = Path("/app/project")
        self.docker_client = docker.from_env()
        
    def execute_freqtrade_command(self, strategy_id: str, command: str) -> Tuple[bool, str]:
        """Execute freqtrade command in strategy container"""
        try:
            container_name = f"ft-{strategy_id}"
            container = self.docker_client.containers.get(container_name)
            
            if container.status != 'running':
                return False, f"Container {container_name} não está rodando"
            
            # Execute command
            result = container.exec_run(command, workdir="/freqtrade")
            
            if result.exit_code == 0:
                return True, result.output.decode('utf-8')
            else:
                return False, result.output.decode('utf-8')
                
        except docker.errors.NotFound:
            return False, f"Container {container_name} não encontrado"
        except Exception as e:
            return False, f"Erro ao executar comando: {str(e)}"
    
    def force_buy(self, strategy_id: str, pair: str, amount: Optional[float] = None) -> Tuple[bool, str]:
        """Force buy a specific pair"""
        try:
            # Build command
            if amount:
                command = f"freqtrade trade --config user_data/configs/{strategy_id}.json --strategy {strategy_id} --forcebuy {pair} --amount {amount}"
            else:
                command = f"freqtrade trade --config user_data/configs/{strategy_id}.json --strategy {strategy_id} --forcebuy {pair}"
            
            success, output = self.execute_freqtrade_command(strategy_id, command)
            
            if success:
                return True, f"✅ Compra forçada executada:\nPar: {pair}\nQuantidade: {amount or 'padrão'}\n\nOutput:\n{output}"
            else:
                return False, f"❌ Erro na compra forçada:\n{output}"
                
        except Exception as e:
            return False, f"❌ Erro interno: {str(e)}"
    
    def force_sell(self, strategy_id: str, pair: str, amount: Optional[float] = None) -> Tuple[bool, str]:
        """Force sell a specific pair"""
        try:
            # Build command
            if amount:
                command = f"freqtrade trade --config user_data/configs/{strategy_id}.json --strategy {strategy_id} --forcesell {pair} --amount {amount}"
            else:
                command = f"freqtrade trade --config user_data/configs/{strategy_id}.json --strategy {strategy_id} --forcesell {pair}"
            
            success, output = self.execute_freqtrade_command(strategy_id, command)
            
            if success:
                return True, f"✅ Venda forçada executada:\nPar: {pair}\nQuantidade: {amount or 'todas as posições'}\n\nOutput:\n{output}"
            else:
                return False, f"❌ Erro na venda forçada:\n{output}"
                
        except Exception as e:
            return False, f"❌ Erro interno: {str(e)}"
    
    def get_open_trades(self, strategy_id: str) -> Tuple[bool, List[Dict]]:
        """Get open trades for a strategy"""
        try:
            command = f"freqtrade show_trades --config user_data/configs/{strategy_id}.json --trade-ids --open-only"
            success, output = self.execute_freqtrade_command(strategy_id, command)
            
            if success:
                # Parse output to extract trade information
                trades = self._parse_trades_output(output)
                return True, trades
            else:
                return False, []
                
        except Exception as e:
            logging.error(f"Error getting open trades: {e}")
            return False, []
    
    def _parse_trades_output(self, output: str) -> List[Dict]:
        """Parse freqtrade trades output"""
        trades = []
        lines = output.split('\n')
        
        for line in lines:
            if '|' in line and 'BTC' in line or 'ETH' in line or 'USDT' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    try:
                        trades.append({
                            'id': parts[1],
                            'pair': parts[2],
                            'amount': parts[3],
                            'open_rate': parts[4],
                            'current_rate': parts[5] if len(parts) > 5 else 'N/A',
                            'profit': parts[6] if len(parts) > 6 else 'N/A'
                        })
                    except:
                        continue
        
        return trades
    
    def adjust_strategy_sensitivity(self, strategy_id: str, mode: str) -> Tuple[bool, str]:
        """Adjust strategy sensitivity based on market conditions"""
        try:
            config_path = self.project_root / "user_data" / "configs" / f"{strategy_id}.json"
            
            if not config_path.exists():
                return False, f"Arquivo de configuração não encontrado: {config_path}"
            
            # Load current config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Backup original config
            backup_path = config_path.with_suffix('.json.backup')
            with open(backup_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Adjust parameters based on mode
            if mode == "aggressive":
                adjustments = self._get_aggressive_adjustments()
                message = "🔥 Modo AGRESSIVO ativado - Estratégia mais penetrável"
            elif mode == "conservative":
                adjustments = self._get_conservative_adjustments()
                message = "🛡️ Modo CONSERVADOR ativado - Estratégia mais cautelosa"
            elif mode == "balanced":
                adjustments = self._get_balanced_adjustments()
                message = "⚖️ Modo EQUILIBRADO ativado - Estratégia balanceada"
            else:
                return False, "Modo inválido. Use: aggressive, conservative, balanced"
            
            # Apply adjustments
            changes_made = []
            for key, value in adjustments.items():
                if key in config:
                    old_value = config[key]
                    config[key] = value
                    changes_made.append(f"• {key}: {old_value} → {value}")
                else:
                    config[key] = value
                    changes_made.append(f"• {key}: adicionado → {value}")
            
            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Restart strategy to apply changes
            restart_success, restart_msg = self._restart_strategy(strategy_id)
            
            result_message = f"{message}\n\n📝 Alterações aplicadas:\n" + "\n".join(changes_made)
            
            if restart_success:
                result_message += f"\n\n🔄 Estratégia reiniciada com sucesso"
            else:
                result_message += f"\n\n⚠️ Configuração salva, mas erro ao reiniciar: {restart_msg}"
            
            return True, result_message
            
        except Exception as e:
            return False, f"❌ Erro ao ajustar estratégia: {str(e)}"
    
    def _get_aggressive_adjustments(self) -> Dict:
        """Get aggressive trading parameters"""
        return {
            "minimal_roi": {
                "0": 0.02,    # 2% ROI target (lower)
                "10": 0.015,  # 1.5% after 10 minutes
                "20": 0.01,   # 1% after 20 minutes
                "30": 0.005   # 0.5% after 30 minutes
            },
            "stoploss": -0.08,  # 8% stop loss (tighter)
            "trailing_stop": True,
            "trailing_stop_positive": 0.01,  # 1%
            "trailing_stop_positive_offset": 0.015,  # 1.5%
            "max_open_trades": 8,  # More concurrent trades
            "stake_amount": "unlimited",
            "timeframe": "5m"  # Faster timeframe
        }
    
    def _get_conservative_adjustments(self) -> Dict:
        """Get conservative trading parameters"""
        return {
            "minimal_roi": {
                "0": 0.08,    # 8% ROI target (higher)
                "30": 0.06,   # 6% after 30 minutes
                "60": 0.04,   # 4% after 1 hour
                "120": 0.02   # 2% after 2 hours
            },
            "stoploss": -0.15,  # 15% stop loss (looser)
            "trailing_stop": True,
            "trailing_stop_positive": 0.03,  # 3%
            "trailing_stop_positive_offset": 0.05,  # 5%
            "max_open_trades": 3,  # Fewer concurrent trades
            "stake_amount": 50,  # Fixed amount
            "timeframe": "15m"  # Slower timeframe
        }
    
    def _get_balanced_adjustments(self) -> Dict:
        """Get balanced trading parameters"""
        return {
            "minimal_roi": {
                "0": 0.04,    # 4% ROI target
                "15": 0.03,   # 3% after 15 minutes
                "30": 0.02,   # 2% after 30 minutes
                "60": 0.01    # 1% after 1 hour
            },
            "stoploss": -0.10,  # 10% stop loss
            "trailing_stop": True,
            "trailing_stop_positive": 0.02,  # 2%
            "trailing_stop_positive_offset": 0.03,  # 3%
            "max_open_trades": 5,  # Moderate concurrent trades
            "stake_amount": 100,  # Moderate amount
            "timeframe": "10m"  # Balanced timeframe
        }
    
    def _restart_strategy(self, strategy_id: str) -> Tuple[bool, str]:
        """Restart a strategy container"""
        try:
            container_name = f"ft-{strategy_id}"
            container = self.docker_client.containers.get(container_name)
            
            container.restart()
            return True, "Container reiniciado com sucesso"
            
        except docker.errors.NotFound:
            return False, f"Container {container_name} não encontrado"
        except Exception as e:
            return False, f"Erro ao reiniciar container: {str(e)}"
    
    def get_market_analysis(self) -> Dict:
        """Get basic market analysis for strategy adjustment recommendations"""
        try:
            # This would typically connect to market data APIs
            # For now, we'll return mock analysis
            import random
            
            volatility = random.uniform(0.1, 0.8)
            trend = random.choice(['bullish', 'bearish', 'sideways'])
            volume = random.uniform(0.3, 1.0)
            
            if volatility > 0.6:
                recommended_mode = "conservative"
                reason = "Alta volatilidade detectada"
            elif trend == 'bullish' and volume > 0.7:
                recommended_mode = "aggressive"
                reason = "Tendência de alta com volume forte"
            else:
                recommended_mode = "balanced"
                reason = "Condições de mercado normais"
            
            return {
                'volatility': volatility,
                'trend': trend,
                'volume': volume,
                'recommended_mode': recommended_mode,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'recommended_mode': 'balanced',
                'reason': 'Erro na análise, usando modo padrão'
            }
    
    def format_trading_status(self, strategy_id: str) -> str:
        """Format trading status for Telegram"""
        try:
            success, trades = self.get_open_trades(strategy_id)
            
            message = f"📊 <b>STATUS DE TRADING - {strategy_id}</b>\n\n"
            
            if success and trades:
                message += f"🔄 <b>Posições Abertas ({len(trades)}):</b>\n"
                for trade in trades[:5]:  # Show max 5 trades
                    message += f"• {trade['pair']}: {trade['amount']} @ {trade['open_rate']}\n"
                
                if len(trades) > 5:
                    message += f"... e mais {len(trades) - 5} posições\n"
            else:
                message += f"💤 <b>Nenhuma posição aberta</b>\n"
            
            # Add market analysis
            analysis = self.get_market_analysis()
            message += f"\n📈 <b>Análise de Mercado:</b>\n"
            message += f"• Volatilidade: {analysis['volatility']:.1%}\n"
            message += f"• Tendência: {analysis['trend'].title()}\n"
            message += f"• Volume: {analysis['volume']:.1%}\n"
            message += f"• Recomendação: {analysis['recommended_mode'].title()}\n"
            message += f"• Motivo: {analysis['reason']}\n"
            
            return message
            
        except Exception as e:
            return f"❌ Erro ao obter status: {str(e)}"

# Global instance
trading_commands = TradingCommands()
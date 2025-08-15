#!/usr/bin/env python3
"""
⚙️ Otimizador de Configurações - FreqTrade Multi-Strategy
Otimiza e padroniza configurações para segurança e performance
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class ConfigOptimizer:
    """Otimizador de configurações de trading"""
    
    def __init__(self):
        self.configs_path = Path("user_data/configs")
        self.backup_path = Path("backups/configs")
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Configurações padrão seguras
        self.safe_defaults = {
            "dry_run": True,
            "stake_amount": 20,
            "max_open_trades": 3,
            "minimal_roi": {
                "0": 0.04,
                "5": 0.03,
                "10": 0.02,
                "15": 0.01,
                "30": 0.001
            },
            "stoploss": -0.08,
            "trailing_stop": True,
            "trailing_stop_positive": 0.02,
            "trailing_stop_positive_offset": 0.03,
            "trailing_only_offset_is_reached": True,
            "unfilledtimeout": {
                "buy": 10,
                "sell": 30
            },
            "order_types": {
                "buy": "limit",
                "sell": "limit",
                "emergencysell": "market",
                "stoploss": "market",
                "stoploss_on_exchange": False
            },
            "exchange": {
                "name": "binance",
                "key": "${EXCHANGE_KEY}",
                "secret": "${EXCHANGE_SECRET}",
                "ccxt_config": {
                    "enableRateLimit": True,
                    "rateLimit": 200
                },
                "pair_whitelist": [
                    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
                    "LINK/USDT", "LTC/USDT", "BCH/USDT", "XRP/USDT", "EOS/USDT"
                ],
                "pair_blacklist": []
            },
            "pairlists": [
                {
                    "method": "StaticPairList"
                }
            ],
            "protections": [
                {
                    "method": "StoplossGuard",
                    "lookback_period_candles": 60,
                    "trade_limit": 4,
                    "stop_duration_candles": 60,
                    "only_per_pair": False
                },
                {
                    "method": "CooldownPeriod",
                    "stop_duration_candles": 20
                }
            ],
            "telegram": {
                "enabled": True,
                "token": "${TELEGRAM_TOKEN}",
                "chat_id": "${TELEGRAM_CHAT_ID}",
                "notification_settings": {
                    "status": "on",
                    "warning": "on",
                    "startup": "on",
                    "buy": "on",
                    "sell": "on",
                    "buy_cancel": "on",
                    "sell_cancel": "on"
                }
            },
            "api_server": {
                "enabled": True,
                "listen_ip_address": "0.0.0.0",
                "listen_port": 8080,
                "verbosity": "error",
                "enable_openapi": False,
                "jwt_secret_key": "${DASHBOARD_SECRET_KEY}",
                "CORS_origins": [],
                "username": "${DASHBOARD_USERNAME}",
                "password": "${DASHBOARD_PASSWORD}"
            },
            "bot_name": "FreqTrade-MultiStrategy",
            "initial_state": "running",
            "force_entry_enable": True,
            "internals": {
                "process_throttle_secs": 5
            }
        }
        
        # Configurações específicas por estratégia
        self.strategy_configs = {
            "SampleStrategyA": {
                "timeframe": "15m",
                "stake_amount": 20,
                "max_open_trades": 2,
                "api_server": {"listen_port": 8081}
            },
            "SampleStrategyB": {
                "timeframe": "15m", 
                "stake_amount": 25,
                "max_open_trades": 3,
                "api_server": {"listen_port": 8082}
            },
            "WaveHyperNWStrategy": {
                "timeframe": "5m",
                "stake_amount": 20,
                "max_open_trades": 6,
                "api_server": {"listen_port": 8083}
            },
            "WaveHyperNWEnhanced": {
                "timeframe": "5m",
                "stake_amount": 30,
                "max_open_trades": 4,
                "api_server": {"listen_port": 8087}
            },
            "MLStrategy": {
                "timeframe": "15m",
                "stake_amount": 50,
                "max_open_trades": 3,
                "api_server": {"listen_port": 8084}
            },
            "MLStrategySimple": {
                "timeframe": "15m",
                "stake_amount": 30,
                "max_open_trades": 3,
                "api_server": {"listen_port": 8085}
            },
            "MultiTimeframeStrategy": {
                "timeframe": "5m",
                "stake_amount": 40,
                "max_open_trades": 4,
                "api_server": {"listen_port": 8086}
            }
        }
    
    def backup_config(self, config_file: Path):
        """Faz backup de uma configuração"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"{config_file.stem}_{timestamp}.json"
        shutil.copy2(config_file, backup_file)
        return backup_file
    
    def load_config(self, config_file: Path) -> Dict[str, Any]:
        """Carrega uma configuração"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar {config_file.name}: {e}")
            return {}
    
    def save_config(self, config_file: Path, config: Dict[str, Any]):
        """Salva uma configuração"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar {config_file.name}: {e}")
            return False
    
    def merge_configs(self, base_config: Dict, updates: Dict) -> Dict:
        """Merge recursivo de configurações"""
        result = base_config.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def optimize_config(self, config_file: Path) -> bool:
        """Otimiza uma configuração específica"""
        print(f"⚙️  Otimizando {config_file.name}...")
        
        # Fazer backup
        backup_file = self.backup_config(config_file)
        print(f"   💾 Backup: {backup_file.name}")
        
        # Carregar configuração atual
        current_config = self.load_config(config_file)
        if not current_config:
            return False
        
        # Identificar estratégia
        strategy_name = current_config.get('strategy')
        if not strategy_name:
            print(f"   ❌ Estratégia não identificada em {config_file.name}")
            return False
        
        print(f"   📊 Estratégia: {strategy_name}")
        
        # Começar com configurações padrão seguras
        optimized_config = self.safe_defaults.copy()
        
        # Aplicar configurações específicas da estratégia
        if strategy_name in self.strategy_configs:
            strategy_specific = self.strategy_configs[strategy_name]
            optimized_config = self.merge_configs(optimized_config, strategy_specific)
            print(f"   ✅ Aplicadas configurações específicas para {strategy_name}")
        
        # Preservar configurações importantes do arquivo original
        preserve_fields = ['strategy', 'user_data_dir']
        for field in preserve_fields:
            if field in current_config:
                optimized_config[field] = current_config[field]
        
        # Aplicar configurações de segurança
        optimized_config['dry_run'] = True  # Sempre começar em dry-run
        optimized_config['force_entry_enable'] = True  # Permitir trading manual
        
        # Salvar configuração otimizada
        if self.save_config(config_file, optimized_config):
            print(f"   ✅ {config_file.name} otimizado com sucesso")
            
            # Mostrar mudanças importantes
            old_dry_run = current_config.get('dry_run', True)
            old_stake = current_config.get('stake_amount', 0)
            old_trades = current_config.get('max_open_trades', 0)
            
            new_dry_run = optimized_config['dry_run']
            new_stake = optimized_config['stake_amount']
            new_trades = optimized_config['max_open_trades']
            
            if old_dry_run != new_dry_run:
                print(f"   🔄 dry_run: {old_dry_run} → {new_dry_run}")
            if old_stake != new_stake:
                print(f"   💰 stake_amount: {old_stake} → {new_stake} USDT")
            if old_trades != new_trades:
                print(f"   📊 max_open_trades: {old_trades} → {new_trades}")
            
            return True
        else:
            return False
    
    def create_missing_configs(self):
        """Cria configurações para estratégias sem config"""
        print("\n🔧 CRIANDO CONFIGURAÇÕES FALTANTES")
        print("-" * 40)
        
        strategies_path = Path("user_data/strategies")
        if not strategies_path.exists():
            print("❌ Pasta de estratégias não encontrada!")
            return
        
        # Encontrar estratégias sem configuração
        strategy_files = list(strategies_path.glob("*.py"))
        existing_configs = {f.stem for f in self.configs_path.glob("*.json")}
        
        created_configs = []
        
        for strategy_file in strategy_files:
            if strategy_file.name.startswith('__'):
                continue
                
            strategy_name = strategy_file.stem
            
            # Tentar identificar classe da estratégia
            try:
                with open(strategy_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar classe que herda de IStrategy
                import re
                class_match = re.search(r'class\s+(\w+)\s*\([^)]*IStrategy[^)]*\):', content)
                if class_match:
                    class_name = class_match.group(1)
                    
                    # Verificar se já existe config para esta classe
                    config_exists = False
                    for config_file in self.configs_path.glob("*.json"):
                        config = self.load_config(config_file)
                        if config.get('strategy') == class_name:
                            config_exists = True
                            break
                    
                    if not config_exists:
                        # Criar nova configuração
                        config_name = strategy_name.lower()
                        config_file = self.configs_path / f"{config_name}.json"
                        
                        new_config = self.safe_defaults.copy()
                        new_config['strategy'] = class_name
                        
                        # Aplicar configurações específicas se disponíveis
                        if class_name in self.strategy_configs:
                            specific_config = self.strategy_configs[class_name]
                            new_config = self.merge_configs(new_config, specific_config)
                        
                        if self.save_config(config_file, new_config):
                            print(f"   ✅ Criado {config_file.name} para {class_name}")
                            created_configs.append(config_file.name)
                        else:
                            print(f"   ❌ Falha ao criar {config_file.name}")
                            
            except Exception as e:
                print(f"   ❌ Erro ao processar {strategy_file.name}: {e}")
        
        if created_configs:
            print(f"\n🎉 {len(created_configs)} configurações criadas:")
            for config in created_configs:
                print(f"   📄 {config}")
        else:
            print("   ℹ️  Nenhuma configuração nova necessária")
    
    def optimize_all_configs(self):
        """Otimiza todas as configurações"""
        print("⚙️  OTIMIZANDO CONFIGURAÇÕES")
        print("-" * 40)
        
        if not self.configs_path.exists():
            print("❌ Pasta de configurações não encontrada!")
            return False
        
        config_files = list(self.configs_path.glob("*.json"))
        if not config_files:
            print("❌ Nenhuma configuração encontrada!")
            return False
        
        success_count = 0
        total_count = len(config_files)
        
        for config_file in config_files:
            if self.optimize_config(config_file):
                success_count += 1
        
        print(f"\n📊 RESULTADO: {success_count}/{total_count} configurações otimizadas")
        return success_count == total_count
    
    def generate_summary(self):
        """Gera resumo das configurações otimizadas"""
        print("\n📋 RESUMO DAS CONFIGURAÇÕES")
        print("=" * 50)
        
        config_files = list(self.configs_path.glob("*.json"))
        
        for config_file in config_files:
            config = self.load_config(config_file)
            if not config:
                continue
            
            strategy = config.get('strategy', 'N/A')
            dry_run = config.get('dry_run', True)
            stake = config.get('stake_amount', 0)
            trades = config.get('max_open_trades', 0)
            port = config.get('api_server', {}).get('listen_port', 'N/A')
            
            status = "DRY-RUN" if dry_run else "🔴 LIVE"
            
            print(f"📄 {config_file.name}")
            print(f"   📊 Estratégia: {strategy}")
            print(f"   💰 Stake: {stake} USDT")
            print(f"   📈 Max Trades: {trades}")
            print(f"   🌐 API Port: {port}")
            print(f"   🔒 Modo: {status}")
            print()
    
    def run_optimization(self):
        """Executa otimização completa"""
        print("⚙️  OTIMIZADOR DE CONFIGURAÇÕES - FreqTrade Multi-Strategy")
        print("=" * 60)
        print()
        
        # Criar configurações faltantes
        self.create_missing_configs()
        
        # Otimizar todas as configurações
        success = self.optimize_all_configs()
        
        # Gerar resumo
        self.generate_summary()
        
        if success:
            print("🎉 OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n🔒 CONFIGURAÇÕES DE SEGURANÇA APLICADAS:")
            print("   ✅ Todas as estratégias em modo DRY-RUN")
            print("   ✅ Stakes seguros e balanceados")
            print("   ✅ Proteções ativadas (StoplossGuard + CooldownPeriod)")
            print("   ✅ Rate limiting habilitado")
            print("   ✅ Telegram notifications configuradas")
            print("   ✅ API servers com portas únicas")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("   1. Execute: python validate_strategies.py")
            print("   2. Execute: .\run.ps1 dry")
            print("   3. Execute: .\run.ps1 status")
            
            return True
        else:
            print("❌ OTIMIZAÇÃO INCOMPLETA - VERIFIQUE OS ERROS")
            return False

def main():
    """Função principal"""
    try:
        optimizer = ConfigOptimizer()
        success = optimizer.run_optimization()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Otimização cancelada pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro durante a otimização: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
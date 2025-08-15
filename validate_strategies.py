#!/usr/bin/env python3
"""
🔍 Validador de Estratégias - FreqTrade Multi-Strategy
Valida estratégias e configurações antes do deploy
"""

import json
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

class StrategyValidator:
    """Validador completo de estratégias e configurações"""
    
    def __init__(self):
        self.strategies_path = Path("user_data/strategies")
        self.configs_path = Path("user_data/configs")
        self.results = {
            'strategies': {},
            'configs': {},
            'matches': {},
            'issues': []
        }
    
    def validate_strategy_file(self, strategy_file: Path) -> Dict[str, Any]:
        """Valida um arquivo de estratégia Python"""
        result = {
            'file': strategy_file.name,
            'valid': False,
            'class_name': None,
            'timeframe': None,
            'stoploss': None,
            'roi': None,
            'indicators': [],
            'issues': []
        }
        
        try:
            # Ler e parsear o arquivo
            with open(strategy_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST para análise estática
            tree = ast.parse(content)
            
            # Encontrar classe da estratégia
            strategy_classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar se herda de IStrategy
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'IStrategy':
                            strategy_classes.append(node.name)
                            result['class_name'] = node.name
                            
                            # Analisar atributos da classe
                            for item in node.body:
                                if isinstance(item, ast.Assign):
                                    for target in item.targets:
                                        if isinstance(target, ast.Name):
                                            attr_name = target.id
                                            
                                            # Extrair valores importantes
                                            if attr_name == 'timeframe':
                                                if isinstance(item.value, ast.Constant):
                                                    result['timeframe'] = item.value.value
                                            elif attr_name == 'stoploss':
                                                if isinstance(item.value, ast.Constant):
                                                    result['stoploss'] = item.value.value
                                                elif isinstance(item.value, ast.UnaryOp) and isinstance(item.value.op, ast.USub):
                                                    if isinstance(item.value.operand, ast.Constant):
                                                        result['stoploss'] = -item.value.operand.value
            
            if not strategy_classes:
                result['issues'].append("Nenhuma classe IStrategy encontrada")
            elif len(strategy_classes) > 1:
                result['issues'].append(f"Múltiplas classes encontradas: {strategy_classes}")
            else:
                result['valid'] = True
                
            # Verificar imports necessários
            required_imports = ['IStrategy', 'talib', 'pandas', 'numpy']
            imports_found = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports_found.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            imports_found.append(f"{node.module}.{alias.name}")
            
            # Verificar indicadores técnicos usados
            indicators_patterns = ['ta.', 'talib.', 'qtpylib.', 'RSI', 'MACD', 'EMA', 'SMA', 'BB']
            for pattern in indicators_patterns:
                if pattern in content:
                    result['indicators'].append(pattern)
            
        except SyntaxError as e:
            result['issues'].append(f"Erro de sintaxe: {e}")
        except Exception as e:
            result['issues'].append(f"Erro na validação: {e}")
        
        return result
    
    def validate_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Valida um arquivo de configuração JSON"""
        result = {
            'file': config_file.name,
            'valid': False,
            'strategy': None,
            'dry_run': None,
            'stake_amount': None,
            'max_open_trades': None,
            'pairs': [],
            'exchange': None,
            'issues': []
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validar campos obrigatórios
            required_fields = ['strategy', 'exchange', 'stake_amount']
            missing_fields = []
            
            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)
                else:
                    result[field] = config[field]
            
            if missing_fields:
                result['issues'].append(f"Campos obrigatórios faltando: {missing_fields}")
            
            # Extrair informações importantes
            result['dry_run'] = config.get('dry_run', True)
            result['stake_amount'] = config.get('stake_amount', 0)
            result['max_open_trades'] = config.get('max_open_trades', 1)
            
            # Validar pares de trading
            pairs_found = False
            if 'pair_whitelist' in config:
                result['pairs'] = config['pair_whitelist']
                pairs_found = True
            elif 'exchange' in config and 'pair_whitelist' in config['exchange']:
                result['pairs'] = config['exchange']['pair_whitelist']
                pairs_found = True
            
            if pairs_found:
                if not result['pairs']:
                    result['issues'].append("Lista de pares vazia")
            else:
                result['issues'].append("pair_whitelist não configurado")
            
            # Validar exchange
            if 'exchange' in config:
                exchange_config = config['exchange']
                if 'name' not in exchange_config:
                    result['issues'].append("Nome da exchange não configurado")
                else:
                    result['exchange'] = exchange_config['name']
            
            # Validações de segurança
            if not result['dry_run']:
                result['issues'].append("⚠️  ATENÇÃO: dry_run=false (modo live)")
            
            if isinstance(result['stake_amount'], (int, float)) and result['stake_amount'] > 100:
                result['issues'].append(f"⚠️  Stake amount alto: {result['stake_amount']} USDT")
            
            if result['max_open_trades'] > 10:
                result['issues'].append(f"⚠️  Muitos trades simultâneos: {result['max_open_trades']}")
            
            if not result['issues']:
                result['valid'] = True
                
        except json.JSONDecodeError as e:
            result['issues'].append(f"JSON inválido: {e}")
        except Exception as e:
            result['issues'].append(f"Erro na validação: {e}")
        
        return result
    
    def find_strategy_config_matches(self) -> Dict[str, Dict]:
        """Encontra correspondências entre estratégias e configurações"""
        matches = {}
        
        for strategy_name, strategy_info in self.results['strategies'].items():
            strategy_class = strategy_info.get('class_name')
            if not strategy_class:
                continue
                
            # Procurar configurações que referenciam esta estratégia
            matching_configs = []
            for config_name, config_info in self.results['configs'].items():
                if config_info.get('strategy') == strategy_class:
                    matching_configs.append(config_name)
            
            matches[strategy_name] = {
                'class_name': strategy_class,
                'configs': matching_configs,
                'has_config': len(matching_configs) > 0
            }
        
        return matches
    
    def validate_all_strategies(self):
        """Valida todas as estratégias"""
        print("🔍 VALIDANDO ESTRATÉGIAS")
        print("-" * 40)
        
        if not self.strategies_path.exists():
            print("❌ Pasta user_data/strategies não encontrada!")
            return
        
        strategy_files = list(self.strategies_path.glob("*.py"))
        if not strategy_files:
            print("❌ Nenhuma estratégia encontrada!")
            return
        
        for strategy_file in strategy_files:
            if strategy_file.name.startswith('__'):
                continue
                
            print(f"📄 Validando {strategy_file.name}...")
            result = self.validate_strategy_file(strategy_file)
            self.results['strategies'][strategy_file.stem] = result
            
            if result['valid']:
                print(f"   ✅ {result['class_name']} - {result.get('timeframe', 'N/A')}")
            else:
                print(f"   ❌ Problemas encontrados:")
                for issue in result['issues']:
                    print(f"      - {issue}")
        
        print()
    
    def validate_all_configs(self):
        """Valida todas as configurações"""
        print("🔍 VALIDANDO CONFIGURAÇÕES")
        print("-" * 40)
        
        if not self.configs_path.exists():
            print("❌ Pasta user_data/configs não encontrada!")
            return
        
        config_files = list(self.configs_path.glob("*.json"))
        if not config_files:
            print("❌ Nenhuma configuração encontrada!")
            return
        
        for config_file in config_files:
            print(f"📄 Validando {config_file.name}...")
            result = self.validate_config_file(config_file)
            self.results['configs'][config_file.stem] = result
            
            if result['valid']:
                dry_status = "DRY-RUN" if result['dry_run'] else "LIVE"
                print(f"   ✅ {result['strategy']} - {result['stake_amount']} USDT ({dry_status})")
            else:
                print(f"   ❌ Problemas encontrados:")
                for issue in result['issues']:
                    print(f"      - {issue}")
        
        print()
    
    def analyze_matches(self):
        """Analisa correspondências entre estratégias e configurações"""
        print("🔗 ANALISANDO CORRESPONDÊNCIAS")
        print("-" * 40)
        
        matches = self.find_strategy_config_matches()
        self.results['matches'] = matches
        
        for strategy_name, match_info in matches.items():
            class_name = match_info['class_name']
            configs = match_info['configs']
            
            if configs:
                print(f"✅ {strategy_name} ({class_name})")
                for config in configs:
                    config_info = self.results['configs'].get(config, {})
                    dry_status = "DRY" if config_info.get('dry_run', True) else "LIVE"
                    stake = config_info.get('stake_amount', 'N/A')
                    print(f"   📋 {config}.json - {stake} USDT ({dry_status})")
            else:
                print(f"❌ {strategy_name} ({class_name}) - SEM CONFIGURAÇÃO")
                self.results['issues'].append(f"Estratégia {strategy_name} sem configuração")
        
        print()
    
    def generate_summary(self):
        """Gera resumo da validação"""
        print("📊 RESUMO DA VALIDAÇÃO")
        print("=" * 50)
        
        total_strategies = len(self.results['strategies'])
        valid_strategies = sum(1 for s in self.results['strategies'].values() if s['valid'])
        
        total_configs = len(self.results['configs'])
        valid_configs = sum(1 for c in self.results['configs'].values() if c['valid'])
        
        matched_strategies = sum(1 for m in self.results['matches'].values() if m['has_config'])
        
        print(f"📈 Estratégias: {valid_strategies}/{total_strategies} válidas")
        print(f"⚙️  Configurações: {valid_configs}/{total_configs} válidas")
        print(f"🔗 Correspondências: {matched_strategies}/{total_strategies} estratégias com config")
        
        # Listar problemas críticos
        critical_issues = [issue for issue in self.results['issues'] if 'SEM CONFIGURAÇÃO' in issue]
        if critical_issues:
            print(f"\n🚨 PROBLEMAS CRÍTICOS ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
        
        # Avisos de segurança
        live_configs = []
        high_stake_configs = []
        
        for config_name, config_info in self.results['configs'].items():
            if not config_info.get('dry_run', True):
                live_configs.append(config_name)
            if isinstance(config_info.get('stake_amount'), (int, float)) and config_info['stake_amount'] > 50:
                high_stake_configs.append((config_name, config_info['stake_amount']))
        
        if live_configs:
            print(f"\n⚠️  CONFIGURAÇÕES EM MODO LIVE ({len(live_configs)}):")
            for config in live_configs:
                print(f"   🔴 {config}.json")
        
        if high_stake_configs:
            print(f"\n💰 STAKES ALTOS ({len(high_stake_configs)}):")
            for config, stake in high_stake_configs:
                print(f"   💸 {config}.json - {stake} USDT")
        
        # Status geral
        print("\n" + "=" * 50)
        if valid_strategies == total_strategies and valid_configs == total_configs and matched_strategies == total_strategies:
            print("🎉 VALIDAÇÃO COMPLETA - SISTEMA PRONTO!")
            return True
        else:
            print("❌ VALIDAÇÃO INCOMPLETA - CORRIJA OS PROBLEMAS")
            return False
    
    def run_validation(self):
        """Executa validação completa"""
        print("🔍 VALIDADOR DE ESTRATÉGIAS - FreqTrade Multi-Strategy")
        print("=" * 60)
        print()
        
        self.validate_all_strategies()
        self.validate_all_configs()
        self.analyze_matches()
        
        return self.generate_summary()

def main():
    """Função principal"""
    try:
        validator = StrategyValidator()
        success = validator.run_validation()
        
        if success:
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("   1. Execute: python optimize_configs.py")
            print("   2. Execute: .\run.ps1 dry")
            print("   3. Execute: .\run.ps1 status")
        else:
            print("\n🔧 CORRIJA OS PROBLEMAS ANTES DE CONTINUAR")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Validação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a validação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Strategy Validator - Sistema de validação de estratégias
Valida sintaxe, lógica, performance e compatibilidade
"""
import importlib.util
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyValidator:
    """
    Validador completo de estratégias Freqtrade
    """

    def __init__(self):
        self.strategies_path = Path("user_data/strategies")
        self.configs_path = Path("user_data/configs")
        self.results = {}

    def validate_all_strategies(self) -> Dict[str, Dict]:
        """
        Validar todas as estratégias disponíveis
        """
        print("🔍 VALIDAÇÃO COMPLETA DE ESTRATÉGIAS")
        print("=" * 60)

        strategy_files = list(self.strategies_path.glob("*.py"))
        strategy_files = [f for f in strategy_files if not f.name.startswith("__")]

        print(f"📊 Encontradas {len(strategy_files)} estratégias para validar")

        for strategy_file in strategy_files:
            strategy_name = strategy_file.stem
            print(f"\n🧪 Validando: {strategy_name}")
            print("-" * 40)

            result = self.validate_strategy(strategy_file)
            self.results[strategy_name] = result

            # Mostrar resultado resumido
            if result['valid']:
                print(f"✅ {strategy_name}: VÁLIDA")
            else:
                print(f"❌ {strategy_name}: INVÁLIDA")
                for error in result['errors']:
                    print(f"   • {error}")

        return self.results

    def validate_strategy(self, strategy_file: Path) -> Dict:
        """
        Validar uma estratégia específica
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {},
            'tests': {}
        }

        strategy_name = strategy_file.stem

        # 1. Validação de sintaxe
        syntax_result = self.validate_syntax(strategy_file)
        result['tests']['syntax'] = syntax_result
        if not syntax_result['passed']:
            result['valid'] = False
            result['errors'].extend(syntax_result['errors'])
            return result  # Se sintaxe falha, não continuar

        # 2. Validação de estrutura
        structure_result = self.validate_structure(strategy_file)
        result['tests']['structure'] = structure_result
        if not structure_result['passed']:
            result['valid'] = False
            result['errors'].extend(structure_result['errors'])

        # 3. Validação de configuração
        config_result = self.validate_config(strategy_name)
        result['tests']['config'] = config_result
        if not config_result['passed']:
            result['warnings'].extend(config_result['warnings'])

        # 4. Validação de lógica
        logic_result = self.validate_logic(strategy_file)
        result['tests']['logic'] = logic_result
        if not logic_result['passed']:
            result['warnings'].extend(logic_result['warnings'])

        # 5. Teste de performance
        performance_result = self.test_performance(strategy_file)
        result['tests']['performance'] = performance_result
        result['metrics'] = performance_result.get('metrics', {})

        return result

    def validate_syntax(self, strategy_file: Path) -> Dict:
        """
        Validar sintaxe Python da estratégia
        """
        result = {'passed': True, 'errors': []}

        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                code = f.read()

            # Compilar código para verificar sintaxe
            compile(code, str(strategy_file), 'exec')
            print("   ✅ Sintaxe Python válida")

        except SyntaxError as e:
            result['passed'] = False
            result['errors'].append(f"Erro de sintaxe linha {e.lineno}: {e.msg}")
            print(f"   ❌ Erro de sintaxe: {e.msg}")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Erro de compilação: {str(e)}")
            print(f"   ❌ Erro de compilação: {e}")

        return result

    def validate_structure(self, strategy_file: Path) -> Dict:
        """
        Validar estrutura da classe de estratégia
        """
        result = {'passed': True, 'errors': [], 'warnings': []}

        try:
            # Importar módulo dinamicamente
            spec = importlib.util.spec_from_file_location("strategy_module", strategy_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Encontrar classe de estratégia
            strategy_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                    hasattr(obj, 'populate_indicators') and
                    hasattr(obj, 'populate_entry_trend')):
                    strategy_class = obj
                    break

            if not strategy_class:
                result['passed'] = False
                result['errors'].append("Classe de estratégia não encontrada")
                return result

            print(f"   ✅ Classe encontrada: {strategy_class.__name__}")

            # Verificar métodos obrigatórios
            required_methods = [
                'populate_indicators',
                'populate_entry_trend',
                'populate_exit_trend'
            ]

            for method in required_methods:
                if not hasattr(strategy_class, method):
                    result['passed'] = False
                    result['errors'].append(f"Método obrigatório '{method}' não encontrado")
                else:
                    print(f"   ✅ Método {method} presente")

            # Verificar atributos obrigatórios
            required_attrs = ['timeframe', 'stoploss']
            for attr in required_attrs:
                if not hasattr(strategy_class, attr):
                    result['warnings'].append(f"Atributo recomendado '{attr}' não encontrado")
                else:
                    print(f"   ✅ Atributo {attr} presente")

            # Verificar INTERFACE_VERSION
            if hasattr(strategy_class, 'INTERFACE_VERSION'):
                version = strategy_class.INTERFACE_VERSION
                if version < 3:
                    result['warnings'].append(f"INTERFACE_VERSION {version} é antiga, recomendado >= 3")
                else:
                    print(f"   ✅ INTERFACE_VERSION: {version}")
            else:
                result['warnings'].append("INTERFACE_VERSION não definida")

        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Erro ao importar estratégia: {str(e)}")
            print(f"   ❌ Erro de importação: {e}")

        return result

    def validate_config(self, strategy_name: str) -> Dict:
        """
        Validar arquivo de configuração da estratégia
        """
        result = {'passed': True, 'warnings': []}

        # Procurar arquivo de config
        possible_configs = [
            self.configs_path / f"{strategy_name.lower()}.json",
            self.configs_path / f"{strategy_name}.json",
        ]

        config_file = None
        for config_path in possible_configs:
            if config_path.exists():
                config_file = config_path
                break

        if not config_file:
            result['passed'] = False
            result['warnings'].append("Arquivo de configuração não encontrado")
            print("   ⚠️ Config não encontrado")
            return result

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            print(f"   ✅ Config carregado: {config_file.name}")

            # Verificar campos essenciais
            essential_fields = [
                'stake_currency', 'stake_amount', 'dry_run',
                'exchange', 'telegram'
            ]

            for field in essential_fields:
                if field not in config:
                    result['warnings'].append(f"Campo '{field}' não encontrado no config")
                else:
                    print(f"   ✅ Campo {field} presente")

            # Verificar configurações específicas
            if 'exchange' in config:
                exchange_config = config['exchange']
                if 'pair_whitelist' not in exchange_config:
                    result['warnings'].append("pair_whitelist não definida")
                else:
                    pairs_count = len(exchange_config['pair_whitelist'])
                    print(f"   ✅ {pairs_count} pares configurados")

            if 'max_open_trades' in config:
                max_trades = config['max_open_trades']
                if max_trades > 10:
                    result['warnings'].append(f"max_open_trades muito alto: {max_trades}")
                else:
                    print(f"   ✅ max_open_trades: {max_trades}")

        except json.JSONDecodeError as e:
            result['passed'] = False
            result['warnings'].append(f"JSON inválido: {str(e)}")
            print(f"   ❌ JSON inválido: {e}")
        except Exception as e:
            result['passed'] = False
            result['warnings'].append(f"Erro ao ler config: {str(e)}")
            print(f"   ❌ Erro no config: {e}")

        return result

    def validate_logic(self, strategy_file: Path) -> Dict:
        """
        Validar lógica da estratégia
        """
        result = {'passed': True, 'warnings': []}

        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                code = f.read()

            # Verificações básicas de lógica
            checks = [
                ('enter_long', 'Sinais de entrada'),
                ('exit_long', 'Sinais de saída'),
                ('dataframe', 'Uso de dataframe'),
                ('volume', 'Consideração de volume'),
            ]

            for check, description in checks:
                if check in code:
                    print(f"   ✅ {description} implementado")
                else:
                    result['warnings'].append(f"{description} pode estar faltando")

            # Verificar uso de proteções
            if 'protections' in code or 'StoplossGuard' in code:
                print("   ✅ Proteções implementadas")
            else:
                result['warnings'].append("Proteções não implementadas")

            # Verificar trailing stop
            if 'trailing_stop' in code:
                print("   ✅ Trailing stop configurado")
            else:
                result['warnings'].append("Trailing stop não configurado")

        except Exception as e:
            result['passed'] = False
            result['warnings'].append(f"Erro na validação de lógica: {str(e)}")

        return result

    def test_performance(self, strategy_file: Path) -> Dict:
        """
        Testar performance da estratégia com dados sintéticos
        """
        result = {'passed': True, 'metrics': {}, 'warnings': []}

        try:
            # Importar estratégia
            spec = importlib.util.spec_from_file_location("strategy_module", strategy_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Encontrar classe
            strategy_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                    hasattr(obj, 'populate_indicators')):
                    strategy_class = obj
                    break

            if not strategy_class:
                result['passed'] = False
                result['warnings'].append("Classe de estratégia não encontrada para teste")
                return result

            # Criar dados sintéticos
            test_data = self.create_test_data(500)

            # Instanciar estratégia (mock config)
            mock_config = {'stake_currency': 'USDT', 'dry_run': True}

            try:
                strategy = strategy_class(mock_config)
            except Exception as e:
                result['warnings'].append(f"Erro ao instanciar estratégia: {str(e)}")
                return result

            # Testar populate_indicators
            start_time = datetime.now()
            try:
                df_with_indicators = strategy.populate_indicators(test_data, {'pair': 'BTC/USDT'})
                indicators_time = (datetime.now() - start_time).total_seconds()

                result['metrics']['indicators_time'] = indicators_time
                result['metrics']['indicators_count'] = len(df_with_indicators.columns) - len(test_data.columns)

                print(f"   ✅ Indicadores: {result['metrics']['indicators_count']} em {indicators_time:.3f}s")

            except Exception as e:
                result['warnings'].append(f"Erro em populate_indicators: {str(e)}")
                return result

            # Testar populate_entry_trend
            start_time = datetime.now()
            try:
                df_with_entry = strategy.populate_entry_trend(df_with_indicators, {'pair': 'BTC/USDT'})
                entry_time = (datetime.now() - start_time).total_seconds()

                entry_signals = df_with_entry.get('enter_long', pd.Series(0)).sum()
                result['metrics']['entry_time'] = entry_time
                result['metrics']['entry_signals'] = int(entry_signals)

                print(f"   ✅ Entrada: {entry_signals} sinais em {entry_time:.3f}s")

            except Exception as e:
                result['warnings'].append(f"Erro em populate_entry_trend: {str(e)}")
                return result

            # Testar populate_exit_trend
            start_time = datetime.now()
            try:
                df_with_exit = strategy.populate_exit_trend(df_with_entry, {'pair': 'BTC/USDT'})
                exit_time = (datetime.now() - start_time).total_seconds()

                exit_signals = df_with_exit.get('exit_long', pd.Series(0)).sum()
                result['metrics']['exit_time'] = exit_time
                result['metrics']['exit_signals'] = int(exit_signals)

                print(f"   ✅ Saída: {exit_signals} sinais em {exit_time:.3f}s")

            except Exception as e:
                result['warnings'].append(f"Erro em populate_exit_trend: {str(e)}")
                return result

            # Métricas de qualidade
            total_candles = len(test_data)
            entry_rate = (entry_signals / total_candles) * 100 if total_candles > 0 else 0
            exit_rate = (exit_signals / total_candles) * 100 if total_candles > 0 else 0

            result['metrics']['entry_rate'] = round(entry_rate, 2)
            result['metrics']['exit_rate'] = round(exit_rate, 2)
            result['metrics']['total_time'] = round(indicators_time + entry_time + exit_time, 3)

            # Avaliar qualidade
            if entry_rate > 20:
                result['warnings'].append(f"Taxa de entrada muito alta: {entry_rate:.1f}%")
            elif entry_rate < 0.5:
                result['warnings'].append(f"Taxa de entrada muito baixa: {entry_rate:.1f}%")

            if result['metrics']['total_time'] > 2.0:
                result['warnings'].append(f"Processamento lento: {result['metrics']['total_time']}s")

            print(f"   📊 Taxa entrada: {entry_rate:.1f}%, Taxa saída: {exit_rate:.1f}%")

        except Exception as e:
            result['passed'] = False
            result['warnings'].append(f"Erro no teste de performance: {str(e)}")

        return result

    def create_test_data(self, length: int = 500) -> pd.DataFrame:
        """
        Criar dados sintéticos para teste
        """
        np.random.seed(42)

        dates = pd.date_range('2023-01-01', periods=length, freq='5min')

        # Preços com tendência e ruído
        trend = np.linspace(100, 120, length)
        noise = np.random.normal(0, 2, length)
        close = trend + noise

        # OHLC
        high = close + np.random.uniform(0, 2, length)
        low = close - np.random.uniform(0, 2, length)
        open_price = np.roll(close, 1)
        open_price[0] = close[0]

        # Volume
        volume = np.random.uniform(1000, 10000, length)

        return pd.DataFrame({
            'date': dates,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    def generate_report(self) -> str:
        """
        Gerar relatório de validação
        """
        if not self.results:
            return "Nenhuma validação executada"

        report = []
        report.append("📋 RELATÓRIO DE VALIDAÇÃO DE ESTRATÉGIAS")
        report.append("=" * 60)

        total_strategies = len(self.results)
        valid_strategies = sum(1 for r in self.results.values() if r['valid'])

        report.append(f"📊 Resumo: {valid_strategies}/{total_strategies} estratégias válidas")
        report.append("")

        for strategy_name, result in self.results.items():
            status = "✅ VÁLIDA" if result['valid'] else "❌ INVÁLIDA"
            report.append(f"🔍 {strategy_name}: {status}")

            # Métricas de performance
            if 'metrics' in result and result['metrics']:
                metrics = result['metrics']
                report.append(f"   📊 Métricas:")
                if 'indicators_count' in metrics:
                    report.append(f"      • Indicadores: {metrics['indicators_count']}")
                if 'entry_signals' in metrics:
                    report.append(f"      • Sinais entrada: {metrics['entry_signals']} ({metrics.get('entry_rate', 0)}%)")
                if 'exit_signals' in metrics:
                    report.append(f"      • Sinais saída: {metrics['exit_signals']} ({metrics.get('exit_rate', 0)}%)")
                if 'total_time' in metrics:
                    report.append(f"      • Tempo processamento: {metrics['total_time']}s")

            # Erros
            if result['errors']:
                report.append(f"   ❌ Erros:")
                for error in result['errors']:
                    report.append(f"      • {error}")

            # Warnings
            if result['warnings']:
                report.append(f"   ⚠️ Avisos:")
                for warning in result['warnings']:
                    report.append(f"      • {warning}")

            report.append("")

        return "\n".join(report)

    def save_report(self, filename: str = None):
        """
        Salvar relatório em arquivo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_validation_report_{timestamp}.txt"

        report = self.generate_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 Relatório salvo em: {filename}")

def main():
    """
    Função principal
    """
    validator = StrategyValidator()

    # Validar todas as estratégias
    results = validator.validate_all_strategies()

    # Mostrar relatório
    print("\n" + "=" * 60)
    report = validator.generate_report()
    print(report)

    # Salvar relatório
    validator.save_report()

    # Status de saída
    valid_count = sum(1 for r in results.values() if r['valid'])
    total_count = len(results)

    if valid_count == total_count:
        print(f"\n🎉 Todas as {total_count} estratégias são válidas!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total_count - valid_count} estratégias com problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()

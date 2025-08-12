#!/usr/bin/env python3
"""
Teste automatizado de todas as estratégias
"""
import os
import sys
from pathlib import Path

# Adicionar path dos scripts
sys.path.append('scripts')

def main():
    """
    Executar validação de todas as estratégias
    """
    print("🚀 TESTE AUTOMATIZADO DE TODAS AS ESTRATÉGIAS")
    print("=" * 60)

    try:
        from strategy_validator import StrategyValidator

        validator = StrategyValidator()
        results = validator.validate_all_strategies()

        # Relatório final
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL")
        print("=" * 60)

        total = len(results)
        valid = sum(1 for r in results.values() if r['valid'])

        print(f"📊 Total de estratégias: {total}")
        print(f"✅ Estratégias válidas: {valid}")
        print(f"❌ Estratégias com problemas: {total - valid}")

        if valid == total:
            print("\n🎉 TODAS AS ESTRATÉGIAS SÃO VÁLIDAS!")
            return True
        else:
            print(f"\n⚠️ {total - valid} ESTRATÉGIAS PRECISAM DE ATENÇÃO")

            # Mostrar problemas
            for name, result in results.items():
                if not result['valid']:
                    print(f"\n❌ {name}:")
                    for error in result['errors']:
                        print(f"   • {error}")

            return False

    except ImportError as e:
        print(f"❌ Erro ao importar validador: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

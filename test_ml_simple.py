#!/usr/bin/env python3
"""
Teste da MLStrategySimple - Validação da estratégia ML simplificada
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Adicionar path das estratégias
sys.path.append('user_data/strategies')

def create_sample_data(length=500):
    """Criar dados de exemplo para teste"""
    np.random.seed(42)

    # Gerar dados OHLCV sintéticos
    dates = pd.date_range('2023-01-01', periods=length, freq='5T')

    # Preços com tendência e ruído
    trend = np.linspace(100, 120, length)
    noise = np.random.normal(0, 2, length)
    close = trend + noise

    # OHLC baseado no close
    high = close + np.random.uniform(0, 2, length)
    low = close - np.random.uniform(0, 2, length)
    open_price = np.roll(close, 1)
    open_price[0] = close[0]

    # Volume sintético
    volume = np.random.uniform(1000, 10000, length)

    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })

    return df

def test_dependencies():
    """Testar dependências"""
    print("🔍 TESTE DE DEPENDÊNCIAS")
    print("=" * 40)

    deps_ok = True

    try:
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
    except ImportError:
        print("❌ pandas não disponível")
        deps_ok = False

    try:
        import numpy as np
        print(f"✅ numpy: {np.__version__}")
    except ImportError:
        print("❌ numpy não disponível")
        deps_ok = False

    try:
        import sklearn
        print(f"✅ scikit-learn: {sklearn.__version__}")
    except ImportError:
        print("⚠️ scikit-learn não disponível (usará fallback)")

    return deps_ok

def test_strategy():
    """Testar a estratégia ML simplificada"""
    print("\n🧪 TESTE DA ML STRATEGY SIMPLE")
    print("=" * 40)

    try:
        from MLStrategySimple import MLStrategySimple
        print("✅ MLStrategySimple importada com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar MLStrategySimple: {e}")
        return False

    # Criar instância da estratégia
    config = {
        'stake_currency': 'USDT',
        'dry_run': True
    }

    try:
        strategy = MLStrategySimple(config)
        print("✅ Estratégia inicializada")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

    # Criar dados de teste
    print("📊 Criando dados de teste...")
    dataframe = create_sample_data(300)

    # Testar indicadores nativos
    print("🔍 Testando indicadores nativos...")
    try:
        # Testar RSI
        rsi = strategy.rsi(dataframe['close'])
        print(f"✅ RSI - Min: {rsi.min():.2f}, Max: {rsi.max():.2f}")

        # Testar EMA
        ema = strategy.ema(dataframe['close'], 20)
        print(f"✅ EMA - Últimos valores: {ema.tail(3).values}")

        # Testar MACD
        macd_line, signal_line, histogram = strategy.macd(dataframe['close'])
        print(f"✅ MACD - Linha: {macd_line.iloc[-1]:.4f}")

        # Testar Bollinger Bands
        bb_upper, bb_middle, bb_lower = strategy.bollinger_bands(dataframe['close'])
        print(f"✅ Bollinger Bands - Largura: {(bb_upper.iloc[-1] - bb_lower.iloc[-1]):.4f}")

    except Exception as e:
        print(f"❌ Erro nos indicadores nativos: {e}")
        return False

    # Testar populate_indicators
    print("🔍 Testando populate_indicators...")
    try:
        df_with_indicators = strategy.populate_indicators(dataframe, {'pair': 'BTC/USDT'})
        print(f"✅ Indicadores calculados - Shape: {df_with_indicators.shape}")

        # Verificar colunas essenciais
        required_cols = ['rsi', 'macd', 'bb_percent', 'ml_prediction']
        missing_cols = [col for col in required_cols if col not in df_with_indicators.columns]

        if missing_cols:
            print(f"⚠️ Colunas faltando: {missing_cols}")
        else:
            print("✅ Todas as colunas essenciais presentes")

    except Exception as e:
        print(f"❌ Erro em populate_indicators: {e}")
        return False

    # Testar sinais de entrada
    print("📈 Testando sinais de entrada...")
    try:
        df_with_entry = strategy.populate_entry_trend(df_with_indicators, {'pair': 'BTC/USDT'})
        entry_signals = df_with_entry['enter_long'].sum()
        print(f"✅ Sinais de entrada: {entry_signals}")

        if entry_signals > 0:
            print("✅ Estratégia gerando sinais de entrada")
            # Mostrar alguns exemplos
            entry_rows = df_with_entry[df_with_entry['enter_long'] == 1]
            if len(entry_rows) > 0:
                print(f"   Exemplo - RSI: {entry_rows['rsi'].iloc[0]:.2f}, BB%: {entry_rows['bb_percent'].iloc[0]:.3f}")
        else:
            print("⚠️ Nenhum sinal de entrada gerado")

    except Exception as e:
        print(f"❌ Erro em populate_entry_trend: {e}")
        return False

    # Testar sinais de saída
    print("📉 Testando sinais de saída...")
    try:
        df_with_exit = strategy.populate_exit_trend(df_with_entry, {'pair': 'BTC/USDT'})
        exit_signals = df_with_exit['exit_long'].sum()
        print(f"✅ Sinais de saída: {exit_signals}")

    except Exception as e:
        print(f"❌ Erro em populate_exit_trend: {e}")
        return False

    # Verificar predições ML
    print("🤖 Verificando predições ML...")
    if 'ml_prediction' in df_with_exit.columns:
        ml_predictions = df_with_exit['ml_prediction']
        avg_prediction = ml_predictions.mean()
        max_prediction = ml_predictions.max()
        min_prediction = ml_predictions.min()

        print(f"✅ Predições ML - Média: {avg_prediction:.3f}, Min: {min_prediction:.3f}, Max: {max_prediction:.3f}")

        if strategy.model is not None:
            print("✅ Modelo ML treinado e funcionando")
        else:
            print("⚠️ Usando fallback técnico")

    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Total de candles: {len(df_with_exit)}")
    print(f"   • Sinais de entrada: {df_with_exit['enter_long'].sum()}")
    print(f"   • Sinais de saída: {df_with_exit['exit_long'].sum()}")
    print(f"   • Colunas geradas: {len(df_with_exit.columns)}")
    print(f"   • NaN values: {df_with_exit.isna().sum().sum()}")

    return True

if __name__ == "__main__":
    print("🚀 TESTE DA ML STRATEGY SIMPLE")
    print("=" * 50)

    # Teste de dependências
    deps_ok = test_dependencies()

    # Teste da estratégia
    strategy_ok = test_strategy()

    # Resultado final
    print("\n" + "=" * 50)
    if deps_ok and strategy_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ MLStrategySimple está pronta para uso")
        sys.exit(0)
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Verifique os erros acima")
        sys.exit(1)

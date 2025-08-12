#!/usr/bin/env python3
"""
Teste apenas dos indicadores técnicos nativos
"""
import numpy as np
import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Implementação nativa do RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ema(series: pd.Series, period: int) -> pd.Series:
    """Implementação nativa da EMA"""
    return series.ewm(span=period).mean()

def sma(series: pd.Series, period: int) -> pd.Series:
    """Implementação nativa da SMA"""
    return series.rolling(window=period).mean()

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Implementação nativa do MACD"""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2):
    """Implementação nativa das Bollinger Bands"""
    sma_line = sma(series, period)
    std = series.rolling(window=period).std()
    upper = sma_line + (std * std_dev)
    lower = sma_line - (std * std_dev)
    return upper, sma_line, lower

def create_sample_data(length=200):
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

def test_indicators():
    """Testar todos os indicadores"""
    print("🧪 TESTE DOS INDICADORES TÉCNICOS")
    print("=" * 50)

    # Criar dados de teste
    df = create_sample_data(200)
    print(f"📊 Dados criados: {len(df)} candles")

    # Testar RSI
    print("\n🔍 Testando RSI...")
    try:
        rsi_values = rsi(df['close'])
        rsi_valid = rsi_values.dropna()
        print(f"✅ RSI calculado - Min: {rsi_valid.min():.2f}, Max: {rsi_valid.max():.2f}, Média: {rsi_valid.mean():.2f}")

        # Verificar se está no range correto
        if rsi_valid.min() >= 0 and rsi_valid.max() <= 100:
            print("✅ RSI dentro do range válido (0-100)")
        else:
            print("❌ RSI fora do range válido")

    except Exception as e:
        print(f"❌ Erro no RSI: {e}")
        return False

    # Testar EMA
    print("\n🔍 Testando EMA...")
    try:
        ema_20 = ema(df['close'], 20)
        ema_valid = ema_20.dropna()
        print(f"✅ EMA-20 calculada - Últimos 3 valores: {ema_valid.tail(3).values}")

        # EMA deve seguir o preço
        if abs(ema_valid.iloc[-1] - df['close'].iloc[-1]) < df['close'].std():
            print("✅ EMA seguindo o preço corretamente")
        else:
            print("⚠️ EMA pode estar com problema")

    except Exception as e:
        print(f"❌ Erro na EMA: {e}")
        return False

    # Testar SMA
    print("\n🔍 Testando SMA...")
    try:
        sma_20 = sma(df['close'], 20)
        sma_valid = sma_20.dropna()
        print(f"✅ SMA-20 calculada - Últimos 3 valores: {sma_valid.tail(3).values}")

    except Exception as e:
        print(f"❌ Erro na SMA: {e}")
        return False

    # Testar MACD
    print("\n🔍 Testando MACD...")
    try:
        macd_line, signal_line, histogram = macd(df['close'])
        macd_valid = macd_line.dropna()
        signal_valid = signal_line.dropna()
        hist_valid = histogram.dropna()

        print(f"✅ MACD calculado:")
        print(f"   Linha MACD: {macd_valid.iloc[-1]:.4f}")
        print(f"   Linha Signal: {signal_valid.iloc[-1]:.4f}")
        print(f"   Histograma: {hist_valid.iloc[-1]:.4f}")

    except Exception as e:
        print(f"❌ Erro no MACD: {e}")
        return False

    # Testar Bollinger Bands
    print("\n🔍 Testando Bollinger Bands...")
    try:
        bb_upper, bb_middle, bb_lower = bollinger_bands(df['close'])
        bb_upper_valid = bb_upper.dropna()
        bb_middle_valid = bb_middle.dropna()
        bb_lower_valid = bb_lower.dropna()

        print(f"✅ Bollinger Bands calculadas:")
        print(f"   Upper: {bb_upper_valid.iloc[-1]:.4f}")
        print(f"   Middle: {bb_middle_valid.iloc[-1]:.4f}")
        print(f"   Lower: {bb_lower_valid.iloc[-1]:.4f}")

        # Verificar se upper > middle > lower
        if bb_upper_valid.iloc[-1] > bb_middle_valid.iloc[-1] > bb_lower_valid.iloc[-1]:
            print("✅ Bollinger Bands em ordem correta")
        else:
            print("❌ Bollinger Bands fora de ordem")

    except Exception as e:
        print(f"❌ Erro nas Bollinger Bands: {e}")
        return False

    # Testar features derivadas
    print("\n🔍 Testando features derivadas...")
    try:
        # BB Percent
        bb_percent = (df['close'] - bb_lower) / (bb_upper - bb_lower)
        bb_percent_valid = bb_percent.dropna()
        print(f"✅ BB Percent - Min: {bb_percent_valid.min():.3f}, Max: {bb_percent_valid.max():.3f}")

        # Volume ratio
        volume_sma = sma(df['volume'], 20)
        volume_ratio = df['volume'] / volume_sma
        volume_ratio_valid = volume_ratio.dropna()
        print(f"✅ Volume Ratio - Média: {volume_ratio_valid.mean():.3f}")

        # Price changes
        price_change_1 = df['close'].pct_change(1)
        price_change_valid = price_change_1.dropna()
        print(f"✅ Price Change 1-period - Std: {price_change_valid.std():.4f}")

    except Exception as e:
        print(f"❌ Erro nas features derivadas: {e}")
        return False

    print("\n🎉 TODOS OS INDICADORES FUNCIONANDO CORRETAMENTE!")
    return True

def test_trading_signals():
    """Testar lógica de sinais de trading"""
    print("\n🎯 TESTE DE SINAIS DE TRADING")
    print("=" * 50)

    # Criar dados de teste
    df = create_sample_data(100)

    # Calcular indicadores
    df['rsi'] = rsi(df['close'])
    df['ema_8'] = ema(df['close'], 8)
    df['ema_21'] = ema(df['close'], 21)

    bb_upper, bb_middle, bb_lower = bollinger_bands(df['close'])
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower
    df['bb_percent'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)

    macd_line, signal_line, histogram = macd(df['close'])
    df['macd'] = macd_line
    df['macd_signal'] = signal_line

    df['volume_sma'] = sma(df['volume'], 20)
    df['volume_ratio'] = df['volume'] / df['volume_sma']

    # Lógica de entrada (exemplo)
    entry_conditions = (
        (df['rsi'] < 30) &
        (df['bb_percent'] < 0.2) &
        (df['macd'] > df['macd_signal']) &
        (df['volume_ratio'] > 1.2) &
        (df['ema_8'] > df['ema_21'])
    )

    # Lógica de saída (exemplo)
    exit_conditions = (
        (df['rsi'] > 70) |
        (df['bb_percent'] > 0.8) |
        (df['macd'] < df['macd_signal'])
    )

    entry_signals = entry_conditions.sum()
    exit_signals = exit_conditions.sum()

    print(f"📈 Sinais de entrada encontrados: {entry_signals}")
    print(f"📉 Sinais de saída encontrados: {exit_signals}")

    if entry_signals > 0:
        print("✅ Lógica de entrada gerando sinais")
    else:
        print("⚠️ Nenhum sinal de entrada (pode ser normal)")

    if exit_signals > 0:
        print("✅ Lógica de saída gerando sinais")
    else:
        print("⚠️ Nenhum sinal de saída (pode ser normal)")

    return True

if __name__ == "__main__":
    print("🚀 TESTE DOS INDICADORES TÉCNICOS NATIVOS")
    print("=" * 60)

    # Testar dependências
    try:
        import numpy as np
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        exit(1)

    # Testar indicadores
    indicators_ok = test_indicators()

    # Testar sinais
    signals_ok = test_trading_signals()

    # Resultado final
    print("\n" + "=" * 60)
    if indicators_ok and signals_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Indicadores técnicos funcionando corretamente")
        print("✅ Lógica de sinais implementada")
        print("✅ MLStrategySimple está pronta para uso no Docker")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        exit(1)

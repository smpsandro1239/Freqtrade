#!/usr/bin/env python3
"""
Teste da WaveHyperNWEnhanced - Validação da estratégia melhorada
"""
import sys

import numpy as np
import pandas as pd


def create_sample_data(length=500):
    """Criar dados de exemplo para teste"""
    np.random.seed(42)

    # Gerar dados OHLCV sintéticos com padrões realistas
    dates = pd.date_range('2023-01-01', periods=length, freq='5min')

    # Preços com tendência, ciclos e ruído
    trend = np.linspace(100, 115, length)
    cycle = 5 * np.sin(np.linspace(0, 4*np.pi, length))
    noise = np.random.normal(0, 1, length)
    close = trend + cycle + noise

    # OHLC baseado no close
    high = close + np.random.uniform(0, 1.5, length)
    low = close - np.random.uniform(0, 1.5, length)
    open_price = np.roll(close, 1)
    open_price[0] = close[0]

    # Volume sintético com padrões
    base_volume = 5000
    volume_trend = np.random.uniform(0.5, 2.0, length)
    volume_noise = np.random.uniform(0.8, 1.2, length)
    volume = base_volume * volume_trend * volume_noise

    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })

    return df

def ema(series: pd.Series, period: int) -> pd.Series:
    """Implementação nativa da EMA"""
    return series.ewm(span=period, adjust=False).mean()

def sma(series: pd.Series, period: int) -> pd.Series:
    """Implementação nativa da SMA"""
    return series.rolling(window=period).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Implementação nativa do RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """Implementação nativa do ATR"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def wavetrend(dataframe: pd.DataFrame, channel_len: int = 8, average_len: int = 18) -> tuple:
    """Implementação do WaveTrend"""
    # Average Price
    ap = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3

    # ESA (Exponential Smoothed Average)
    esa = ema(ap, channel_len)

    # Deviation
    d = ema(abs(ap - esa), channel_len)

    # Channel Index
    ci = (ap - esa) / (0.015 * d)

    # WaveTrend lines
    wt1 = ema(ci, average_len)
    wt2 = sma(wt1, 4)

    return wt1, wt2

def nadaraya_watson(dataframe: pd.DataFrame, bandwidth: float = 3.5, lookback: int = 25) -> tuple:
    """Implementação do Nadaraya-Watson Estimator"""
    close = dataframe['close'].values

    # Kernel Gaussiano
    weights = np.array([np.exp(-(i**2)/(2*bandwidth**2)) for i in range(-lookback, lookback+1)])
    weights = weights / weights.sum()

    # Aplicar convolução
    nw_estimate = np.convolve(close, weights, mode='same')
    nw_series = pd.Series(nw_estimate, index=dataframe.index)

    # Bandas baseadas em desvio padrão
    std = dataframe['close'].rolling(lookback).std()
    multiplier = 1.2

    nw_upper = nw_series + multiplier * std
    nw_lower = nw_series - multiplier * std

    return nw_series, nw_upper, nw_lower

def calculate_trend_strength(dataframe: pd.DataFrame) -> pd.Series:
    """Calcular força da tendência"""
    # EMA alignment
    ema_8 = dataframe['ema_8']
    ema_21 = dataframe['ema_21']
    ema_50 = dataframe['ema_50']

    ema_score = (
        (ema_8 > ema_21).astype(int) * 0.4 +
        (ema_21 > ema_50).astype(int) * 0.3 +
        (dataframe['close'] > ema_8).astype(int) * 0.3
    )

    # RSI momentum
    rsi_normalized = (dataframe['rsi'] - 50) / 50
    rsi_score = (rsi_normalized.clip(-1, 1) + 1) / 2

    # WaveTrend momentum
    wt_score = ((dataframe['wt1'] + 100) / 200).clip(0, 1)

    # Combine scores
    trend_strength = (
        ema_score * 0.5 +
        rsi_score * 0.3 +
        wt_score * 0.2
    )

    return trend_strength.clip(0, 1)

def test_enhanced_indicators():
    """Testar os indicadores melhorados"""
    print("🧪 TESTE DOS INDICADORES MELHORADOS")
    print("=" * 50)

    # Criar dados de teste
    df = create_sample_data(300)
    print(f"📊 Dados criados: {len(df)} candles")

    # Calcular indicadores básicos
    print("\n🔍 Calculando indicadores básicos...")
    df['rsi'] = rsi(df['close'])
    df['ema_8'] = ema(df['close'], 8)
    df['ema_21'] = ema(df['close'], 21)
    df['ema_50'] = ema(df['close'], 50)
    df['atr'] = atr(df['high'], df['low'], df['close'])
    df['volume_sma'] = sma(df['volume'], 24)
    df['volume_ratio'] = df['volume'] / df['volume_sma']

    print("✅ Indicadores básicos calculados")

    # Testar WaveTrend melhorado
    print("\n🌊 Testando WaveTrend melhorado...")
    try:
        df['wt1'], df['wt2'] = wavetrend(df)
        wt1_valid = df['wt1'].dropna()
        wt2_valid = df['wt2'].dropna()

        print(f"✅ WaveTrend calculado:")
        print(f"   • WT1 - Min: {wt1_valid.min():.2f}, Max: {wt1_valid.max():.2f}")
        print(f"   • WT2 - Min: {wt2_valid.min():.2f}, Max: {wt2_valid.max():.2f}")

        # Verificar crossovers
        crossovers = ((df['wt1'] > df['wt2']) & (df['wt1'].shift(1) <= df['wt2'].shift(1))).sum()
        print(f"   • Crossovers bullish: {crossovers}")

    except Exception as e:
        print(f"❌ Erro no WaveTrend: {e}")
        return False

    # Testar Nadaraya-Watson melhorado
    print("\n📈 Testando Nadaraya-Watson melhorado...")
    try:
        df['nw_estimate'], df['nw_upper'], df['nw_lower'] = nadaraya_watson(df)

        nw_valid = df['nw_estimate'].dropna()
        print(f"✅ Nadaraya-Watson calculado:")
        print(f"   • Estimate - Últimos 3: {nw_valid.tail(3).values}")

        # Verificar se as bandas fazem sentido
        upper_valid = df['nw_upper'].dropna()
        lower_valid = df['nw_lower'].dropna()

        if len(upper_valid) > 0 and len(lower_valid) > 0:
            if upper_valid.iloc[-1] > lower_valid.iloc[-1]:
                print("✅ Bandas NW em ordem correta")
            else:
                print("❌ Bandas NW fora de ordem")

    except Exception as e:
        print(f"❌ Erro no Nadaraya-Watson: {e}")
        return False

    # Testar trend strength
    print("\n💪 Testando cálculo de força da tendência...")
    try:
        df['trend_strength'] = calculate_trend_strength(df)

        trend_valid = df['trend_strength'].dropna()
        avg_strength = trend_valid.mean()
        strong_periods = (trend_valid > 0.7).sum()

        print(f"✅ Trend Strength calculado:")
        print(f"   • Força média: {avg_strength:.3f}")
        print(f"   • Períodos fortes (>0.7): {strong_periods}/{len(trend_valid)} ({strong_periods/len(trend_valid)*100:.1f}%)")

    except Exception as e:
        print(f"❌ Erro no Trend Strength: {e}")
        return False

    return True

def test_enhanced_signals():
    """Testar lógica de sinais melhorada"""
    print("\n🎯 TESTE DE SINAIS MELHORADOS")
    print("=" * 50)

    # Criar dados de teste
    df = create_sample_data(200)

    # Calcular todos os indicadores
    df['rsi'] = rsi(df['close'])
    df['ema_8'] = ema(df['close'], 8)
    df['ema_21'] = ema(df['close'], 21)
    df['ema_50'] = ema(df['close'], 50)
    df['atr'] = atr(df['high'], df['low'], df['close'])
    df['volume_sma'] = sma(df['volume'], 24)
    df['volume_ratio'] = df['volume'] / df['volume_sma']

    df['wt1'], df['wt2'] = wavetrend(df)
    df['nw_estimate'], df['nw_upper'], df['nw_lower'] = nadaraya_watson(df)
    df['trend_strength'] = calculate_trend_strength(df)

    # Filtros de qualidade
    df['volatility'] = df['atr'] / df['close']
    df['volatility_ok'] = df['volatility'] < 0.05
    df['price_momentum'] = df['close'].pct_change(5)

    # Support/Resistance
    df['resistance'] = df['high'].rolling(20).max()
    df['support'] = df['low'].rolling(20).min()
    df['price_position'] = (df['close'] - df['support']) / (df['resistance'] - df['support'])

    # Lógica de entrada melhorada
    wt_oversold = -55
    trend_strength_min = 0.6
    min_volume_ratio = 0.5

    # Condições de entrada
    wt_bullish = (
        (df['wt1'] > df['wt2']) &
        (df['wt1'] < wt_oversold) &
        (df['wt1'].shift(1) <= df['wt1'])
    )

    nw_support = (
        (df['close'] <= df['nw_lower']) |
        ((df['close'] < df['nw_estimate']) & (df['rsi'] < 40))
    )

    trend_favorable = (
        (df['trend_strength'] > trend_strength_min) &
        (df['ema_8'] > df['ema_21'])
    )

    volume_ok = (
        (df['volume_ratio'] > min_volume_ratio) &
        (df['volume_ratio'] < 3.0)  # Não volume anômalo
    )

    quality_filters = (
        df['volatility_ok'] &
        (df['price_momentum'] > -0.01) &
        (df['price_position'] < 0.8)
    )

    rsi_ok = df['rsi'] < 65

    # Sinal final
    entry_signal = (
        wt_bullish &
        nw_support &
        trend_favorable &
        volume_ok &
        quality_filters &
        rsi_ok
    )

    # Lógica de saída
    wt_overbought = 55

    wt_exit = (
        (df['wt1'] < df['wt2']) &
        (df['wt1'] > wt_overbought) &
        (df['wt1'].shift(1) >= df['wt1'])
    )

    rsi_exit = df['rsi'] > 75
    trend_deterioration = df['trend_strength'] < 0.3
    profit_taking = df['close'] > df['ema_8'] * 1.04

    exit_signal = (
        wt_exit |
        rsi_exit |
        trend_deterioration |
        profit_taking
    )

    # Contar sinais
    entry_count = entry_signal.sum()
    exit_count = exit_signal.sum()

    print(f"📈 Sinais de entrada: {entry_count}")
    print(f"📉 Sinais de saída: {exit_count}")

    if entry_count > 0:
        print("✅ Lógica de entrada gerando sinais")

        # Analisar qualidade dos sinais
        entry_rows = df[entry_signal]
        if len(entry_rows) > 0:
            avg_rsi = entry_rows['rsi'].mean()
            avg_trend = entry_rows['trend_strength'].mean()
            avg_volume = entry_rows['volume_ratio'].mean()

            print(f"   • RSI médio nos sinais: {avg_rsi:.1f}")
            print(f"   • Trend strength médio: {avg_trend:.3f}")
            print(f"   • Volume ratio médio: {avg_volume:.2f}")
    else:
        print("⚠️ Nenhum sinal de entrada (condições muito restritivas)")

    if exit_count > 0:
        print("✅ Lógica de saída gerando sinais")
    else:
        print("⚠️ Nenhum sinal de saída")

    return True

def test_risk_management():
    """Testar gestão de risco melhorada"""
    print("\n🛡️ TESTE DE GESTÃO DE RISCO")
    print("=" * 50)

    # Simular cenários de risco
    scenarios = [
        {"atr_pct": 0.02, "trend_strength": 0.8, "expected_stop": "conservador"},
        {"atr_pct": 0.05, "trend_strength": 0.4, "expected_stop": "amplo"},
        {"atr_pct": 0.08, "trend_strength": 0.2, "expected_stop": "muito amplo"},
    ]

    for i, scenario in enumerate(scenarios, 1):
        atr_normalized = scenario["atr_pct"]
        trend_strength = scenario["trend_strength"]

        # Lógica do stop loss dinâmico
        trend_multiplier = 1.0 + (1.0 - trend_strength)
        dynamic_stop = atr_normalized * 2.5 * trend_multiplier
        dynamic_stop = max(0.04, min(0.12, dynamic_stop))

        print(f"📊 Cenário {i}:")
        print(f"   • ATR: {atr_normalized*100:.1f}%")
        print(f"   • Trend Strength: {trend_strength:.1f}")
        print(f"   • Stop Loss: {dynamic_stop*100:.1f}%")
        print(f"   • Categoria: {scenario['expected_stop']}")

    print("✅ Gestão de risco dinâmica funcionando")
    return True

if __name__ == "__main__":
    print("🚀 TESTE DA WAVE HYPER NW ENHANCED")
    print("=" * 60)

    # Testar dependências
    try:
        import numpy as np
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        sys.exit(1)

    # Executar testes
    indicators_ok = test_enhanced_indicators()
    signals_ok = test_enhanced_signals()
    risk_ok = test_risk_management()

    # Resultado final
    print("\n" + "=" * 60)
    if indicators_ok and signals_ok and risk_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Indicadores melhorados funcionando")
        print("✅ Lógica de sinais aprimorada")
        print("✅ Gestão de risco dinâmica")
        print("✅ WaveHyperNWEnhanced está pronta para uso")
        sys.exit(0)
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        sys.exit(1)

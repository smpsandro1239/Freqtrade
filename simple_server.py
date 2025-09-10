#!/usr/bin/env python3
"""
Servidor HTTP simples para indicadores
"""

import http.server
import json
import socketserver
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import numpy as np


class IndicatorsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

        try:
            if path == '/api/health':
                response = {
                    'status': 'ok',
                    'timestamp': datetime.now().isoformat(),
                    'server': 'simple_server'
                }
            elif path == '/api/strategies':
                response = [
                    'MLStrategy',
                    'WaveHyperNWStrategy',
                    'SampleStrategyA',
                    'combined'
                ]
            elif path == '/api/stats':
                response = self.generate_stats()
            elif path.startswith('/api/trades'):
                limit = int(query.get('limit', [10])[0])
                response = self.generate_trades(limit)
            elif path.startswith('/api/ohlcv'):
                pair = 'BTC/USDT'  # Default
                timeframe = '5m'   # Default
                limit = 200
                if '/api/ohlcv/' in path:
                    parts = path.split('/')
                    if len(parts) >= 4:
                        pair = parts[3]
                        timeframe = parts[4] if len(parts) > 4 else '5m'
                limit = int(query.get('limit', [limit])[0])
                response = self.generate_ohlcv(pair, timeframe, limit)
            else:
                response = {
                    'message': 'Freqtrade Mock Server Running!',
                    'endpoints': [
                        '/api/health',
                        '/api/strategies',
                        '/api/stats',
                        '/api/trades?limit=10',
                        '/api/ohlcv/{pair}/{timeframe}?limit=200'
                    ]
                }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error_response = {'error': str(e), 'status': 'error'}
            self.wfile.write(json.dumps(error_response).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
        except:
            data = {}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

        try:
            if path == '/api/login':
                username = data.get('username', '')
                password = data.get('password', '')
                if username == 'admin' and password == 'admin123':
                    response = {'token': 'dummy_jwt_token_12345'}
                else:
                    self.send_response(401)
                    response = {'error': 'Invalid credentials'}
                self.wfile.write(json.dumps(response).encode())
                return
            else:
                self.send_response(404)
                response = {'error': 'Endpoint not found'}
                self.wfile.write(json.dumps(response).encode())
                return

        except Exception as e:
            error_response = {'error': str(e), 'status': 'error'}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def generate_stats(self):
        """Gera estatísticas mock do Freqtrade"""
        return {
            'total_trades': 156,
            'open_trades': 3,
            'win_rate': 67.3,
            'total_profit': 245.78,
            'daily_profit': 12.45,
            'best_pair': 'BTC/USDT',
            'worst_pair': 'ADA/USDT',
            'timestamp': datetime.now().isoformat()
        }

    def generate_trades(self, limit=10):
        """Gera trades mock"""
        trades = []
        now = datetime.now()
        for i in range(limit):
            timestamp = now - timedelta(hours=i*2)
            profit = np.random.uniform(-0.05, 0.15)
            trades.append({
                'id': i+1,
                'pair': np.random.choice(['BTC/USDT', 'ETH/USDT', 'ADA/USDT']),
                'strategy': np.random.choice(['MLStrategy', 'WaveHyperNWStrategy', 'SampleStrategyA']),
                'amount': round(np.random.uniform(50, 200), 2),
                'open_date': timestamp.isoformat(),
                'close_date': (timestamp + timedelta(hours=np.random.uniform(1, 24))).isoformat(),
                'profit_ratio': profit,
                'profit_abs': round(profit * 100, 2),
                'status': 'closed' if profit != 0 else 'open'
            })
        return {'trades': trades, 'total': len(trades)}

    def generate_ohlcv(self, pair, timeframe, limit=200):
        """Gera dados OHLCV e indicadores compatíveis com Freqtrade"""
        # Gerar velas
        candles = []
        now = datetime.now()
        price = 45000 + np.random.normal(0, 2000)
        volume_base = 1000 + np.random.normal(0, 500)

        for i in range(limit):
            timestamp = now - timedelta(minutes=5*(limit-i))
            change = np.random.normal(0, price * 0.005)
            open_price = price
            close_price = price + change
            high_price = max(open_price, close_price) + abs(np.random.normal(0, price * 0.003))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, price * 0.003))
            volume = volume_base + np.random.normal(0, 200)

            candles.append({
                'timestamp': int(timestamp.timestamp() * 1000),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 2)
            })

            price = close_price
            volume_base += np.random.normal(0, 50)

        # Calcular indicadores
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]

        # RSI (14)
        rsi = self.calculate_rsi(closes, 14)

        # MACD
        macd, signal, histogram = self.calculate_macd(closes)

        # EMAs
        ema_8 = self.calculate_ema(closes, 8)
        ema_21 = self.calculate_ema(closes, 21)
        ema_50 = self.calculate_ema(closes, 50)

        # SMAs
        sma_20 = self.calculate_sma(closes, 20)
        sma_50 = self.calculate_sma(closes, 50)

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes, 20)

        # ATR
        atr = self.calculate_atr(highs, lows, closes, 14)

        # Pad arrays to match length
        def pad_array(arr, length):
            return arr + [arr[-1]] * (length - len(arr))

        indicators = {
            'rsi': pad_array(rsi, limit),
            'macd': pad_array(macd, limit),
            'macd_signal': pad_array(signal, limit),
            'macd_histogram': pad_array(histogram, limit),
            'ema_8': pad_array(ema_8, limit),
            'ema_21': pad_array(ema_21, limit),
            'ema_50': pad_array(ema_50, limit),
            'sma_20': pad_array(sma_20, limit),
            'sma_50': pad_array(sma_50, limit),
            'bb_upper': pad_array(bb_upper, limit),
            'bb_middle': pad_array(bb_middle, limit),
            'bb_lower': pad_array(bb_lower, limit),
            'atr': pad_array(atr, limit)
        }

        return {
            'ohlcv': candles,
            'indicators': indicators,
            'pair': pair,
            'timeframe': timeframe,
            'last_update': datetime.now().isoformat(),
            'status': 'success'
        }

    def calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = [100 - (100 / (1 + rs))]
        for i in range(period, len(prices)):
            gain = gains[i-1] if i-1 < len(gains) else 0
            loss = losses[i-1] if i-1 < len(losses) else 0
            avg_gain = (avg_gain * (period-1) + gain) / period
            avg_loss = (avg_loss * (period-1) + loss) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi.append(100 - (100 / (1 + rs)))
        return rsi

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcula MACD"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = self.calculate_ema(macd, signal)
        histogram = [m - s for m, s in zip(macd, signal_line)]
        return macd, signal_line, histogram

    def calculate_ema(self, prices, period):
        """Calcula EMA"""
        multiplier = 2 / (period + 1)
        ema = [prices[0]]
        for price in prices[1:]:
            ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))
        return ema

    def calculate_sma(self, prices, period):
        """Calcula SMA"""
        sma = []
        for i in range(len(prices)):
            if i < period - 1:
                sma.append(None)
            else:
                sma.append(np.mean(prices[i-period+1:i+1]))
        return [s if s is not None else prices[i] for i, s in enumerate(sma)]

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calcula Bollinger Bands"""
        sma = self.calculate_sma(prices, period)
        upper = []
        middle = []
        lower = []
        for i in range(len(prices)):
            if i < period - 1:
                upper.append(prices[i])
                middle.append(prices[i])
                lower.append(prices[i])
            else:
                std = np.std(prices[i-period+1:i+1])
                middle.append(sma[i])
                upper.append(sma[i] + (std * std_dev))
                lower.append(sma[i] - (std * std_dev))
        return upper, middle, lower

    def calculate_atr(self, highs, lows, closes, period=14):
        """Calcula ATR"""
        trs = [highs[0] - lows[0]]
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            trs.append(max(tr1, tr2, tr3))
        atr = self.calculate_sma(trs, period)
        return atr

if __name__ == '__main__':
    PORT = 5000

    print("Starting simple indicators server...")
    print(f"Server: http://localhost:{PORT}")
    print(f"Health: http://localhost:{PORT}/api/health")
    print(f"Strategies: http://localhost:{PORT}/api/strategies")
    print(f"Indicators: http://localhost:{PORT}/api/indicators/waveHyperNW")
    print()

    try:
        with socketserver.TCPServer(("", PORT), IndicatorsHandler) as httpd:
            print(f"Server running on port {PORT}")
            print("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")

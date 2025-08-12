#!/usr/bin/env python3
"""
Dashboard API - API REST para Dashboard Web
Fornece dados para gráficos multi-timeframe e indicadores
"""
import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import jwt
import numpy as np
import pandas as pd
import redis
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuração
app = Flask(__name__)
CORS(app)
limiter = Limiter(
    app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)

# Configurações
SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "your-secret-key-change-this")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DB_PATH = "/freqtrade/user_data/tradesv3.sqlite"

app.config["SECRET_KEY"] = SECRET_KEY

# Redis connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
except:
    redis_client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardAPI:
    """API para Dashboard Web"""

    def __init__(self):
        self.users = {
            "admin": self.hash_password("admin123"),  # Altere esta senha!
            "trader": self.hash_password("trader123"),
        }

    def hash_password(self, password: str) -> str:
        """Hash da senha"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, username: str, password: str) -> bool:
        """Verificar senha"""
        if username not in self.users:
            return False
        return self.users[username] == self.hash_password(password)

    def generate_token(self, username: str) -> str:
        """Gerar JWT token"""
        payload = {"username": username, "exp": datetime.utcnow() + timedelta(hours=24)}
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[str]:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["username"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_ohlcv_data(self, pair: str, timeframe: str, limit: int = 500) -> List[Dict]:
        """Obter dados OHLCV do banco"""
        try:
            conn = sqlite3.connect(DB_PATH)

            # Query para obter dados OHLCV
            query = """
            SELECT date, open, high, low, close, volume
            FROM pair_locks
            WHERE pair = ?
            ORDER BY date DESC
            LIMIT ?
            """

            df = pd.read_sql_query(query, conn, params=(pair, limit))
            conn.close()

            # Converter para formato esperado pelo frontend
            data = []
            for _, row in df.iterrows():
                data.append(
                    {
                        "timestamp": int(row["date"]),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"]),
                    }
                )

            return list(reversed(data))  # Ordem cronológica

        except Exception as e:
            logger.error(f"Erro ao obter dados OHLCV: {e}")
            return []

    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calcular todos os indicadores"""
        indicators = {}

        if len(df) < 50:
            return indicators

        try:
            # RSI
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators["rsi"] = (100 - (100 / (1 + rs))).tolist()

            # EMAs
            indicators["ema_8"] = df["close"].ewm(span=8).mean().tolist()
            indicators["ema_21"] = df["close"].ewm(span=21).mean().tolist()
            indicators["ema_50"] = df["close"].ewm(span=50).mean().tolist()

            # SMAs
            indicators["sma_20"] = df["close"].rolling(20).mean().tolist()
            indicators["sma_50"] = df["close"].rolling(50).mean().tolist()

            # MACD
            ema_12 = df["close"].ewm(span=12).mean()
            ema_26 = df["close"].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()

            indicators["macd"] = macd_line.tolist()
            indicators["macd_signal"] = signal_line.tolist()
            indicators["macd_histogram"] = (macd_line - signal_line).tolist()

            # Bollinger Bands
            sma_20 = df["close"].rolling(20).mean()
            std_20 = df["close"].rolling(20).std()
            indicators["bb_upper"] = (sma_20 + 2 * std_20).tolist()
            indicators["bb_middle"] = sma_20.tolist()
            indicators["bb_lower"] = (sma_20 - 2 * std_20).tolist()

            # Volume
            indicators["volume_sma"] = df["volume"].rolling(20).mean().tolist()

            # ATR
            high_low = df["high"] - df["low"]
            high_close = np.abs(df["high"] - df["close"].shift())
            low_close = np.abs(df["low"] - df["close"].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            indicators["atr"] = true_range.rolling(14).mean().tolist()

        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {e}")

        return indicators

    def get_trades_data(self, limit: int = 100) -> List[Dict]:
        """Obter dados de trades"""
        try:
            conn = sqlite3.connect(DB_PATH)

            query = """
            SELECT pair, is_open, open_date, close_date, open_rate, close_rate,
                   amount, stake_amount, profit_abs, profit_ratio, strategy
            FROM trades
            ORDER BY open_date DESC
            LIMIT ?
            """

            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()

            trades = []
            for _, row in df.iterrows():
                trades.append(
                    {
                        "pair": row["pair"],
                        "is_open": bool(row["is_open"]),
                        "open_date": row["open_date"],
                        "close_date": row["close_date"],
                        "open_rate": (
                            float(row["open_rate"]) if row["open_rate"] else None
                        ),
                        "close_rate": (
                            float(row["close_rate"]) if row["close_rate"] else None
                        ),
                        "amount": float(row["amount"]) if row["amount"] else None,
                        "stake_amount": (
                            float(row["stake_amount"]) if row["stake_amount"] else None
                        ),
                        "profit_abs": (
                            float(row["profit_abs"]) if row["profit_abs"] else None
                        ),
                        "profit_ratio": (
                            float(row["profit_ratio"]) if row["profit_ratio"] else None
                        ),
                        "strategy": row["strategy"],
                    }
                )

            return trades

        except Exception as e:
            logger.error(f"Erro ao obter trades: {e}")
            return []


# Instância da API
dashboard_api = DashboardAPI()


# Middleware de autenticação
def require_auth(f):
    """Decorator para exigir autenticação"""

    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token não fornecido"}), 401

        if token.startswith("Bearer "):
            token = token[7:]

        username = dashboard_api.verify_token(token)
        if not username:
            return jsonify({"error": "Token inválido"}), 401

        request.current_user = username
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Rotas da API


@app.route("/")
def dashboard():
    """Página principal do dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Login endpoint"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username e password obrigatórios"}), 400

    if dashboard_api.verify_password(username, password):
        token = dashboard_api.generate_token(username)
        return jsonify(
            {"token": token, "username": username, "expires_in": 24 * 3600}  # 24 horas
        )
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401


@app.route("/api/pairs")
@require_auth
def get_pairs():
    """Obter lista de pares disponíveis"""
    # Lista padrão de pares (pode ser obtida do banco)
    pairs = [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "ADA/USDT",
        "DOT/USDT",
        "LINK/USDT",
        "SOL/USDT",
        "MATIC/USDT",
        "AVAX/USDT",
        "ATOM/USDT",
        "LTC/USDT",
        "XRP/USDT",
    ]
    return jsonify({"pairs": pairs})


@app.route("/api/ohlcv/<pair>/<timeframe>")
@require_auth
def get_ohlcv(pair, timeframe):
    """Obter dados OHLCV com indicadores"""
    limit = request.args.get("limit", 500, type=int)

    # Obter dados OHLCV
    ohlcv_data = dashboard_api.get_ohlcv_data(pair, timeframe, limit)

    if not ohlcv_data:
        return jsonify({"error": "Dados não encontrados"}), 404

    # Converter para DataFrame para calcular indicadores
    df = pd.DataFrame(ohlcv_data)

    # Calcular indicadores
    indicators = dashboard_api.calculate_indicators(df)

    return jsonify(
        {
            "pair": pair,
            "timeframe": timeframe,
            "ohlcv": ohlcv_data,
            "indicators": indicators,
        }
    )


@app.route("/api/trades")
@require_auth
def get_trades():
    """Obter histórico de trades"""
    limit = request.args.get("limit", 100, type=int)
    trades = dashboard_api.get_trades_data(limit)

    return jsonify({"trades": trades})


@app.route("/api/stats")
@require_auth
def get_stats():
    """Obter estatísticas gerais"""
    trades = dashboard_api.get_trades_data(1000)

    if not trades:
        return jsonify({"error": "Nenhum trade encontrado"}), 404

    # Calcular estatísticas
    total_trades = len(trades)
    open_trades = len([t for t in trades if t["is_open"]])
    closed_trades = total_trades - open_trades

    profitable_trades = len(
        [
            t
            for t in trades
            if not t["is_open"] and t["profit_abs"] and t["profit_abs"] > 0
        ]
    )
    win_rate = (profitable_trades / closed_trades * 100) if closed_trades > 0 else 0

    total_profit = sum([t["profit_abs"] for t in trades if t["profit_abs"]])

    stats = {
        "total_trades": total_trades,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "win_rate": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "profitable_trades": profitable_trades,
    }

    return jsonify(stats)


@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": redis_client is not None,
        }
    )


# HTML do Dashboard (será criado em arquivo separado)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Freqtrade Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .login-form { max-width: 400px; margin: 100px auto; padding: 20px; background: #2a2a2a; border-radius: 8px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #444; background: #333; color: white; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .dashboard { display: none; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #2a2a2a; padding: 20px; border-radius: 8px; text-align: center; }
        .chart-container { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .controls { margin-bottom: 20px; }
        .controls select { padding: 8px; margin-right: 10px; background: #333; color: white; border: 1px solid #444; }
        .error { color: #ff4444; text-align: center; margin: 10px 0; }
        .success { color: #44ff44; text-align: center; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Form -->
        <div id="loginForm" class="login-form">
            <h2 style="text-align: center;">Freqtrade Dashboard</h2>
            <div class="form-group">
                <label>Username:</label>
                <input type="text" id="username" placeholder="Digite seu username">
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" id="password" placeholder="Digite sua senha">
            </div>
            <button class="btn" onclick="login()" style="width: 100%;">Login</button>
            <div id="loginError" class="error"></div>
        </div>

        <!-- Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="header">
                <h1>Freqtrade Multi-Strategy Dashboard</h1>
                <button class="btn" onclick="logout()">Logout</button>
            </div>

            <!-- Stats -->
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Trades</h3>
                    <div id="totalTrades">-</div>
                </div>
                <div class="stat-card">
                    <h3>Trades Abertos</h3>
                    <div id="openTrades">-</div>
                </div>
                <div class="stat-card">
                    <h3>Win Rate</h3>
                    <div id="winRate">-</div>
                </div>
                <div class="stat-card">
                    <h3>Profit Total</h3>
                    <div id="totalProfit">-</div>
                </div>
            </div>

            <!-- Controls -->
            <div class="controls">
                <select id="pairSelect">
                    <option value="">Selecione um par</option>
                </select>
                <select id="timeframeSelect">
                    <option value="1m">1 Minuto</option>
                    <option value="5m" selected>5 Minutos</option>
                    <option value="15m">15 Minutos</option>
                    <option value="1h">1 Hora</option>
                    <option value="4h">4 Horas</option>
                    <option value="1d">1 Dia</option>
                </select>
                <button class="btn" onclick="loadChart()">Carregar Gráfico</button>
            </div>

            <!-- Chart -->
            <div class="chart-container">
                <canvas id="priceChart" width="400" height="200"></canvas>
            </div>

            <!-- Indicators Chart -->
            <div class="chart-container">
                <canvas id="indicatorsChart" width="400" height="150"></canvas>
            </div>
        </div>
    </div>

    <script>
        let authToken = localStorage.getItem('authToken');
        let priceChart = null;
        let indicatorsChart = null;

        // Check if already logged in
        if (authToken) {
            showDashboard();
        }

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('loginError');

            if (!username || !password) {
                errorDiv.textContent = 'Username e password são obrigatórios';
                return;
            }

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    authToken = data.token;
                    localStorage.setItem('authToken', authToken);
                    showDashboard();
                } else {
                    errorDiv.textContent = data.error || 'Erro no login';
                }
            } catch (error) {
                errorDiv.textContent = 'Erro de conexão';
            }
        }

        function logout() {
            authToken = null;
            localStorage.removeItem('authToken');
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
        }

        async function showDashboard() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';

            await loadPairs();
            await loadStats();
        }

        async function apiCall(endpoint) {
            const response = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });

            if (response.status === 401) {
                logout();
                return null;
            }

            return response.json();
        }

        async function loadPairs() {
            const data = await apiCall('/api/pairs');
            if (data) {
                const select = document.getElementById('pairSelect');
                data.pairs.forEach(pair => {
                    const option = document.createElement('option');
                    option.value = pair;
                    option.textContent = pair;
                    select.appendChild(option);
                });
            }
        }

        async function loadStats() {
            const data = await apiCall('/api/stats');
            if (data) {
                document.getElementById('totalTrades').textContent = data.total_trades;
                document.getElementById('openTrades').textContent = data.open_trades;
                document.getElementById('winRate').textContent = data.win_rate + '%';
                document.getElementById('totalProfit').textContent = data.total_profit + ' USDT';
            }
        }

        async function loadChart() {
            const pair = document.getElementById('pairSelect').value;
            const timeframe = document.getElementById('timeframeSelect').value;

            if (!pair) {
                alert('Selecione um par');
                return;
            }

            const data = await apiCall(`/api/ohlcv/${pair}/${timeframe}`);
            if (data) {
                createPriceChart(data);
                createIndicatorsChart(data);
            }
        }

        function createPriceChart(data) {
            const ctx = document.getElementById('priceChart').getContext('2d');

            if (priceChart) {
                priceChart.destroy();
            }

            const candleData = data.ohlcv.map(candle => ({
                x: candle.timestamp,
                o: candle.open,
                h: candle.high,
                l: candle.low,
                c: candle.close
            }));

            priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Preço',
                        data: data.ohlcv.map(candle => ({
                            x: candle.timestamp,
                            y: candle.close
                        })),
                        borderColor: '#00ff00',
                        backgroundColor: 'rgba(0, 255, 0, 0.1)',
                        fill: false
                    }, {
                        label: 'EMA 8',
                        data: data.indicators.ema_8?.map((value, index) => ({
                            x: data.ohlcv[index].timestamp,
                            y: value
                        })) || [],
                        borderColor: '#ff0000',
                        fill: false
                    }, {
                        label: 'EMA 21',
                        data: data.indicators.ema_21?.map((value, index) => ({
                            x: data.ohlcv[index].timestamp,
                            y: value
                        })) || [],
                        borderColor: '#0000ff',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: 'time',
                            time: { unit: 'minute' }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: `${data.pair} - ${data.timeframe}`
                        }
                    }
                }
            });
        }

        function createIndicatorsChart(data) {
            const ctx = document.getElementById('indicatorsChart').getContext('2d');

            if (indicatorsChart) {
                indicatorsChart.destroy();
            }

            indicatorsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'RSI',
                        data: data.indicators.rsi?.map((value, index) => ({
                            x: data.ohlcv[index].timestamp,
                            y: value
                        })) || [],
                        borderColor: '#ffff00',
                        yAxisID: 'y1'
                    }, {
                        label: 'MACD',
                        data: data.indicators.macd?.map((value, index) => ({
                            x: data.ohlcv[index].timestamp,
                            y: value
                        })) || [],
                        borderColor: '#ff00ff',
                        yAxisID: 'y2'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: 'time',
                            time: { unit: 'minute' }
                        },
                        y1: {
                            type: 'linear',
                            position: 'left',
                            min: 0,
                            max: 100
                        },
                        y2: {
                            type: 'linear',
                            position: 'right'
                        }
                    }
                }
            });
        }

        // Auto-refresh stats every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

# Rotas da API


@app.route("/")
def dashboard():
    """Página principal do dashboard"""
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return render_template_string(DASHBOARD_HTML)


@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Login endpoint"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username e password obrigatórios"}), 400

    if dashboard_api.verify_password(username, password):
        token = dashboard_api.generate_token(username)
        return jsonify(
            {"token": token, "username": username, "expires_in": 24 * 3600}  # 24 horas
        )
    else:
        return jsonify({"error": "Credenciais inválidas"}), 401


@app.route("/api/pairs")
@require_auth
def get_pairs():
    """Obter lista de pares disponíveis"""
    # Lista padrão de pares (pode ser obtida do banco)
    pairs = [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "ADA/USDT",
        "DOT/USDT",
        "LINK/USDT",
        "SOL/USDT",
        "MATIC/USDT",
        "AVAX/USDT",
        "ATOM/USDT",
        "LTC/USDT",
        "XRP/USDT",
    ]
    return jsonify({"pairs": pairs})


@app.route("/api/ohlcv/<pair>/<timeframe>")
@require_auth
def get_ohlcv(pair, timeframe):
    """Obter dados OHLCV com indicadores"""
    limit = request.args.get("limit", 500, type=int)

    # Obter dados OHLCV
    ohlcv_data = dashboard_api.get_ohlcv_data(pair, timeframe, limit)

    if not ohlcv_data:
        return jsonify({"error": "Dados não encontrados"}), 404

    # Converter para DataFrame para calcular indicadores
    df = pd.DataFrame(ohlcv_data)

    # Calcular indicadores
    indicators = dashboard_api.calculate_indicators(df)

    return jsonify(
        {
            "pair": pair,
            "timeframe": timeframe,
            "ohlcv": ohlcv_data,
            "indicators": indicators,
        }
    )


@app.route("/api/trades")
@require_auth
def get_trades():
    """Obter histórico de trades"""
    limit = request.args.get("limit", 100, type=int)
    trades = dashboard_api.get_trades_data(limit)

    return jsonify({"trades": trades})


@app.route("/api/stats")
@require_auth
def get_stats():
    """Obter estatísticas gerais"""
    trades = dashboard_api.get_trades_data(1000)

    if not trades:
        return jsonify({"error": "Nenhum trade encontrado"}), 404

    # Calcular estatísticas
    total_trades = len(trades)
    open_trades = len([t for t in trades if t["is_open"]])
    closed_trades = total_trades - open_trades

    profitable_trades = len(
        [
            t
            for t in trades
            if not t["is_open"] and t["profit_abs"] and t["profit_abs"] > 0
        ]
    )
    win_rate = (profitable_trades / closed_trades * 100) if closed_trades > 0 else 0

    total_profit = sum([t["profit_abs"] for t in trades if t["profit_abs"]])

    stats = {
        "total_trades": total_trades,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "win_rate": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "profitable_trades": profitable_trades,
    }

    return jsonify(stats)


@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": redis_client is not None,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

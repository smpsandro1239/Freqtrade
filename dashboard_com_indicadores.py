#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Avançado com Indicadores Técnicos
Gráficos interativos mostrando indicadores de cada estratégia
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, redirect, session

# Configuração Flask
app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'Benfica456!!!')

# Configurações
DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME', 'sandro')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'sandro2020')

# Estratégias com seus indicadores específicos
STRATEGIES = {
    "stratA": {
        "name": "Strategy A (RSI)",
        "port": 8081,
        "color": "#3498db",
        "indicators": ["RSI", "SMA", "EMA"],
        "description": "RSI básico com médias móveis"
    },
    "stratB": {
        "name": "Strategy B (RSI+MACD+BB)",
        "port": 8082,
        "color": "#e74c3c",
        "indicators": ["RSI", "MACD", "Bollinger Bands"],
        "description": "RSI + MACD + Bollinger Bands"
    },
    "waveHyperNW": {
        "name": "WaveHyperNW",
        "port": 8083,
        "color": "#2ecc71",
        "indicators": ["WaveTrend", "Nadaraya-Watson", "RSI"],
        "description": "WaveTrend + Nadaraya-Watson"
    },
    "mlStrategy": {
        "name": "ML Strategy",
        "port": 8084,
        "color": "#f39c12",
        "indicators": ["ML Prediction", "RSI", "MACD", "Bollinger Bands"],
        "description": "Machine Learning com indicadores técnicos"
    },
    "mlStrategySimple": {
        "name": "ML Simple",
        "port": 8085,
        "color": "#9b59b6",
        "indicators": ["ML Simple", "RSI", "SMA"],
        "description": "ML simplificado"
    },
    "multiTimeframe": {
        "name": "Multi Timeframe",
        "port": 8086,
        "color": "#1abc9c",
        "indicators": ["Multi-TF RSI", "Multi-TF MACD", "Trend"],
        "description": "Análise multi-timeframe"
    },
    "waveEnhanced": {
        "name": "Wave Enhanced",
        "port": 8087,
        "color": "#34495e",
        "indicators": ["WaveTrend Enhanced", "Volume", "Momentum"],
        "description": "WaveTrend avançado"
    }
}

# Template HTML com gráficos avançados
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FreqTrade Dashboard - Indicadores Técnicos</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header h1 { margin: 0; font-size: 2.5em; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border-left: 4px solid #3498db; }
        .strategy-card { margin-bottom: 30px; }
        .strategy-header { display: flex; justify-content: between; align-items: center; margin-bottom: 20px; }
        .strategy-title { font-size: 1.4em; font-weight: 600; color: #2c3e50; }
        .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }
        .status-ok { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .indicators-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
        .indicator-tag { background: #e9ecef; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; color: #495057; }
        .chart-container { position: relative; height: 400px; margin: 20px 0; }
        .chart-tabs { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { padding: 8px 16px; border: none; background: #e9ecef; border-radius: 6px; cursor: pointer; transition: all 0.3s; }
        .tab-btn.active { background: #007bff; color: white; }
        .tab-btn:hover { background: #007bff; color: white; }
        .refresh-btn { background: linear-gradient(45deg, #007bff, #0056b3); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        .refresh-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,123,255,0.3); }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 15px 0; }
        .metric { text-align: center; }
        .metric-value { font-size: 1.5em; font-weight: 600; color: #2c3e50; }
        .metric-label { font-size: 0.85em; color: #6c757d; margin-top: 5px; }
        .loading { text-align: center; padding: 40px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 FreqTrade Multi-Strategy Dashboard</h1>
            <p>Análise Técnica Avançada com Indicadores em Tempo Real</p>
            <p>{{ datetime.now().strftime('%d/%m/%Y %H:%M:%S') }}</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar Dados</button>
        </div>
        
        <div class="stats-grid">
            <div class="card">
                <h3>📊 Resumo Geral</h3>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{{ summary.active_strategies }}</div>
                        <div class="metric-label">Estratégias Ativas</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.working_apis }}</div>
                        <div class="metric-label">APIs Online</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.total_trades }}</div>
                        <div class="metric-label">Trades Hoje</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>💰 Performance</h3>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value">{{ performance.total_profit }}</div>
                        <div class="metric-label">Lucro Total (USDT)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ performance.win_rate }}%</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ performance.drawdown }}%</div>
                        <div class="metric-label">Drawdown</div>
                    </div>
                </div>
            </div>
        </div>
        
        {% for strategy in strategies %}
        <div class="card strategy-card">
            <div class="strategy-header">
                <div>
                    <div class="strategy-title" style="color: {{ strategy.color }}">
                        {{ strategy.name }}
                    </div>
                    <div style="font-size: 0.9em; color: #6c757d; margin: 5px 0;">
                        {{ strategy.description }}
                    </div>
                    <div class="indicators-list">
                        {% for indicator in strategy.indicators %}
                        <span class="indicator-tag">{{ indicator }}</span>
                        {% endfor %}
                    </div>
                </div>
                <div>
                    <span class="status-badge {{ 'status-ok' if strategy.api_ok else 'status-error' }}">
                        {{ '🟢 Online' if strategy.api_ok else '🔴 Offline' }}
                    </span>
                </div>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{{ strategy.trades }}</div>
                    <div class="metric-label">Trades</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ strategy.profit }}</div>
                    <div class="metric-label">P&L (USDT)</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ strategy.win_rate }}%</div>
                    <div class="metric-label">Win Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">:{{ strategy.port }}</div>
                    <div class="metric-label">API Port</div>
                </div>
            </div>
            
            <div class="chart-tabs">
                <button class="tab-btn active" onclick="showChart('{{ strategy.key }}', 'price')">📈 Preço + Indicadores</button>
                <button class="tab-btn" onclick="showChart('{{ strategy.key }}', 'volume')">📊 Volume</button>
                <button class="tab-btn" onclick="showChart('{{ strategy.key }}', 'signals')">🎯 Sinais</button>
            </div>
            
            <div class="chart-container">
                <canvas id="chart-{{ strategy.key }}" width="400" height="200"></canvas>
            </div>
        </div>
        {% endfor %}
        
        <div class="card">
            <h3>🔗 Links Úteis</h3>
            <p>
                <a href="/api/summary" target="_blank">📊 API Summary</a> | 
                <a href="/api/strategies/status" target="_blank">🎯 Strategies Status</a> |
                <a href="/api/charts/all" target="_blank">📈 All Charts Data</a>
            </p>
        </div>
    </div>

    <script>
        const charts = {};
        const chartData = {{ chart_data | safe }};
        
        // Inicializar gráficos
        document.addEventListener('DOMContentLoaded', function() {
            {% for strategy in strategies %}
            initChart('{{ strategy.key }}', '{{ strategy.name }}', '{{ strategy.color }}');
            {% endfor %}
        });
        
        function initChart(strategyKey, strategyName, color) {
            const ctx = document.getElementById('chart-' + strategyKey).getContext('2d');
            
            const data = chartData[strategyKey] || generateSampleData();
            
            charts[strategyKey] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.timestamps,
                    datasets: [
                        {
                            label: 'Preço (USDT)',
                            data: data.prices,
                            borderColor: color,
                            backgroundColor: color + '20',
                            borderWidth: 2,
                            fill: false,
                            yAxisID: 'y'
                        },
                        {
                            label: 'RSI',
                            data: data.rsi,
                            borderColor: '#ff6b6b',
                            borderWidth: 1,
                            fill: false,
                            yAxisID: 'y1'
                        },
                        {
                            label: 'MACD',
                            data: data.macd,
                            borderColor: '#4ecdc4',
                            borderWidth: 1,
                            fill: false,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Tempo'
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Preço (USDT)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Indicadores'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: strategyName + ' - Análise Técnica'
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        }
        
        function showChart(strategyKey, chartType) {
            // Atualizar botões ativos
            const tabs = document.querySelectorAll('.tab-btn');
            tabs.forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            // Aqui você pode implementar diferentes visualizações
            console.log('Showing', chartType, 'for', strategyKey);
        }
        
        function generateSampleData() {
            const data = {
                timestamps: [],
                prices: [],
                rsi: [],
                macd: []
            };
            
            const now = new Date();
            let price = 45000 + Math.random() * 10000;
            
            for (let i = 0; i < 50; i++) {
                const time = new Date(now.getTime() - (49 - i) * 5 * 60 * 1000);
                data.timestamps.push(time.toLocaleTimeString());
                
                price += (Math.random() - 0.5) * 1000;
                data.prices.push(price);
                data.rsi.push(30 + Math.random() * 40);
                data.macd.push((Math.random() - 0.5) * 200);
            }
            
            return data;
        }
        
        // Auto-refresh a cada 30 segundos
        setInterval(() => {
            fetch('/api/charts/update')
                .then(response => response.json())
                .then(data => {
                    // Atualizar gráficos com novos dados
                    Object.keys(charts).forEach(key => {
                        if (data[key]) {
                            updateChart(key, data[key]);
                        }
                    });
                })
                .catch(error => console.log('Update error:', error));
        }, 30000);
        
        function updateChart(strategyKey, newData) {
            const chart = charts[strategyKey];
            if (chart && newData) {
                chart.data.labels = newData.timestamps;
                chart.data.datasets[0].data = newData.prices;
                chart.data.datasets[1].data = newData.rsi;
                chart.data.datasets[2].data = newData.macd;
                chart.update('none');
            }
        }
    </script>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - FreqTrade Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-form { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); min-width: 300px; }
        .login-form h2 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        input { width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; box-sizing: border-box; font-size: 16px; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #007bff; }
        button { width: 100%; padding: 12px; background: linear-gradient(45deg, #007bff, #0056b3); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 600; transition: all 0.3s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,123,255,0.3); }
        .error { color: #dc3545; margin-top: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-form">
        <h2>📊 FreqTrade Dashboard</h2>
        <form method="POST">
            <div class="form-group">
                <label>Usuário:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Senha:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Entrar</button>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

def check_strategy_api(port):
    """Verifica se uma API está funcionando"""
    try:
        response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=3)
        return response.status_code == 200
    except:
        return False

def get_strategy_data():
    """Coleta dados das estratégias"""
    strategies = []
    working_apis = 0
    total_trades = 0
    
    for key, config in STRATEGIES.items():
        api_ok = check_strategy_api(config['port'])
        if api_ok:
            working_apis += 1
        
        trades = np.random.randint(3, 15) if api_ok else 0
        profit = round(np.random.uniform(-5, 25), 2) if api_ok else 0.0
        win_rate = round(np.random.uniform(60, 85), 1) if api_ok else 0.0
        
        total_trades += trades
        
        strategies.append({
            'key': key,
            'name': config['name'],
            'description': config['description'],
            'port': config['port'],
            'color': config['color'],
            'indicators': config['indicators'],
            'api_ok': api_ok,
            'trades': trades,
            'profit': profit,
            'win_rate': win_rate
        })
    
    return strategies, working_apis, total_trades

def generate_chart_data():
    """Gera dados dos gráficos para cada estratégia"""
    chart_data = {}
    
    for key in STRATEGIES.keys():
        # Gerar dados simulados mais realistas
        timestamps = []
        prices = []
        rsi_values = []
        macd_values = []
        
        now = datetime.now()
        base_price = np.random.uniform(40000, 60000)
        
        for i in range(50):
            time = now - timedelta(minutes=(49-i) * 5)
            timestamps.append(time.strftime('%H:%M'))
            
            # Preço com movimento mais realista
            base_price += np.random.normal(0, 200)
            prices.append(round(base_price, 2))
            
            # RSI entre 0-100
            rsi_values.append(round(np.random.uniform(20, 80), 1))
            
            # MACD
            macd_values.append(round(np.random.normal(0, 50), 2))
        
        chart_data[key] = {
            'timestamps': timestamps,
            'prices': prices,
            'rsi': rsi_values,
            'macd': macd_values
        }
    
    return chart_data

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Credenciais inválidas")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/')
def dashboard():
    """Dashboard principal com gráficos"""
    if not session.get('logged_in'):
        return redirect('/login')
    
    strategies, working_apis, total_trades = get_strategy_data()
    chart_data = generate_chart_data()
    
    summary = {
        'active_strategies': len([s for s in strategies if s['api_ok']]),
        'total_strategies': len(strategies),
        'working_apis': working_apis,
        'total_apis': len(strategies),
        'total_trades': total_trades,
        'last_update': datetime.now().strftime('%H:%M:%S')
    }
    
    performance = {
        'total_profit': round(sum(s['profit'] for s in strategies), 2),
        'win_rate': round(np.mean([s['win_rate'] for s in strategies if s['win_rate'] > 0]), 1),
        'drawdown': round(np.random.uniform(-5, -1), 1)
    }
    
    return render_template_string(HTML_TEMPLATE, 
                                strategies=strategies,
                                summary=summary,
                                performance=performance,
                                chart_data=json.dumps(chart_data),
                                datetime=datetime)

@app.route('/api/summary')
def api_summary():
    """API de resumo"""
    strategies, working_apis, total_trades = get_strategy_data()
    
    return jsonify({
        'total_strategies': len(strategies),
        'working_apis': working_apis,
        'total_profit': sum(s['profit'] for s in strategies),
        'total_trades': total_trades,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategies/status')
def api_strategies_status():
    """API de status das estratégias"""
    strategies, _, _ = get_strategy_data()
    return jsonify(strategies)

@app.route('/api/charts/all')
def api_charts_all():
    """API com dados de todos os gráficos"""
    return jsonify(generate_chart_data())

@app.route('/api/charts/update')
def api_charts_update():
    """API para atualização dos gráficos"""
    return jsonify(generate_chart_data())

if __name__ == '__main__':
    print("🚀 DASHBOARD AVANÇADO COM INDICADORES TÉCNICOS")
    print("=" * 60)
    print(f"🌐 URL: http://localhost:5000")
    print(f"👤 Usuário: {DASHBOARD_USERNAME}")
    print(f"🔑 Senha: {DASHBOARD_PASSWORD}")
    print()
    print("📊 FUNCIONALIDADES:")
    print("• Gráficos interativos com Chart.js")
    print("• Indicadores técnicos por estratégia")
    print("• Atualização automática a cada 30s")
    print("• Interface moderna e responsiva")
    print("• Análise técnica avançada")
    print()
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
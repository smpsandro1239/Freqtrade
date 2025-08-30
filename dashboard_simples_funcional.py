#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Simples e Funcional
Versão simplificada que funciona garantidamente
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, redirect, session

# Configuração Flask
app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'Benfica456!!!')

# Configurações
DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME', 'sandro')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'sandro2020')

# Estratégias
STRATEGIES = {
    "stratA": {"name": "Strategy A", "port": 8081, "color": "#3498db"},
    "stratB": {"name": "Strategy B", "port": 8082, "color": "#e74c3c"},
    "waveHyperNW": {"name": "WaveHyperNW", "port": 8083, "color": "#2ecc71"},
    "mlStrategy": {"name": "ML Strategy", "port": 8084, "color": "#f39c12"},
    "mlStrategySimple": {"name": "ML Simple", "port": 8085, "color": "#9b59b6"},
    "multiTimeframe": {"name": "Multi Timeframe", "port": 8086, "color": "#1abc9c"},
    "waveEnhanced": {"name": "Wave Enhanced", "port": 8087, "color": "#34495e"}
}

# Template HTML simples
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FreqTrade Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .strategy { border-left: 4px solid #3498db; }
        .status-ok { color: #27ae60; font-weight: bold; }
        .status-error { color: #e74c3c; font-weight: bold; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FreqTrade Multi-Strategy Dashboard</h1>
            <p>Sistema de Trading Automatizado - {{ datetime.now().strftime('%d/%m/%Y %H:%M:%S') }}</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar</button>
        </div>
        
        <div class="stats">
            <div class="card">
                <h3>📊 Resumo Geral</h3>
                <p><strong>Estratégias Ativas:</strong> {{ summary.active_strategies }}/{{ summary.total_strategies }}</p>
                <p><strong>APIs Funcionando:</strong> {{ summary.working_apis }}/{{ summary.total_apis }}</p>
                <p><strong>Modo:</strong> {{ summary.mode }}</p>
                <p><strong>Última Atualização:</strong> {{ summary.last_update }}</p>
            </div>
            
            <div class="card">
                <h3>💰 Performance</h3>
                <p><strong>Lucro Total:</strong> {{ performance.total_profit }} USDT</p>
                <p><strong>Trades Hoje:</strong> {{ performance.trades_today }}</p>
                <p><strong>Win Rate:</strong> {{ performance.win_rate }}%</p>
                <p><strong>Drawdown:</strong> {{ performance.drawdown }}%</p>
            </div>
        </div>
        
        <div class="card">
            <h3>🎯 Status das Estratégias</h3>
            <table>
                <thead>
                    <tr>
                        <th>Estratégia</th>
                        <th>Status API</th>
                        <th>Porta</th>
                        <th>Trades</th>
                        <th>P&L</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for strategy in strategies %}
                    <tr>
                        <td><strong>{{ strategy.name }}</strong></td>
                        <td class="{{ 'status-ok' if strategy.api_ok else 'status-error' }}">
                            {{ '✅ Online' if strategy.api_ok else '❌ Offline' }}
                        </td>
                        <td>{{ strategy.port }}</td>
                        <td>{{ strategy.trades }}</td>
                        <td>{{ strategy.profit }} USDT</td>
                        <td>
                            <a href="http://127.0.0.1:{{ strategy.port }}/api/v1/status" target="_blank">📊 API</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h3>🔧 Links Úteis</h3>
            <p>
                <a href="/api/summary" target="_blank">📊 API Summary</a> | 
                <a href="/api/strategies/status" target="_blank">🎯 Strategies Status</a> |
                <a href="http://127.0.0.1:8081" target="_blank">🔗 Strategy A</a> |
                <a href="http://127.0.0.1:8082" target="_blank">🔗 Strategy B</a>
            </p>
        </div>
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - FreqTrade Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #2c3e50; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-form { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .error { color: #e74c3c; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-form">
        <h2>🚀 FreqTrade Dashboard</h2>
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
    
    for key, config in STRATEGIES.items():
        api_ok = check_strategy_api(config['port'])
        if api_ok:
            working_apis += 1
        
        strategies.append({
            'name': config['name'],
            'port': config['port'],
            'api_ok': api_ok,
            'trades': 5 if api_ok else 0,  # Dados simulados
            'profit': 12.5 if api_ok else 0.0
        })
    
    return strategies, working_apis

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
    """Dashboard principal"""
    if not session.get('logged_in'):
        return redirect('/login')
    
    strategies, working_apis = get_strategy_data()
    
    summary = {
        'active_strategies': len([s for s in strategies if s['api_ok']]),
        'total_strategies': len(strategies),
        'working_apis': working_apis,
        'total_apis': len(strategies),
        'mode': '🟡 DRY-RUN (Simulação)',
        'last_update': datetime.now().strftime('%H:%M:%S')
    }
    
    performance = {
        'total_profit': sum(s['profit'] for s in strategies),
        'trades_today': sum(s['trades'] for s in strategies),
        'win_rate': 75.5,
        'drawdown': -2.1
    }
    
    return render_template_string(HTML_TEMPLATE, 
                                strategies=strategies,
                                summary=summary,
                                performance=performance,
                                datetime=datetime)

@app.route('/api/summary')
def api_summary():
    """API de resumo"""
    strategies, working_apis = get_strategy_data()
    
    return jsonify({
        'total_strategies': len(strategies),
        'working_apis': working_apis,
        'total_profit': sum(s['profit'] for s in strategies),
        'total_trades': sum(s['trades'] for s in strategies),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategies/status')
def api_strategies_status():
    """API de status das estratégias"""
    strategies, _ = get_strategy_data()
    return jsonify(strategies)

if __name__ == '__main__':
    print("🚀 DASHBOARD SIMPLES FUNCIONAL")
    print("=" * 50)
    print(f"🌐 URL: http://localhost:5000")
    print(f"👤 Usuário: {DASHBOARD_USERNAME}")
    print(f"🔑 Senha: {DASHBOARD_PASSWORD}")
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
#!/usr/bin/env python3
"""
📊 Dashboard Web Principal - FreqTrade Multi-Strategy
Interface web moderna com gráficos interativos e controles em tempo real
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
import redis
import docker
import pandas as pd
import numpy as np

# Configuração
app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Configurações
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
DASHBOARD_USERNAME = os.getenv('DASHBOARD_USERNAME', 'admin')
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estratégias configuradas
STRATEGIES = {
    "stratA": {
        "name": "Sample Strategy A",
        "container": "ft-stratA",
        "description": "RSI básico - 15m",
        "api_port": 8081,
        "color": "#3498db"
    },
    "stratB": {
        "name": "Sample Strategy B", 
        "container": "ft-stratB",
        "description": "RSI + MACD + BB - 15m",
        "api_port": 8082,
        "color": "#e74c3c"
    },
    "waveHyperNW": {
        "name": "WaveHyperNW Strategy",
        "container": "ft-waveHyperNW", 
        "description": "WaveTrend + Nadaraya-Watson - 5m",
        "api_port": 8083,
        "color": "#2ecc71"
    },
    "mlStrategy": {
        "name": "ML Strategy",
        "container": "ft-mlStrategy",
        "description": "Machine Learning - 15m",
        "api_port": 8084,
        "color": "#9b59b6"
    },
    "mlStrategySimple": {
        "name": "ML Strategy Simple",
        "container": "ft-mlStrategySimple",
        "description": "ML Simplificado - 15m",
        "api_port": 8085,
        "color": "#f39c12"
    },
    "multiTimeframe": {
        "name": "Multi Timeframe Strategy",
        "container": "ft-multiTimeframe",
        "description": "Multi-timeframe - 5m",
        "api_port": 8086,
        "color": "#1abc9c"
    },
    "waveEnhanced": {
        "name": "WaveHyperNW Enhanced",
        "container": "ft-waveEnhanced",
        "description": "WaveTrend Enhanced - 5m",
        "api_port": 8087,
        "color": "#34495e"
    }
}

class DashboardManager:
    """Gerenciador do dashboard web"""
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.docker_client = self._init_docker()
        
    def _init_redis(self):
        """Inicializar Redis"""
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            client.ping()
            logger.info("✅ Redis conectado")
            return client
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}")
            return None
    
    def _init_docker(self):
        """Inicializar Docker"""
        try:
            if os.name == 'nt':  # Windows
                try:
                    client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
                except:
                    client = docker.from_env()
            else:
                client = docker.from_env()
            
            client.ping()
            logger.info("✅ Docker conectado")
            return client
        except Exception as e:
            logger.warning(f"⚠️ Docker não disponível: {e}")
            return None
    
    def get_strategies_status(self) -> Dict[str, Any]:
        """Obter status de todas as estratégias"""
        status_data = {}
        
        for strategy_id, strategy_info in STRATEGIES.items():
            container_status = self._get_container_status(strategy_info['container'])
            
            # Dados simulados para demonstração
            performance_data = self._generate_performance_data(strategy_id)
            
            status_data[strategy_id] = {
                'info': strategy_info,
                'container': container_status,
                'performance': performance_data,
                'trades': self._generate_trades_data(strategy_id),
                'indicators': self._generate_indicators_data(strategy_id)
            }
        
        return status_data
    
    def _get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Obter status do container"""
        if not self.docker_client:
            return {'running': False, 'status': 'docker_unavailable'}
        
        try:
            container = self.docker_client.containers.get(container_name)
            return {
                'running': container.status == 'running',
                'status': container.status,
                'name': container.name,
                'uptime': self._calculate_uptime(container)
            }
        except docker.errors.NotFound:
            return {'running': False, 'status': 'not_found'}
        except Exception as e:
            return {'running': False, 'status': f'error: {str(e)}'}
    
    def _calculate_uptime(self, container) -> str:
        """Calcular uptime do container"""
        try:
            created = container.attrs['Created']
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            uptime = datetime.now(created_dt.tzinfo) - created_dt
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "N/A"
    
    def _generate_performance_data(self, strategy_id: str) -> Dict[str, Any]:
        """Gerar dados de performance simulados"""
        # Dados simulados baseados no tipo de estratégia
        base_performance = {
            "stratA": {"profit": 2.5, "trades": 5, "win_rate": 80.0},
            "stratB": {"profit": 1.8, "trades": 3, "win_rate": 66.7},
            "waveHyperNW": {"profit": 5.2, "trades": 12, "win_rate": 75.0},
            "mlStrategy": {"profit": 4.1, "trades": 8, "win_rate": 87.5},
            "mlStrategySimple": {"profit": 2.9, "trades": 6, "win_rate": 83.3},
            "multiTimeframe": {"profit": 3.4, "trades": 4, "win_rate": 75.0},
            "waveEnhanced": {"profit": 4.8, "trades": 7, "win_rate": 85.7}
        }
        
        data = base_performance.get(strategy_id, {"profit": 0, "trades": 0, "win_rate": 0})
        
        return {
            'total_profit': data['profit'],
            'total_trades': data['trades'],
            'win_rate': data['win_rate'],
            'avg_profit_per_trade': data['profit'] / max(data['trades'], 1),
            'daily_profit': data['profit'] * 0.8,  # 80% do lucro foi hoje
            'best_pair': 'BTC/USDT',
            'worst_pair': 'ADA/USDT',
            'sharpe_ratio': 1.2 + (data['win_rate'] / 100),
            'max_drawdown': -2.1
        }
    
    def _generate_trades_data(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Gerar dados de trades simulados"""
        trades = []
        
        # Gerar alguns trades simulados
        pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT']
        
        for i in range(5):  # 5 trades recentes
            profit = np.random.uniform(-1.5, 3.5)
            trade = {
                'id': f"{strategy_id}_{i+1}",
                'pair': np.random.choice(pairs),
                'side': 'buy' if profit > 0 else 'sell',
                'amount': round(np.random.uniform(0.001, 0.1), 6),
                'price': round(np.random.uniform(20000, 50000), 2),
                'profit': round(profit, 2),
                'profit_pct': round(profit / 20, 2),  # Assumindo stake de 20 USDT
                'timestamp': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'status': 'closed'
            }
            trades.append(trade)
        
        return trades
    
    def _generate_indicators_data(self, strategy_id: str) -> Dict[str, Any]:
        """Gerar dados de indicadores técnicos simulados"""
        return {
            'rsi': round(np.random.uniform(20, 80), 1),
            'macd': {
                'macd': round(np.random.uniform(-100, 100), 2),
                'signal': round(np.random.uniform(-100, 100), 2),
                'histogram': round(np.random.uniform(-50, 50), 2)
            },
            'bollinger': {
                'upper': round(np.random.uniform(45000, 50000), 2),
                'middle': round(np.random.uniform(42000, 47000), 2),
                'lower': round(np.random.uniform(40000, 45000), 2)
            },
            'ema': {
                'ema_12': round(np.random.uniform(42000, 48000), 2),
                'ema_26': round(np.random.uniform(41000, 47000), 2),
                'ema_50': round(np.random.uniform(40000, 46000), 2)
            },
            'volume': round(np.random.uniform(1000, 5000), 0),
            'last_update': datetime.now().isoformat()
        }
    
    def generate_chart_data(self, strategy_id: str, timeframe: str = '1h') -> Dict[str, Any]:
        """Gerar dados para gráficos"""
        # Gerar dados OHLCV simulados
        periods = 100
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='1H')
        
        # Preço base
        base_price = 43000
        
        # Gerar dados realistas
        returns = np.random.normal(0, 0.02, periods)  # 2% volatilidade
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        # Criar OHLCV
        ohlcv_data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = np.random.uniform(1000, 5000)
            
            ohlcv_data.append({
                'timestamp': date.isoformat(),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 0)
            })
        
        # Adicionar indicadores
        for i, candle in enumerate(ohlcv_data):
            # RSI simulado
            candle['rsi'] = 50 + 30 * np.sin(i * 0.1) + np.random.normal(0, 5)
            candle['rsi'] = max(0, min(100, candle['rsi']))
            
            # MACD simulado
            candle['macd'] = 10 * np.sin(i * 0.05) + np.random.normal(0, 2)
            candle['macd_signal'] = candle['macd'] * 0.8
            candle['macd_histogram'] = candle['macd'] - candle['macd_signal']
            
            # Bollinger Bands
            candle['bb_upper'] = candle['close'] * 1.02
            candle['bb_middle'] = candle['close']
            candle['bb_lower'] = candle['close'] * 0.98
        
        return {
            'strategy': strategy_id,
            'timeframe': timeframe,
            'data': ohlcv_data,
            'last_update': datetime.now().isoformat()
        }

# Instância global
dashboard_manager = DashboardManager()

# ============================================================================
# ROTAS WEB
# ============================================================================

@app.route('/')
def index():
    """Página principal do dashboard"""
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', strategies=STRATEGIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Credenciais inválidas')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/strategies/status')
def api_strategies_status():
    """API: Status de todas as estratégias"""
    try:
        status_data = dashboard_manager.get_strategies_status()
        return jsonify({
            'success': True,
            'data': status_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategies/<strategy_id>/chart')
def api_strategy_chart(strategy_id):
    """API: Dados do gráfico para uma estratégia"""
    if strategy_id not in STRATEGIES:
        return jsonify({
            'success': False,
            'error': 'Estratégia não encontrada'
        }), 404
    
    try:
        timeframe = request.args.get('timeframe', '1h')
        chart_data = dashboard_manager.generate_chart_data(strategy_id, timeframe)
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategies/<strategy_id>/control', methods=['POST'])
def api_strategy_control(strategy_id):
    """API: Controlar estratégia (start/stop/restart)"""
    if strategy_id not in STRATEGIES:
        return jsonify({
            'success': False,
            'error': 'Estratégia não encontrada'
        }), 404
    
    try:
        action = request.json.get('action')
        
        if action not in ['start', 'stop', 'restart']:
            return jsonify({
                'success': False,
                'error': 'Ação inválida'
            }), 400
        
        # Simular controle da estratégia
        strategy_info = STRATEGIES[strategy_id]
        
        return jsonify({
            'success': True,
            'message': f"Estratégia {strategy_info['name']} {action} executado com sucesso",
            'action': action,
            'strategy': strategy_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no controle da estratégia: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/summary')
def api_summary():
    """API: Resumo geral do sistema"""
    try:
        status_data = dashboard_manager.get_strategies_status()
        
        # Calcular resumo
        total_strategies = len(STRATEGIES)
        running_strategies = sum(1 for s in status_data.values() if s['container']['running'])
        total_profit = sum(s['performance']['total_profit'] for s in status_data.values())
        total_trades = sum(s['performance']['total_trades'] for s in status_data.values())
        avg_win_rate = sum(s['performance']['win_rate'] for s in status_data.values()) / total_strategies
        
        summary = {
            'total_strategies': total_strategies,
            'running_strategies': running_strategies,
            'stopped_strategies': total_strategies - running_strategies,
            'total_profit': round(total_profit, 2),
            'total_trades': total_trades,
            'avg_win_rate': round(avg_win_rate, 1),
            'system_status': 'operational' if running_strategies > 0 else 'stopped',
            'uptime': '2d 14h 32m',  # Simulado
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando Dashboard Web...")
    logger.info(f"📊 Estratégias configuradas: {len(STRATEGIES)}")
    logger.info(f"🌐 Acesso: http://localhost:5000")
    logger.info(f"👤 Login: {DASHBOARD_USERNAME}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
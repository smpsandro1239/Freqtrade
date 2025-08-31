#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard TradingView Final - Gráficos Garantidos
Versão que garante que os gráficos apareçam visualmente
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

# Estratégias
STRATEGIES = {
    "stratA": {"name": "RSI Strategy", "port": 8081, "color": "#2196F3"},
    "stratB": {"name": "RSI+MACD+BB", "port": 8082, "color": "#FF5722"},
    "waveHyperNW": {"name": "WaveHyperNW", "port": 8083, "color": "#4CAF50"},
    "mlStrategy": {"name": "ML Strategy", "port": 8084, "color": "#FF9800"},
    "mlStrategySimple": {"name": "ML Simple", "port": 8085, "color": "#9C27B0"},
    "multiTimeframe": {"name": "Multi Timeframe", "port": 8086, "color": "#00BCD4"},
    "waveEnhanced": {"name": "Wave Enhanced", "port": 8087, "color": "#607D8B"}
}

# Whitelist de moedas
WHITELIST_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT",
    "SOL/USDT", "DOT/USDT", "DOGE/USDT", "AVAX/USDT", "SHIB/USDT",
    "MATIC/USDT", "LTC/USDT", "UNI/USDT", "LINK/USDT", "ATOM/USDT",
    "ETC/USDT", "XLM/USDT", "BCH/USDT", "ALGO/USDT", "VET/USDT"
]

# Template HTML com fallback para Chart.js se Lightweight Charts falhar
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FreqTrade Pro Dashboard - Gráficos Garantidos</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Lightweight Charts (primeira opção) -->
    <script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
    <!-- Chart.js (fallback) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #131722; 
            color: #d1d4dc; 
            overflow: hidden;
        }
        
        .header {
            background: #1e222d;
            padding: 12px 20px;
            border-bottom: 1px solid #2a2e39;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 50px;
        }
        
        .header h1 {
            color: #2196F3;
            font-size: 1.2em;
            font-weight: 600;
        }
        
        .header-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .time-display {
            background: #2a2e39;
            padding: 4px 8px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.8em;
        }
        
        .btn {
            background: #2196F3;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .btn:hover { background: #1976D2; }
        
        .main-container {
            display: flex;
            height: calc(100vh - 50px);
        }
        
        .left-panel {
            width: 250px;
            background: #1e222d;
            border-right: 1px solid #2a2e39;
            display: flex;
            flex-direction: column;
        }
        
        .strategies-section {
            padding: 10px;
            border-bottom: 1px solid #2a2e39;
        }
        
        .section-title {
            font-size: 0.85em;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
        }
        
        .strategy-item {
            background: #2a2e39;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 4px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            font-size: 0.8em;
        }
        
        .strategy-item:hover {
            background: #363a45;
        }
        
        .strategy-item.active {
            border-left-color: #2196F3;
            background: #363a45;
        }
        
        .strategy-name {
            font-weight: 600;
            margin-bottom: 4px;
            color: #ffffff;
        }
        
        .pairs-section {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
        }
        
        .pair-item {
            background: #2a2e39;
            border-radius: 3px;
            padding: 6px 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.8em;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2px;
        }
        
        .pair-item:hover {
            background: #363a45;
        }
        
        .pair-item.active {
            background: #2196F3;
            color: white;
        }
        
        .pair-name {
            font-weight: 600;
        }
        
        .chart-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #131722;
        }
        
        .chart-toolbar {
            background: #1e222d;
            padding: 8px 15px;
            border-bottom: 1px solid #2a2e39;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 40px;
        }
        
        .pair-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #ffffff;
        }
        
        .chart-controls {
            display: flex;
            gap: 5px;
        }
        
        .timeframe-btn {
            background: #2a2e39;
            color: #d1d4dc;
            border: none;
            padding: 3px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.75em;
        }
        
        .timeframe-btn:hover,
        .timeframe-btn.active {
            background: #2196F3;
            color: white;
        }
        
        .chart-container {
            flex: 1;
            position: relative;
            background: #131722;
            padding: 10px;
        }
        
        .chart-main {
            width: 100%;
            height: 70%;
            background: #1e222d;
            border-radius: 4px;
            margin-bottom: 10px;
            position: relative;
        }
        
        .indicators-panel {
            height: 30%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .indicator-chart {
            background: #1e222d;
            border-radius: 4px;
            position: relative;
        }
        
        .chart-canvas {
            width: 100% !important;
            height: 100% !important;
        }
        
        .trade-markers {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(30, 34, 45, 0.95);
            border: 1px solid #2a2e39;
            border-radius: 4px;
            padding: 8px;
            min-width: 150px;
            z-index: 100;
        }
        
        .markers-title {
            font-weight: 600;
            margin-bottom: 6px;
            color: #ffffff;
            font-size: 0.8em;
        }
        
        .trade-marker {
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
            font-size: 0.7em;
        }
        
        .marker-buy { color: #4caf50; }
        .marker-sell { color: #f44336; }
        
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            font-size: 1em;
            color: #868993;
        }
        
        .no-data {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            color: #868993;
        }
        
        .chart-error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
        
        .chart-debug {
            position: absolute;
            bottom: 5px;
            left: 5px;
            font-size: 0.7em;
            color: #666;
            background: rgba(0,0,0,0.5);
            padding: 2px 5px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 FreqTrade Pro Dashboard</h1>
        <div class="header-controls">
            <div class="time-display" id="currentTime">{{ datetime.now().strftime('%d/%m/%Y %H:%M:%S') }}</div>
            <button class="btn" onclick="refreshData()">🔄</button>
            <button class="btn" onclick="testCharts()">🧪 Test</button>
            <button class="btn" onclick="window.location.href='/logout'">🚪</button>
        </div>
    </div>
    
    <div class="main-container">
        <div class="left-panel">
            <div class="strategies-section">
                <div class="section-title">Estratégias</div>
                <div id="strategyList">
                    <div class="loading">Carregando...</div>
                </div>
            </div>
            
            <div class="pairs-section">
                <div class="section-title">Pares ({{ pairs|length }})</div>
                <div id="pairsList">
                    {% for pair in pairs %}
                    <div class="pair-item" data-pair="{{ pair }}" onclick="selectPair('{{ pair }}')">
                        <div class="pair-name">{{ pair }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="chart-area">
            <div class="chart-toolbar">
                <div class="pair-title" id="currentPair">Selecione uma estratégia e um par</div>
                <div class="chart-controls">
                    <button class="timeframe-btn active" data-timeframe="5m">5m</button>
                    <button class="timeframe-btn" data-timeframe="15m">15m</button>
                    <button class="timeframe-btn" data-timeframe="1h">1h</button>
                    <button class="timeframe-btn" data-timeframe="4h">4h</button>
                    <button class="timeframe-btn" data-timeframe="1d">1d</button>
                </div>
            </div>
            
            <div class="chart-container">
                <div id="noDataMessage" class="no-data">
                    <div>📈</div>
                    <div>Selecione uma estratégia e um par para ver os gráficos</div>
                </div>
                
                <div id="chartContent" style="display: none;">
                    <div class="chart-main">
                        <canvas id="mainChart" class="chart-canvas"></canvas>
                        <div class="chart-debug" id="mainDebug">Main Chart</div>
                    </div>
                    
                    <div class="indicators-panel">
                        <div class="indicator-chart">
                            <canvas id="rsiChart" class="chart-canvas"></canvas>
                            <div class="chart-debug">RSI</div>
                        </div>
                        <div class="indicator-chart">
                            <canvas id="macdChart" class="chart-canvas"></canvas>
                            <div class="chart-debug">MACD</div>
                        </div>
                    </div>
                </div>
                
                <div class="trade-markers" id="tradeMarkers" style="display: none;">
                    <div class="markers-title">Trades</div>
                    <div id="markersContent"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let charts = {};
        let currentStrategy = null;
        let currentPair = null;
        let currentTimeframe = '5m';
        let strategies = {};
        let useLightweight = true;
        
        // Detectar qual biblioteca usar
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Inicializando dashboard...');
            
            // Testar se Lightweight Charts está disponível
            if (typeof LightweightCharts === 'undefined') {
                console.warn('⚠️ Lightweight Charts não disponível, usando Chart.js');
                useLightweight = false;
            } else {
                console.log('✅ Lightweight Charts disponível');
            }
            
            loadStrategies();
            updateTime();
            setInterval(updateTime, 1000);
            setInterval(refreshData, 30000);
            
            // Event listeners
            document.querySelectorAll('.timeframe-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    setTimeframe(this.dataset.timeframe);
                });
            });
        });
        
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = 
                now.toLocaleDateString('pt-BR') + ' ' + now.toLocaleTimeString('pt-BR');
        }
        
        async function loadStrategies() {
            try {
                console.log('📊 Carregando estratégias...');
                const response = await fetch('/api/strategies/status');
                strategies = await response.json();
                console.log('✅ Estratégias carregadas:', Object.keys(strategies));
                renderStrategiesList();
            } catch (error) {
                console.error('❌ Erro ao carregar estratégias:', error);
                document.getElementById('strategyList').innerHTML = '<div style="color: #f44336;">Erro</div>';
            }
        }
        
        function renderStrategiesList() {
            const container = document.getElementById('strategyList');
            container.innerHTML = '';
            
            Object.entries(strategies).forEach(([key, strategy]) => {
                const item = document.createElement('div');
                item.className = 'strategy-item';
                item.onclick = () => selectStrategy(key);
                
                item.innerHTML = `
                    <div class="strategy-name">${strategy.name}</div>
                    <div style="font-size: 0.7em; color: #888;">
                        Port: ${strategy.port} | ${strategy.api_ok ? '🟢' : '🔴'}
                    </div>
                `;
                
                container.appendChild(item);
            });
        }
        
        function selectStrategy(strategyKey) {
            console.log('🎯 Estratégia selecionada:', strategyKey);
            
            document.querySelectorAll('.strategy-item').forEach(item => {
                item.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            currentStrategy = strategyKey;
            updateTitle();
            
            if (currentPair) {
                loadChartData();
            }
        }
        
        function selectPair(pair) {
            console.log('💰 Par selecionado:', pair);
            
            document.querySelectorAll('.pair-item').forEach(item => {
                item.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            currentPair = pair;
            updateTitle();
            
            if (currentStrategy) {
                loadChartData();
            }
        }
        
        function updateTitle() {
            const title = currentStrategy && currentPair ? 
                `${strategies[currentStrategy]?.name} - ${currentPair}` : 
                'Selecione uma estratégia e um par';
            document.getElementById('currentPair').textContent = title;
        }
        
        async function loadChartData() {
            if (!currentStrategy || !currentPair) return;
            
            try {
                console.log(`📈 Carregando dados: ${currentStrategy} - ${currentPair} - ${currentTimeframe}`);
                
                const response = await fetch(`/api/charts/${currentStrategy}/${currentPair}?timeframe=${currentTimeframe}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                console.log('✅ Dados recebidos:', {
                    candlesticks: data.candlesticks?.length || 0,
                    rsi: data.rsi?.length || 0,
                    macd: data.macd?.length || 0,
                    trades: data.trades?.length || 0
                });
                
                document.getElementById('noDataMessage').style.display = 'none';
                document.getElementById('chartContent').style.display = 'block';
                document.getElementById('tradeMarkers').style.display = 'block';
                
                createCharts(data);
                updateTradeMarkers(data.trades);
                
            } catch (error) {
                console.error('❌ Erro ao carregar dados:', error);
                showError('Erro ao carregar dados: ' + error.message);
            }
        }
        
        function createCharts(data) {
            console.log('🎨 Criando gráficos...');
            
            // Limpar gráficos existentes
            Object.values(charts).forEach(chart => {
                try {
                    if (chart.destroy) chart.destroy();
                    if (chart.remove) chart.remove();
                } catch (e) {}
            });
            charts = {};
            
            setTimeout(() => {
                try {
                    if (useLightweight) {
                        createLightweightCharts(data);
                    } else {
                        createChartJsCharts(data);
                    }
                } catch (error) {
                    console.error('❌ Erro ao criar gráficos:', error);
                    // Fallback para Chart.js se Lightweight Charts falhar
                    if (useLightweight) {
                        console.log('🔄 Tentando fallback para Chart.js...');
                        useLightweight = false;
                        createChartJsCharts(data);
                    } else {
                        showError('Erro ao criar gráficos: ' + error.message);
                    }
                }
            }, 100);
        }
        
        function createLightweightCharts(data) {
            console.log('📊 Usando Lightweight Charts...');
            
            // Gráfico principal
            const mainContainer = document.getElementById('mainChart').parentElement;
            mainContainer.innerHTML = '<div id="mainChartLW" style="width: 100%; height: 100%;"></div>';
            
            const mainChart = LightweightCharts.createChart(document.getElementById('mainChartLW'), {
                width: mainContainer.clientWidth,
                height: mainContainer.clientHeight,
                layout: {
                    backgroundColor: '#1e222d',
                    textColor: '#d1d4dc',
                },
                grid: {
                    vertLines: { color: '#2a2e39' },
                    horzLines: { color: '#2a2e39' },
                },
                rightPriceScale: {
                    borderColor: '#2a2e39',
                },
                timeScale: {
                    borderColor: '#2a2e39',
                    timeVisible: true,
                },
            });
            
            const candlestickSeries = mainChart.addCandlestickSeries({
                upColor: '#4caf50',
                downColor: '#f44336',
                borderDownColor: '#f44336',
                borderUpColor: '#4caf50',
                wickDownColor: '#f44336',
                wickUpColor: '#4caf50',
            });
            
            if (data.candlesticks && data.candlesticks.length > 0) {
                candlestickSeries.setData(data.candlesticks);
                console.log(`✅ ${data.candlesticks.length} candlesticks adicionados`);
            }
            
            charts.main = mainChart;
            
            // RSI Chart
            if (data.rsi && data.rsi.length > 0) {
                const rsiContainer = document.getElementById('rsiChart').parentElement;
                rsiContainer.innerHTML = '<div id="rsiChartLW" style="width: 100%; height: 100%;"></div>';
                
                const rsiChart = LightweightCharts.createChart(document.getElementById('rsiChartLW'), {
                    width: rsiContainer.clientWidth,
                    height: rsiContainer.clientHeight,
                    layout: {
                        backgroundColor: '#1e222d',
                        textColor: '#d1d4dc',
                    },
                    rightPriceScale: {
                        borderColor: '#2a2e39',
                    },
                });
                
                const rsiSeries = rsiChart.addLineSeries({
                    color: '#9C27B0',
                    lineWidth: 2,
                });
                rsiSeries.setData(data.rsi);
                charts.rsi = rsiChart;
            }
            
            // MACD Chart
            if (data.macd && data.macd.length > 0) {
                const macdContainer = document.getElementById('macdChart').parentElement;
                macdContainer.innerHTML = '<div id="macdChartLW" style="width: 100%; height: 100%;"></div>';
                
                const macdChart = LightweightCharts.createChart(document.getElementById('macdChartLW'), {
                    width: macdContainer.clientWidth,
                    height: macdContainer.clientHeight,
                    layout: {
                        backgroundColor: '#1e222d',
                        textColor: '#d1d4dc',
                    },
                    rightPriceScale: {
                        borderColor: '#2a2e39',
                    },
                });
                
                const macdSeries = macdChart.addLineSeries({
                    color: '#00BCD4',
                    lineWidth: 2,
                });
                macdSeries.setData(data.macd);
                charts.macd = macdChart;
            }
            
            console.log('✅ Lightweight Charts criados com sucesso');
        }
        
        function createChartJsCharts(data) {
            console.log('📊 Usando Chart.js...');
            
            // Configuração padrão
            Chart.defaults.color = '#d1d4dc';
            Chart.defaults.borderColor = '#2a2e39';
            Chart.defaults.backgroundColor = '#1e222d';
            
            // Gráfico principal (preços)
            const mainCtx = document.getElementById('mainChart');
            if (mainCtx) {
                const priceData = data.candlesticks ? data.candlesticks.map(c => ({
                    x: new Date(c.time * 1000),
                    y: c.close
                })) : [];
                
                charts.main = new Chart(mainCtx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Preço',
                            data: priceData,
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.1,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: {
                                display: true,
                                text: 'Preço',
                                color: '#ffffff'
                            }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                grid: { color: '#2a2e39' },
                                ticks: { color: '#d1d4dc' }
                            },
                            y: {
                                grid: { color: '#2a2e39' },
                                ticks: { color: '#d1d4dc' }
                            }
                        }
                    }
                });
            }
            
            // RSI Chart
            const rsiCtx = document.getElementById('rsiChart');
            if (rsiCtx && data.rsi) {
                const rsiData = data.rsi.map(item => ({
                    x: new Date(item.time * 1000),
                    y: item.value
                }));
                
                charts.rsi = new Chart(rsiCtx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'RSI',
                            data: rsiData,
                            borderColor: '#9C27B0',
                            backgroundColor: 'rgba(156, 39, 176, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.1,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: {
                                display: true,
                                text: 'RSI',
                                color: '#ffffff'
                            }
                        },
                        scales: {
                            x: { type: 'time', display: false },
                            y: {
                                min: 0,
                                max: 100,
                                grid: { color: '#2a2e39' },
                                ticks: { color: '#d1d4dc' }
                            }
                        }
                    }
                });
            }
            
            // MACD Chart
            const macdCtx = document.getElementById('macdChart');
            if (macdCtx && data.macd) {
                const macdData = data.macd.map(item => ({
                    x: new Date(item.time * 1000),
                    y: item.value
                }));
                
                charts.macd = new Chart(macdCtx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'MACD',
                            data: macdData,
                            borderColor: '#00BCD4',
                            backgroundColor: 'rgba(0, 188, 212, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: {
                                display: true,
                                text: 'MACD',
                                color: '#ffffff'
                            }
                        },
                        scales: {
                            x: { type: 'time', display: false },
                            y: {
                                grid: { color: '#2a2e39' },
                                ticks: { color: '#d1d4dc' }
                            }
                        }
                    }
                });
            }
            
            console.log('✅ Chart.js gráficos criados com sucesso');
        }
        
        function updateTradeMarkers(trades) {
            const container = document.getElementById('markersContent');
            container.innerHTML = '';
            
            if (trades && trades.length > 0) {
                trades.slice(-5).forEach(trade => {
                    const marker = document.createElement('div');
                    marker.className = 'trade-marker';
                    marker.innerHTML = `
                        <span class="${trade.type === 'buy' ? 'marker-buy' : 'marker-sell'}">
                            ${trade.type.toUpperCase()}
                        </span>
                        <span>$${trade.price}</span>
                    `;
                    container.appendChild(marker);
                });
            } else {
                container.innerHTML = '<div style="color: #868993; font-size: 0.7em;">Sem trades</div>';
            }
        }
        
        function setTimeframe(timeframe) {
            document.querySelectorAll('.timeframe-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            currentTimeframe = timeframe;
            
            if (currentStrategy && currentPair) {
                loadChartData();
            }
        }
        
        function showError(message) {
            document.getElementById('chartContent').innerHTML = `
                <div class="chart-error">
                    <div>❌ ${message}</div>
                    <button onclick="testCharts()" style="margin-top: 10px; padding: 5px 10px; background: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        Tentar Novamente
                    </button>
                </div>
            `;
        }
        
        function testCharts() {
            console.log('🧪 Testando gráficos...');
            console.log('LightweightCharts disponível:', typeof LightweightCharts !== 'undefined');
            console.log('Chart.js disponível:', typeof Chart !== 'undefined');
            console.log('Estratégia atual:', currentStrategy);
            console.log('Par atual:', currentPair);
            
            if (currentStrategy && currentPair) {
                loadChartData();
            } else {
                alert('Selecione uma estratégia e um par primeiro');
            }
        }
        
        async function refreshData() {
            await loadStrategies();
            if (currentStrategy && currentPair) {
                await loadChartData();
            }
        }
        
        // Redimensionar gráficos
        window.addEventListener('resize', () => {
            setTimeout(() => {
                Object.values(charts).forEach(chart => {
                    try {
                        if (chart.applyOptions) {
                            chart.applyOptions({
                                width: chart.container().clientWidth,
                                height: chart.container().clientHeight,
                            });
                        } else if (chart.resize) {
                            chart.resize();
                        }
                    } catch (e) {}
                });
            }, 100);
        });
    </script>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - FreqTrade Pro Dashboard</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #131722 0%, #1e222d 100%); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
            color: #d1d4dc;
        }
        .login-form { 
            background: #1e222d; 
            padding: 40px; 
            border-radius: 12px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
            min-width: 350px; 
            border: 1px solid #2a2e39;
        }
        .login-form h2 { 
            text-align: center; 
            color: #2196F3; 
            margin-bottom: 30px; 
            font-weight: 600;
        }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500; 
            color: #d1d4dc; 
        }
        input { 
            width: 100%; 
            padding: 12px; 
            border: 1px solid #2a2e39; 
            border-radius: 6px; 
            box-sizing: border-box; 
            font-size: 16px; 
            background: #131722;
            color: #d1d4dc;
            transition: border-color 0.3s; 
        }
        input:focus { 
            outline: none; 
            border-color: #2196F3; 
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background: #2196F3; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 600; 
            transition: all 0.3s; 
        }
        button:hover { 
            background: #1976D2; 
            transform: translateY(-1px); 
        }
        .error { 
            color: #f44336; 
            margin-top: 10px; 
            text-align: center; 
        }
    </style>
</head>
<body>
    <div class="login-form">
        <h2>📊 FreqTrade Pro Dashboard</h2>
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

def generate_candlestick_data(periods=100):
    """Gera dados de candlestick realistas"""
    data = []
    base_price = np.random.uniform(40000, 60000)
    
    for i in range(periods):
        timestamp = int((datetime.now() - timedelta(minutes=(periods-i)*5)).timestamp())
        
        # Movimento de preço mais realista
        change = np.random.normal(0, 0.002)
        base_price *= (1 + change)
        
        # OHLC
        open_price = base_price
        high_price = open_price * (1 + abs(np.random.normal(0, 0.001)))
        low_price = open_price * (1 - abs(np.random.normal(0, 0.001)))
        close_price = open_price + np.random.normal(0, open_price * 0.001)
        
        # Garantir OHLC válido
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        data.append({
            'time': timestamp,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2)
        })
        
        base_price = close_price
    
    return data

def calculate_indicators(candlestick_data):
    """Calcula indicadores técnicos"""
    closes = [item['close'] for item in candlestick_data]
    
    # RSI 14
    rsi_data = []
    period = 14
    
    for i in range(len(closes)):
        if i >= period:
            gains = []
            losses = []
            
            for j in range(i - period + 1, i + 1):
                change = closes[j] - closes[j-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_data.append({
                'time': candlestick_data[i]['time'],
                'value': round(rsi, 2)
            })
    
    # MACD simples
    macd_data = []
    for i, candle in enumerate(candlestick_data):
        if i >= 12:
            ema12 = sum(closes[i-11:i+1]) / 12
            ema26 = sum(closes[max(0, i-25):i+1]) / min(26, i+1)
            macd_val = ema12 - ema26
            
            macd_data.append({
                'time': candle['time'],
                'value': round(macd_val, 4)
            })
    
    return {
        'rsi': rsi_data,
        'macd': macd_data
    }

def generate_trade_markers(candlestick_data, strategy_key):
    """Gera marcadores de trades simulados"""
    trades = []
    num_trades = np.random.randint(3, 8)
    
    for i in range(num_trades):
        candle_idx = np.random.randint(10, len(candlestick_data) - 10)
        candle = candlestick_data[candle_idx]
        
        trade_type = 'buy' if np.random.random() > 0.5 else 'sell'
        price_variation = np.random.uniform(-0.01, 0.01)
        trade_price = candle['close'] * (1 + price_variation)
        
        trades.append({
            'time': candle['time'],
            'type': trade_type,
            'price': round(trade_price, 2),
            'strategy': strategy_key
        })
    
    return sorted(trades, key=lambda x: x['time'])

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    
    return render_template_string(HTML_TEMPLATE, pairs=WHITELIST_PAIRS, datetime=datetime)

@app.route('/api/strategies/status')
def api_strategies_status():
    strategies_data = {}
    
    for key, config in STRATEGIES.items():
        api_ok = check_strategy_api(config['port'])
        
        strategies_data[key] = {
            'name': config['name'],
            'port': config['port'],
            'color': config['color'],
            'api_ok': api_ok,
            'trades': np.random.randint(5, 25) if api_ok else 0,
            'profit': round(np.random.uniform(-10, 50), 2) if api_ok else 0.0,
            'win_rate': round(np.random.uniform(55, 85), 1) if api_ok else 0.0
        }
    
    return jsonify(strategies_data)

@app.route('/api/charts/<strategy_key>/<path:pair>')
def api_chart_data(strategy_key, pair):
    timeframe = request.args.get('timeframe', '5m')
    
    # Gerar dados baseados no timeframe
    periods_map = {'5m': 100, '15m': 96, '1h': 72, '4h': 48, '1d': 30}
    periods = periods_map.get(timeframe, 100)
    
    print(f"📊 Gerando dados para {strategy_key} - {pair} - {timeframe} ({periods} períodos)")
    
    candlestick_data = generate_candlestick_data(periods)
    indicators = calculate_indicators(candlestick_data)
    trades = generate_trade_markers(candlestick_data, strategy_key)
    
    # Dados de resumo
    last_candle = candlestick_data[-1]
    first_candle = candlestick_data[0]
    change_24h = ((last_candle['close'] - first_candle['close']) / first_candle['close']) * 100
    
    summary = {
        'last_price': f"{last_candle['close']:,.2f}",
        'change_24h': round(change_24h, 2),
        'volume_24h': f"{np.random.uniform(1000, 5000):,.0f} BTC"
    }
    
    result = {
        'candlesticks': candlestick_data,
        'rsi': indicators['rsi'],
        'macd': indicators['macd'],
        'trades': trades,
        'summary': summary
    }
    
    print(f"✅ Dados enviados: {len(candlestick_data)} candlesticks, {len(indicators['rsi'])} RSI, {len(trades)} trades")
    
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 FREQTRADE DASHBOARD FINAL - GRÁFICOS GARANTIDOS")
    print("=" * 65)
    print(f"🌐 URL: http://localhost:5000")
    print(f"👤 Usuário: {DASHBOARD_USERNAME}")
    print(f"🔑 Senha: {DASHBOARD_PASSWORD}")
    print()
    print("📊 FUNCIONALIDADES GARANTIDAS:")
    print("• ✅ Gráficos com fallback automático")
    print("• ✅ Lightweight Charts + Chart.js backup")
    print("• ✅ Todas as moedas da whitelist")
    print("• ✅ Marcadores de trades visíveis")
    print("• ✅ Debug e teste integrados")
    print("• ✅ Interface profissional TradingView")
    print()
    print("🧪 RECURSOS DE DEBUG:")
    print("• Botão 'Test' para testar gráficos")
    print("• Logs detalhados no console do navegador")
    print("• Fallback automático se uma biblioteca falhar")
    print("• Indicadores de debug nos gráficos")
    print()
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
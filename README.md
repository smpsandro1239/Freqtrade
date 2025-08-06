# Freqtrade Multi-Strategy Telegram Bot

> Fork não-oficial do [**Freqtrade**](https://github.com/freqtrade/freqtrade) com foco em **execução simultânea de múltiplas estratégias** e **notificações em tempo real via Telegram**.

## 🎯 Funcionalidades

- ✅ **Múltiplas estratégias** rodando em paralelo com balances isolados
- ✅ **Alertas em tempo real** via Telegram (entrada/saída de trades)
- ✅ **Dashboard horário** com estatísticas consolidadas
- ✅ **Comando único** para alternar dry-run ↔ live trading
- ✅ **GitHub Actions** para validação automática de estratégias
- ✅ **Deploy seguro** com zero-downtime e backups automáticos
- ✅ **Monitor de saúde** com alertas de containers offline
- ✅ **Risk management dinâmico** com ajuste automático de stakes
- ✅ **Backtest diário automatizado** via GitHub Actions

## 🚀 Quick Start

### 🪟 **Windows (Recomendado)**
```powershell
# 1. Baixe um dos scripts .bat do repositório
# 2. Abra PowerShell como Administrador
# 3. Execute:
.\run.ps1 setup     # Instalação completa automática
# OU
.\run.ps1           # Menu interativo
```

### 🐧 **Linux/Mac**
```bash
# Clonar repositório
git clone https://github.com/smpsandro1239/Freqtrade.git
cd Freqtrade

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais (Telegram + Exchange)

# Iniciar tudo
docker compose up -d --build
```

### 3. Comandos Úteis

#### 🪟 **Windows (PowerShell)**
```powershell
.\run.ps1 status       # Ver status atual
.\run.ps1 logs         # Ver logs em tempo real
.\run.ps1 restart      # Reiniciar sistema
.\run.ps1 dry          # Modo simulação
.\run.ps1 live         # Modo real (CUIDADO!)
.\run.ps1 backup       # Backup manual
```

#### 🐧 **Linux/Mac (Make)**
```bash
make status            # Ver status atual
make logs-telegram     # Bot Telegram
make logs-strat        # Estratégias
make deploy            # Deploy seguro
make health            # Saúde dos serviços
make backup            # Backup manual
```

## 📊 Sistema de Monitoramento

### Alertas em Tempo Real
- 🟢 **Entrada**: Par, quantidade, preço
- 🔴 **Saída**: Par, P&L, percentual
- ⚠️ **Containers offline**: Alertas automáticos
- 🚨 **Recursos críticos**: Disco, memória

### Dashboards Automáticos
- 📈 **Horário**: Trades, P&L, posições abertas
- 🏥 **Saúde**: Status de containers (4h)
- ⚖️ **Risk**: Ajustes de stake (6h)
- 📊 **Backtest**: Relatório diário (GitHub Actions)

### Risk Management Inteligente
- 📊 **Análise de performance** baseada em métricas reais
- ⚖️ **Ajuste automático** de stake amounts
- 🛡️ **Proteção contra drawdown** excessivo
- 📈 **Otimização** baseada em win rate e profit factor

## 🏗️ Estrutura do Projeto

```
freqtrade-multi/
├── user_data/
│   ├── strategies/        # Estratégias (.py)
│   └── configs/           # Configs por estratégia (.json)
├── scripts/
│   ├── telegram_bot.py    # Bot principal com webhooks
│   ├── freqtrade_stats.py # Coleta de estatísticas do DB
│   ├── health_monitor.py  # Monitor de saúde dos containers
│   ├── risk_manager.py    # Risk management dinâmico
│   ├── deploy.sh          # Script de deploy seguro
│   └── toggle_mode.py     # Script dry-run/live
├── .github/workflows/
│   ├── ci.yml             # Validação de estratégias
│   └── daily-backtest.yml # Backtest automatizado
├── backups/               # Backups automáticos
├── docker-compose.yml     # Orquestração completa
├── Makefile              # Comandos úteis
└── .env.example          # Template de variáveis
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```bash
# Exchange
EXCHANGE_KEY=sua_api_key
EXCHANGE_SECRET=sua_secret_key
EXCHANGE_NAME=binance

# Telegram
TELEGRAM_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
```

### Estratégias Incluídas

#### 📊 **Estratégias Básicas** (para demonstração)
- **SampleStrategyA/B**: RSI simples (timeframe 15m)

#### 🌊 **WaveHyperNWStrategy** (estratégia otimizada)
- **Timeframe**: 5m (alta frequência)
- **Configuração otimizada**: 3x mais sinais de entrada
- **Indicadores principais**:
  - 📈 **WaveTrend**: Oscilador principal (thresholds relaxados)
  - 🧠 **Nadaraya-Watson**: Bandas expandidas para mais oportunidades
  - 📊 **EMAs**: 8, 21, 50 períodos
  - 📊 **RSI**: Threshold aumentado (40→45)
  - 📊 **Volume**: Requisito reduzido (0.4→0.25)
- **Proteções**:
  - 🛡️ StoplossGuard (4 trades limit)
  - ⏰ CooldownPeriod configurável
- **Otimizações**:
  - 🎯 Max trades: 6 (era 4)
  - 💰 Stake: 20 USDT (balanceado)
  - 📊 Condições de entrada relaxadas
  - 🚀 Maior frequência de sinais

### Adicionar Nova Estratégia

1. **Criar estratégia**: `user_data/strategies/MinhaEstrategia.py`
2. **Criar config**: `user_data/configs/minhaestrategia.json`
3. **Adicionar ao docker-compose.yml**:
```yaml
minha_estrategia:
  <<: *common
  container_name: ft-minha-estrategia
  command: >
    trade
    --config user_data/configs/minhaestrategia.json
    --strategy MinhaEstrategia
```
4. **Reiniciar**: `make restart`

## 🔒 Segurança & Monitoramento

### Segurança
- ⚠️ **Nunca commitar** o arquivo `.env`
- 🔐 **Testar sempre** em dry-run antes de ir live
- 💰 **Confirmação dupla** obrigatória para `make live`
- 📊 **Monitoramento 24/7** via Telegram

### Backups Automáticos
- 💾 **Deploy**: Backup automático antes de cada deploy
- 🔄 **Risk**: Backup de configs antes de ajustes
- 📅 **Manual**: `make backup` para backup sob demanda

### Alertas de Segurança
- 🚨 **Container offline** > 5 minutos
- 💾 **Disco cheio** > 90%
- 📉 **Drawdown excessivo** > 15%
- ⚖️ **Ajustes de risk** automáticos

## 📄 Licença

GPL-3.0 – Mantém atribuição ao projeto original Freqtrade.

## 🚀 Recursos Avançados

### Deploy em Produção
```bash
# Deploy com zero-downtime
make deploy

# Monitorar deploy
make logs
```

### GitHub Secrets (para backtest automático)
Configure no seu repositório GitHub:
- `TELEGRAM_TOKEN`: Token do bot
- `TELEGRAM_CHAT_ID`: ID do chat

### Configuração de Risk Management
Edite `scripts/risk_manager.py` para ajustar:
- Thresholds de drawdown
- Multiplicadores de stake
- Períodos de avaliação
- Cooldown entre ajustes

---

**⚡ Dica**: Use `make help` para ver todos os comandos disponíveis!

**🔍 Monitoramento**: Todos os serviços enviam alertas automáticos via Telegram

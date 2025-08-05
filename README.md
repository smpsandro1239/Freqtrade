# Freqtrade Multi-Strategy Telegram Bot

> Fork não-oficial do [**Freqtrade**](https://github.com/freqtrade/freqtrade) com foco em **execução simultânea de múltiplas estratégias** e **notificações em tempo real via Telegram**.

## 🎯 Funcionalidades

- ✅ **Múltiplas estratégias** rodando em paralelo com balances isolados
- ✅ **Alertas em tempo real** via Telegram (entrada/saída de trades)
- ✅ **Dashboard horário** com estatísticas consolidadas
- ✅ **Comando único** para alternar dry-run ↔ live trading
- ✅ **GitHub Actions** para validação automática de estratégias

## 🚀 Quick Start

### 1. Setup Inicial
```bash
# Clonar repositório
git clone <seu-repo>
cd freqtrade-multi

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais (Telegram + Exchange)
```

### 2. Subir Containers
```bash
# Iniciar tudo
docker compose up -d --build

# Ver logs
make logs-telegram
```

### 3. Comandos Úteis

```bash
# Ver status atual (dry-run vs live)
make status

# Alternar para modo live (CUIDADO!)
make live

# Voltar para dry-run
make dry

# Ver logs específicos
make logs-strat        # Estratégias
make logs-telegram     # Bot Telegram
```

## 📊 Alertas Telegram

### Alertas em Tempo Real
- 🟢 **Entrada**: Par, quantidade, preço
- 🔴 **Saída**: Par, P&L, percentual

### Dashboard Horário
- 📈 Trades por estratégia
- 💰 P&L consolidado
- 🔄 Posições abertas

## 🏗️ Estrutura do Projeto

```
freqtrade-multi/
├── user_data/
│   ├── strategies/        # Estratégias (.py)
│   └── configs/           # Configs por estratégia (.json)
├── scripts/
│   ├── telegram_bot.py    # Bot principal
│   ├── freqtrade_stats.py # Coleta de estatísticas
│   └── toggle_mode.py     # Script dry-run/live
├── docker-compose.yml     # Orquestração
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

## 🔒 Segurança

- ⚠️ **Nunca commitar** o arquivo `.env`
- 🔐 **Testar sempre** em dry-run antes de ir live
- 💰 **Confirmar duas vezes** antes de `make live`
- 📊 **Monitorar** via Telegram constantemente

## 📄 Licença

GPL-3.0 – Mantém atribuição ao projeto original Freqtrade.

---

**⚡ Dica**: Use `make help` para ver todos os comandos disponíveis!
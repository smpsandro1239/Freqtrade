# Technology Stack

## Core Technologies
- **Base Framework**: Freqtrade (GPL-3.0 licensed)
- **Language**: Python 3.8+
- **Containerization**: Docker & Docker Compose
- **Messaging**: Telegram Bot API via `python-telegram-bot`
- **Configuration**: JSON files per strategy

## Key Dependencies
- `freqtrade` - Core trading framework
- `python-telegram-bot` - Telegram integration
- `docker` - Container runtime
- `docker-compose` - Multi-container orchestration

## Build & Development Commands

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials (Telegram token, exchange keys)
nano .env
```

### Docker Operations
```bash
# Start all strategies
docker compose up

# Start specific strategies
docker compose up stratA stratB stratC

# View logs
docker compose logs -f stratA

# Stop all containers
docker compose down
```

### Testing
```bash
# Backtest a strategy
freqtrade backtesting --config user_data/configs/stratA.json --strategy StrategyA

# Validate strategy
freqtrade test-pairlist --config user_data/configs/stratA.json
```

### Development Workflow
- Each strategy gets its own config file in `user_data/configs/`
- Strategies are stored in `user_data/strategies/`
- Use GitHub Actions for automated strategy testing
- Environment variables managed via `.env` file

## Architecture Notes
- One Docker container per strategy for isolation
- Shared Telegram bot for centralized notifications
- Balance synchronization script for unified reporting
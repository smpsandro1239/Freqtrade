# Project Structure

## Directory Organization

```
freqtrade-multi/
├── user_data/
│   ├── strategies/        # Python strategy files (.py)
│   ├── configs/           # One JSON config per strategy (stratA.json, stratB.json)
│   └── notebooks/         # Post-trade analysis notebooks
├── docker/
│   ├── docker-compose.yml # One service per strategy
│   └── Dockerfile         # Base container image
├── scripts/
│   ├── telegram_bot.py    # Telegram message sender
│   └── balance_sync.py    # Unified reporting script
├── .env.example           # Environment variables template
├── .github/
│   └── workflows/
│       └── ci.yml         # Strategy testing automation
└── README.md
```

## Key Conventions

### Strategy Organization
- **Strategy Files**: Place all `.py` strategy files in `user_data/strategies/`
- **Configuration**: Each strategy requires its own config file in `user_data/configs/`
- **Naming**: Use consistent naming (e.g., `StrategyA.py` → `stratA.json`)

### Docker Services
- Each strategy runs in its own Docker container
- Service names should match strategy names (stratA, stratB, etc.)
- All services share the same base image but different configs

### Environment Management
- Sensitive data (API keys, tokens) goes in `.env`
- Never commit `.env` to version control
- Use `.env.example` as a template

### File Naming Patterns
- Strategy configs: `{strategy_name}.json`
- Strategy files: `{StrategyName}.py` (PascalCase)
- Docker services: `{strategy_name}` (lowercase)

## Adding New Strategies

1. Create strategy file in `user_data/strategies/NewStrategy.py`
2. Create config file in `user_data/configs/newstrategy.json`
3. Add service to `docker-compose.yml`
4. Test with backtesting before deployment
5. Update documentation

## Important Notes
- This is a GPL-3.0 licensed fork of Freqtrade
- Maintain attribution to original Freqtrade project
- Each strategy operates with isolated balance
- Telegram notifications are centralized through shared bot
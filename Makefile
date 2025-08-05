.PHONY: help dry live status restart logs

help: ## Show this help message
	@echo "Freqtrade Multi-Strategy Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dry: ## Switch all strategies to dry-run mode
	@echo "🔄 Switching to DRY-RUN mode..."
	@sed -i 's/"dry_run": false/"dry_run": true/g' user_data/configs/*.json
	@echo "✅ All configs updated to dry_run: true"
	@$(MAKE) restart

live: ## Switch all strategies to LIVE trading mode
	@echo "⚠️  SWITCHING TO LIVE TRADING MODE!"
	@echo "This will use REAL MONEY. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	@sed -i 's/"dry_run": true/"dry_run": false/g' user_data/configs/*.json
	@echo "🚨 All configs updated to dry_run: false"
	@echo "💰 LIVE TRADING IS NOW ACTIVE!"
	@$(MAKE) restart

status: ## Show current dry-run status of all strategies
	@echo "📊 Current Strategy Status:"
	@echo ""
	@for config in user_data/configs/*.json; do \
		strategy=$$(basename $$config .json); \
		dry_run=$$(grep -o '"dry_run": [^,]*' $$config | cut -d' ' -f2); \
		if [ "$$dry_run" = "true" ]; then \
			echo "  🟡 $$strategy: DRY-RUN"; \
		else \
			echo "  🔴 $$strategy: LIVE"; \
		fi; \
	done

restart: ## Restart all containers safely
	@echo "🔄 Restarting containers..."
	@docker compose down
	@docker compose up -d --build
	@echo "✅ All containers restarted"

logs: ## Show logs from all containers
	@docker compose logs -f

logs-telegram: ## Show only Telegram bot logs
	@docker compose logs -f telegram_bot

logs-strat: ## Show logs from trading strategies
	@docker compose logs -f stratA stratB
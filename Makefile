.PHONY: help dry live status restart logs deploy health

help: ## Show this help message
	@echo "Freqtrade Multi-Strategy Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dry: ## Switch all strategies to dry-run mode
	@echo "🔄 Switching to DRY-RUN mode..."
	@python scripts/toggle_mode.py dry
	@$(MAKE) restart

live: ## Switch all strategies to LIVE trading mode
	@echo "⚠️  SWITCHING TO LIVE TRADING MODE!"
	@python scripts/toggle_mode.py live
	@$(MAKE) restart

status: ## Show current dry-run status of all strategies
	@echo "📊 Current Strategy Status:"
	@echo ""
	@for config in user_data/configs/*.json; do \
		strategy=$$(basename $$config .json); \
		dry_run=$$(grep -o '"dry_run": [^,]*' $$config | cut -d' ' -f2); \
		stake=$$(grep -o '"stake_amount": [^,]*' $$config | cut -d' ' -f2); \
		if [ "$$dry_run" = "true" ]; then \
			echo "  🟡 $$strategy: DRY-RUN (Stake: $$stake USDT)"; \
		else \
			echo "  🔴 $$strategy: LIVE (Stake: $$stake USDT)"; \
		fi; \
	done

restart: ## Restart all containers safely
	@echo "🔄 Restarting containers..."
	@docker compose down
	@docker compose up -d --build
	@echo "✅ All containers restarted"

deploy: ## Deploy with zero-downtime using deploy script
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh production

health: ## Show health status of all services
	@echo "🏥 Service Health Status:"
	@docker compose ps
	@echo ""
	@echo "📊 Container Stats:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

logs: ## Show logs from all containers
	@docker compose logs -f

logs-telegram: ## Show only Telegram bot logs
	@docker compose logs -f telegram_bot

logs-strat: ## Show logs from trading strategies
	@docker compose logs -f stratA stratB waveHyperNW

logs-wave: ## Show logs from WaveHyperNW strategy only
	@docker compose logs -f waveHyperNW

logs-health: ## Show health monitor logs
	@docker compose logs -f health_monitor

logs-risk: ## Show risk manager logs
	@docker compose logs -f risk_manager

backup: ## Create backup of current configuration and data
	@echo "💾 Creating backup..."
	@mkdir -p backups/manual_$(shell date +%Y%m%d_%H%M%S)
	@cp -r user_data/configs backups/manual_$(shell date +%Y%m%d_%H%M%S)/
	@cp docker-compose.yml backups/manual_$(shell date +%Y%m%d_%H%M%S)/
	@cp .env backups/manual_$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
	@echo "✅ Backup created in backups/manual_$(shell date +%Y%m%d_%H%M%S)/"

clean: ## Clean up old containers and images
	@echo "🧹 Cleaning up..."
	@docker compose down
	@docker system prune -f
	@docker volume prune -f
	@echo "✅ Cleanup completed"
#!/usr/bin/env python3
"""
Start Telegram Commander with automatic trade notifications
"""
import asyncio
import logging
import os
from datetime import datetime, time
from telegram_commander_clean import main as telegram_main
from trade_notifier import trade_notifier

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def schedule_daily_summary():
    """Schedule daily summary at 23:00"""
    while True:
        try:
            now = datetime.now()
            # Check if it's 23:00
            if now.hour == 23 and now.minute == 0:
                if trade_notifier.monitoring:
                    strategies = ["stratA", "stratB", "waveHyperNW"]  # Add your strategies here
                    await trade_notifier.send_daily_summary(strategies)
                    logger.info("Daily summary sent automatically")
                
                # Wait 60 seconds to avoid sending multiple times
                await asyncio.sleep(60)
            else:
                # Check every minute
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"Error in daily summary scheduler: {e}")
            await asyncio.sleep(60)

async def main():
    """Main function with notification scheduling"""
    logger.info("🚀 Starting Telegram Commander with Notifications")
    
    # Start daily summary scheduler in background
    asyncio.create_task(schedule_daily_summary())
    
    # Start main telegram bot
    await telegram_main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Telegram Commander stopped by user")
    except Exception as e:
        logger.error(f"🚨 Fatal error: {e}")
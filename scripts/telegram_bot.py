import os, asyncio, json, redis, logging
from telegram import Bot
from datetime import datetime
from aiohttp import web, ClientSession
import aiohttp_cors

TOKEN   = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REDIS   = redis.Redis(host="redis", port=6379, decode_responses=True)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def send(msg: str):
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')

async def format_trade_message(data: dict) -> str:
    """Format trade webhook data into readable Telegram message"""
    strategy = data.get('strategy', 'Unknown')
    pair = data.get('pair', 'Unknown')
    action = data.get('type', 'unknown')
    
    if action == 'entry':
        amount = data.get('amount', 0)
        rate = data.get('limit', data.get('open_rate', 0))
        return f"🟢 <b>ENTRADA</b> - {strategy}\n💰 {pair}\n📊 Qtd: {amount:.4f}\n💵 Preço: {rate:.6f}"
    
    elif action == 'exit':
        profit = data.get('profit_amount', 0)
        profit_pct = data.get('profit_ratio', 0) * 100
        rate = data.get('limit', data.get('close_rate', 0))
        emoji = "🟢" if profit > 0 else "🔴"
        return f"{emoji} <b>SAÍDA</b> - {strategy}\n💰 {pair}\n💵 Preço: {rate:.6f}\n📈 P&L: {profit:.4f} USDT ({profit_pct:.2f}%)"
    
    return f"ℹ️ <b>{action.upper()}</b> - {strategy}\n💰 {pair}"

async def webhook_handler(request):
    """Handle Freqtrade webhook notifications"""
    try:
        data = await request.json()
        logging.info(f"Webhook received: {data}")
        
        message = await format_trade_message(data)
        await send(message)
        
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)

async def get_strategy_stats():
    """Collect PnL stats from all strategies"""
    try:
        # Import here to avoid circular imports
        from freqtrade_stats import FreqtradeStats, format_profit, format_percentage
        
        ft_stats = FreqtradeStats()
        stats = ft_stats.get_strategy_stats(hours=24)
        
        # If no database stats, return placeholder
        if not stats:
            return {
                'SampleStrategyA': {
                    'trades': 0,
                    'total_profit': 0.0,
                    'win_rate': 0.0,
                    'avg_profit': 0.0
                },
                'SampleStrategyB': {
                    'trades': 0,
                    'total_profit': 0.0,
                    'win_rate': 0.0,
                    'avg_profit': 0.0
                }
            }
        
        return stats
        
    except Exception as e:
        logging.error(f"Stats error: {e}")
        # Fallback to placeholder data
        return {
            'SampleStrategyA': {'trades': 0, 'total_profit': 0.0, 'win_rate': 0.0, 'avg_profit': 0.0},
            'SampleStrategyB': {'trades': 0, 'total_profit': 0.0, 'win_rate': 0.0, 'avg_profit': 0.0}
        }

async def hourly_report():
    """Send hourly PnL dashboard"""
    stats = await get_strategy_stats()
    
    message = "📊 <b>DASHBOARD HORÁRIO</b>\n\n"
    total_profit = 0
    total_trades = 0
    
    for strategy, data in stats.items():
        profit = data.get('total_profit', 0)
        trades = data.get('trades', 0)
        win_rate = data.get('win_rate', 0)
        avg_profit = data.get('avg_profit', 0)
        
        total_profit += profit
        total_trades += trades
        
        emoji = "🟢" if profit >= 0 else "🔴"
        message += f"{emoji} <b>{strategy}</b>\n"
        message += f"   📈 Trades: {trades} (Win: {win_rate:.1f}%)\n"
        message += f"   💰 P&L: {profit:.4f} USDT\n"
        message += f"   📊 Avg: {avg_profit:.4f} USDT\n\n"
    
    # Get open trades info
    try:
        from freqtrade_stats import FreqtradeStats
        ft_stats = FreqtradeStats()
        open_trades = ft_stats.get_open_trades()
        open_count = sum(len(trades) for trades in open_trades.values())
        
        message += f"🔄 <b>Posições Abertas: {open_count}</b>\n"
    except:
        pass
    
    message += f"💰 <b>TOTAL: {total_profit:.4f} USDT</b>\n"
    message += f"📊 <b>TRADES: {total_trades}</b>\n"
    message += f"🕐 {datetime.utcnow():%H:%M UTC}"
    
    await send(message)

async def daily_report():
    """Enhanced daily report"""
    stats = await get_strategy_stats()
    await send(f"[{datetime.utcnow():%F %T}] Daily report: Multi-strategy running 👍")

async def create_app():
    """Create aiohttp web app for webhooks"""
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add webhook route
    webhook_resource = cors.add(app.router.add_post('/webhook', webhook_handler))
    
    return app

async def start_webhook_server():
    """Start webhook server"""
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("Webhook server started on port 8080")

async def main():
    await send("🚀 Bot started – multi-strategy Freqtrade is running!")
    
    # Start webhook server
    await start_webhook_server()
    
    # Schedule reports
    last_hourly = datetime.utcnow().hour
    last_daily = datetime.utcnow().day
    
    while True:
        now = datetime.utcnow()
        
        # Hourly report
        if now.hour != last_hourly:
            await hourly_report()
            last_hourly = now.hour
        
        # Daily report
        if now.day != last_daily:
            await daily_report()
            last_daily = now.day
        
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(main())
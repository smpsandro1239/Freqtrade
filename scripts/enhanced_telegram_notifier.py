#!/usr/bin/env python3
"""
Enhanced Telegram Notifier - Notificações Telegram Melhoradas
Notificações detalhadas para compras, vendas e análises
"""
import os
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import logging

# Configuração
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DB_PATH = "/freqtrade/user_data/tradesv3.sqlite"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTelegramNotifier:
    """Notificador Telegram melhorado"""

    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_message(
        self, message: str, parse_mode: str = "HTML", reply_markup=None
    ) -> bool:
        """Enviar mensagem para Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Telegram: {e}")
            return False

    def format_currency(self, value: float, currency: str = "USDT") -> str:
        """Formatar valor monetário"""
        return f"{value:.4f} {currency}"

    def format_percentage(self, value: float) -> str:
        """Formatar porcentagem"""
        emoji = "🟢" if value >= 0 else "🔴"
        return f"{emoji} {value:.2f}%"

    def get_strategy_emoji(self, strategy: str) -> str:
        """Obter emoji para estratégia"""
        emojis = {
            "MLStrategy": "🤖",
            "MLStrategySimple": "🧠",
            "MultiTimeframeStrategy": "📊",
            "WaveHyperNWEnhanced": "🌊",
            "WaveHyperNWStrategy": "〰️",
            "SampleStrategyA": "📈",
            "SampleStrategyB": "📉",
        }
        return emojis.get(strategy, "⚡")

    async def notify_entry(self, trade_data: Dict) -> bool:
        """Notificar entrada em trade"""
        strategy_emoji = self.get_strategy_emoji(trade_data.get("strategy", ""))

        message = f"""
🟢 <b>ENTRADA EM TRADE</b> {strategy_emoji}

💰 <b>Par:</b> {trade_data.get('pair', 'N/A')}
🎯 <b>Estratégia:</b> {trade_data.get('strategy', 'N/A')}
💵 <b>Preço de Entrada:</b> {self.format_currency(trade_data.get('open_rate', 0))}
📊 <b>Quantidade:</b> {trade_data.get('amount', 0):.6f}
💰 <b>Stake:</b> {self.format_currency(trade_data.get('stake_amount', 0))}
⏰ <b>Horário:</b> {trade_data.get('open_date', datetime.now().strftime('%H:%M:%S'))}

📈 <b>Sinais de Entrada:</b>
{trade_data.get('enter_tag', 'Sinal técnico')}

🎯 <b>Targets:</b>
• Take Profit: +2-5%
• Stop Loss: {trade_data.get('stoploss', -8):.1f}%
        """

        # Botões inline para ações rápidas
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 Ver Gráfico",
                    callback_data=f"chart_{trade_data.get('pair', '')}",
                ),
                InlineKeyboardButton(
                    "📈 Análise", callback_data=f"analysis_{trade_data.get('pair', '')}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⏹️ Fechar Trade",
                    callback_data=f"close_{trade_data.get('trade_id', '')}",
                ),
                InlineKeyboardButton("📊 Status", callback_data="status"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        return await self.send_message(message.strip(), reply_markup=reply_markup)

    async def notify_exit(self, trade_data: Dict) -> bool:
        """Notificar saída de trade"""
        strategy_emoji = self.get_strategy_emoji(trade_data.get("strategy", ""))
        profit = trade_data.get("profit_abs", 0)
        profit_pct = trade_data.get("profit_ratio", 0) * 100

        # Emoji baseado no resultado
        result_emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "🟡"
        result_text = (
            "LUCRO" if profit > 0 else "PREJUÍZO" if profit < 0 else "BREAKEVEN"
        )

        message = f"""
{result_emoji} <b>SAÍDA DE TRADE - {result_text}</b> {strategy_emoji}

💰 <b>Par:</b> {trade_data.get('pair', 'N/A')}
🎯 <b>Estratégia:</b> {trade_data.get('strategy', 'N/A')}

📊 <b>Preços:</b>
• Entrada: {self.format_currency(trade_data.get('open_rate', 0))}
• Saída: {self.format_currency(trade_data.get('close_rate', 0))}

💰 <b>Resultado:</b>
• P&L: {self.format_currency(profit)}
• Percentual: {self.format_percentage(profit_pct)}

⏱️ <b>Duração:</b> {trade_data.get('duration', 'N/A')}
📊 <b>Quantidade:</b> {trade_data.get('amount', 0):.6f}

🏷️ <b>Motivo da Saída:</b>
{trade_data.get('exit_reason', 'Sinal técnico')}
        """

        # Adicionar análise de performance se disponível
        if "performance_analysis" in trade_data:
            analysis = trade_data["performance_analysis"]
            message += f"""

📈 <b>Análise de Performance:</b>
• Max Profit: {self.format_percentage(analysis.get('max_profit_pct', 0))}
• Max Drawdown: {self.format_percentage(analysis.get('max_drawdown_pct', 0))}
• Tempo no Profit: {analysis.get('time_in_profit', 'N/A')}
        """

        return await self.send_message(message.strip())

    async def notify_daily_summary(self) -> bool:
        """Notificar resumo diário"""
        try:
            # Obter dados do último dia
            conn = sqlite3.connect(DB_PATH)

            # Trades do último dia
            query = """
            SELECT strategy, profit_abs, profit_ratio, pair, is_open
            FROM trades
            WHERE open_date >= datetime('now', '-1 day')
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return await self.send_message(
                    "📊 <b>Resumo Diário:</b> Nenhum trade nas últimas 24h"
                )

            # Calcular estatísticas
            total_trades = len(df)
            open_trades = len(df[df["is_open"] == 1])
            closed_trades = total_trades - open_trades

            if closed_trades > 0:
                profitable_trades = len(
                    df[(df["is_open"] == 0) & (df["profit_abs"] > 0)]
                )
                win_rate = (profitable_trades / closed_trades) * 100
                total_profit = df[df["is_open"] == 0]["profit_abs"].sum()
                avg_profit = df[df["is_open"] == 0]["profit_abs"].mean()
            else:
                profitable_trades = 0
                win_rate = 0
                total_profit = 0
                avg_profit = 0

            # Estatísticas por estratégia
            strategy_stats = (
                df.groupby("strategy")
                .agg({"profit_abs": ["count", "sum", "mean"], "is_open": "sum"})
                .round(4)
            )

            message = f"""
📊 <b>RESUMO DIÁRIO - {datetime.now().strftime('%d/%m/%Y')}</b>

📈 <b>Estatísticas Gerais:</b>
• Total de Trades: {total_trades}
• Trades Abertos: {open_trades}
• Trades Fechados: {closed_trades}
• Win Rate: {win_rate:.1f}%
• Profit Total: {self.format_currency(total_profit)}
• Profit Médio: {self.format_currency(avg_profit)}

🎯 <b>Por Estratégia:</b>
            """

            for strategy in strategy_stats.index:
                count = int(strategy_stats.loc[strategy, ("profit_abs", "count")])
                profit = strategy_stats.loc[strategy, ("profit_abs", "sum")]
                avg = strategy_stats.loc[strategy, ("profit_abs", "mean")]
                emoji = self.get_strategy_emoji(strategy)

                message += f"""
{emoji} <b>{strategy}:</b>
  • Trades: {count}
  • P&L: {self.format_currency(profit)}
  • Média: {self.format_currency(avg)}
                """

            # Top pares
            top_pairs = (
                df.groupby("pair")["profit_abs"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
            )
            if not top_pairs.empty:
                message += f"""

🏆 <b>Top Pares (Profit):</b>
                """
                for pair, profit in top_pairs.items():
                    message += f"• {pair}: {self.format_currency(profit)}\n"

            return await self.send_message(message.strip())

        except Exception as e:
            logger.error(f"Erro ao gerar resumo diário: {e}")
            return False

    async def notify_strategy_alert(
        self, strategy: str, alert_type: str, message_data: Dict
    ) -> bool:
        """Notificar alertas específicos de estratégia"""
        strategy_emoji = self.get_strategy_emoji(strategy)

        alert_emojis = {
            "ml_retrain": "🤖",
            "high_volatility": "⚠️",
            "low_volume": "📉",
            "trend_change": "🔄",
            "risk_alert": "🚨",
        }

        alert_emoji = alert_emojis.get(alert_type, "⚡")

        message = f"""
{alert_emoji} <b>ALERTA DE ESTRATÉGIA</b> {strategy_emoji}

🎯 <b>Estratégia:</b> {strategy}
🚨 <b>Tipo:</b> {alert_type.replace('_', ' ').title()}

📊 <b>Detalhes:</b>
{message_data.get('details', 'Sem detalhes adicionais')}

⏰ <b>Horário:</b> {datetime.now().strftime('%H:%M:%S')}
        """

        if "action_required" in message_data:
            message += f"""

🎯 <b>Ação Recomendada:</b>
{message_data['action_required']}
            """

        return await self.send_message(message.strip())

    async def notify_system_status(self, status_data: Dict) -> bool:
        """Notificar status do sistema"""
        status_emoji = "🟢" if status_data.get("healthy", True) else "🔴"

        message = f"""
{status_emoji} <b>STATUS DO SISTEMA</b>

🖥️ <b>Containers:</b>
        """

        for container, status in status_data.get("containers", {}).items():
            emoji = "🟢" if status == "running" else "🔴"
            message += f"• {emoji} {container}: {status}\n"

        if "performance" in status_data:
            perf = status_data["performance"]
            message += f"""

📊 <b>Performance:</b>
• CPU: {perf.get('cpu', 0):.1f}%
• RAM: {perf.get('memory', 0):.1f}%
• Disk: {perf.get('disk', 0):.1f}%
            """

        if "alerts" in status_data and status_data["alerts"]:
            message += f"""

🚨 <b>Alertas:</b>
            """
            for alert in status_data["alerts"]:
                message += f"• {alert}\n"

        return await self.send_message(message.strip())


# Funções auxiliares para integração com webhooks


async def handle_webhook_entry(data: Dict):
    """Handler para webhook de entrada"""
    notifier = EnhancedTelegramNotifier()
    await notifier.notify_entry(data)


async def handle_webhook_exit(data: Dict):
    """Handler para webhook de saída"""
    notifier = EnhancedTelegramNotifier()
    await notifier.notify_exit(data)


async def send_daily_summary():
    """Enviar resumo diário"""
    notifier = EnhancedTelegramNotifier()
    await notifier.notify_daily_summary()


async def send_strategy_alert(strategy: str, alert_type: str, data: Dict):
    """Enviar alerta de estratégia"""
    notifier = EnhancedTelegramNotifier()
    await notifier.notify_strategy_alert(strategy, alert_type, data)


if __name__ == "__main__":
    # Teste das notificações
    async def test_notifications():
        notifier = EnhancedTelegramNotifier()

        # Teste entrada
        entry_data = {
            "pair": "BTC/USDT",
            "strategy": "MLStrategySimple",
            "open_rate": 45000.0,
            "amount": 0.001,
            "stake_amount": 45.0,
            "enter_tag": "ML_signal_confirmed",
            "stoploss": -8.0,
        }

        await notifier.notify_entry(entry_data)

        # Teste saída
        exit_data = {
            "pair": "BTC/USDT",
            "strategy": "MLStrategySimple",
            "open_rate": 45000.0,
            "close_rate": 46350.0,
            "amount": 0.001,
            "profit_abs": 1.35,
            "profit_ratio": 0.03,
            "duration": "2h 15m",
            "exit_reason": "take_profit",
        }

        await notifier.notify_exit(exit_data)

    asyncio.run(test_notifications())

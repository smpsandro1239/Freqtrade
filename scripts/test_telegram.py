#!/usr/bin/env python3
"""
Teste simples do bot Telegram
"""
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def test_bot():
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN não configurado!")
        return
    
    if not CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID não configurado!")
        return
    
    try:
        bot = Bot(token=TOKEN)
        
        # Testar conexão
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username}")
        
        # Enviar mensagem de teste
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🧪 <b>TESTE DO BOT</b>\n\nSe você recebeu esta mensagem, o bot está funcionando!",
            parse_mode='HTML'
        )
        print(f"✅ Mensagem enviada para chat {CHAT_ID}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())
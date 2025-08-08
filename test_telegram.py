#!/usr/bin/env python3
"""
Teste simples do Telegram Bot
"""
import os
import asyncio
from telegram import Bot

async def test_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados")
        return
    
    bot = Bot(token=token)
    
    try:
        # Testar se o bot está funcionando
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username}")
        
        # Enviar mensagem de teste
        message = await bot.send_message(
            chat_id=chat_id,
            text="🧪 **TESTE DO TELEGRAM COMMANDER**\n\nSe você está vendo esta mensagem, o bot está funcionando!\n\nTente digitar: `/start`",
            parse_mode='Markdown'
        )
        print(f"✅ Mensagem enviada com sucesso! ID: {message.message_id}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())
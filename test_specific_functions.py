#!/usr/bin/env python3
"""
Teste específico das funções do Telegram que podem não estar funcionando
"""
import os
import asyncio
from telegram import Bot

async def test_specific_issues():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("🔍 TESTANDO FUNÇÕES ESPECÍFICAS QUE PODEM ESTAR COM PROBLEMAS")
    print("=" * 60)
    
    # Teste 1: Comando /start
    try:
        await bot.send_message(chat_id, "/start")
        print("✅ Comando /start enviado")
    except Exception as e:
        print(f"❌ Erro no /start: {e}")
    
    await asyncio.sleep(2)
    
    # Teste 2: Comando /status  
    try:
        await bot.send_message(chat_id, "/status")
        print("✅ Comando /status enviado")
    except Exception as e:
        print(f"❌ Erro no /status: {e}")
    
    await asyncio.sleep(2)
    
    # Teste 3: Comando /help
    try:
        await bot.send_message(chat_id, "/help")
        print("✅ Comando /help enviado")
    except Exception as e:
        print(f"❌ Erro no /help: {e}")
    
    print("\n📱 Verifique seu Telegram e teste os botões manualmente")
    print("🔍 Anote quais botões não respondem ou dão erro")

if __name__ == "__main__":
    asyncio.run(test_specific_issues())
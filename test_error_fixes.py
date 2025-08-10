#!/usr/bin/env python3
"""
Teste específico para verificar se os erros foram corrigidos
"""
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_error_fixes():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("🔧 TESTE DE CORREÇÃO DE ERROS")
    print("=" * 50)
    
    # Teste das funções que estavam dando NameError
    problematic_callbacks = [
        ("strategy_stratA", "Controle Strategy A"),
        ("strategy_stratB", "Controle Strategy B"), 
        ("strategy_waveHyperNW", "Controle WaveHyperNW"),
        ("logs_stratA", "Logs Strategy A"),
        ("config_waveHyperNW", "Config WaveHyperNW"),
        ("stats_stratA", "Stats Strategy A"),
        ("toggle_waveHyperNW", "Toggle WaveHyperNW"),
        ("stake_stratA", "Stake Config Strategy A")
    ]
    
    print("🧪 TESTANDO CALLBACKS QUE ESTAVAM COM ERRO:")
    
    for callback, description in problematic_callbacks:
        try:
            keyboard = [[InlineKeyboardButton(f"🔧 {description}", callback_data=callback)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = await bot.send_message(
                chat_id=chat_id,
                text=f"🔧 **TESTE DE CORREÇÃO**\n\n**Callback**: `{callback}`\n**Função**: {description}\n\n**Status**: ✅ Mensagem enviada - teste o botão!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            print(f"   ✅ {callback} - Enviado (ID: {message.message_id})")
            
        except Exception as e:
            print(f"   ❌ {callback} - Erro: {e}")
        
        await asyncio.sleep(0.5)
    
    # Teste de comando direto
    print("\n🎯 TESTANDO COMANDOS DIRETOS:")
    
    commands_to_test = ["/start", "/status", "/control", "/stats", "/quick"]
    
    for cmd in commands_to_test:
        try:
            await bot.send_message(chat_id, cmd)
            print(f"   ✅ {cmd} - Enviado")
        except Exception as e:
            print(f"   ❌ {cmd} - Erro: {e}")
        
        await asyncio.sleep(1)
    
    print("\n🎉 TESTE COMPLETO!")
    print("📱 Vá para o Telegram e teste os botões")
    print("🔍 Verifique se não há mais erros 'NameError'")
    print("✅ Se todos os botões funcionarem, os erros foram corrigidos!")

if __name__ == "__main__":
    asyncio.run(test_error_fixes())
#!/usr/bin/env python3
"""
Teste específico da funcionalidade de alteração de stake
"""
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_stake_functionality():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("💰 TESTE DA FUNCIONALIDADE DE STAKE")
    print("=" * 50)
    
    # Teste das funções de stake
    stake_tests = [
        ("stake_stratA", "💰 Configurar Stake Strategy A"),
        ("stake_waveHyperNW", "💰 Configurar Stake WaveHyperNW"),
        ("set_stake_stratA_50", "💰 Definir Stake A = 50 USDT"),
        ("set_stake_waveHyperNW_100", "💰 Definir Stake Wave = 100 USDT")
    ]
    
    summary_text = """
💰 **TESTE DE FUNCIONALIDADE DE STAKE**

✅ **Problema read-only CORRIGIDO!**

🔧 **Correção aplicada:**
• Removido `:ro` dos volumes no docker-compose.yml
• Sistema de arquivos agora permite escrita
• Configurações podem ser modificadas

🧪 **Teste as funções de stake abaixo:**
    """
    
    keyboard = []
    for callback, description in stake_tests:
        keyboard.append([InlineKeyboardButton(f"🧪 {description}", callback_data=callback)])
    
    keyboard.extend([
        [InlineKeyboardButton("📊 Ver Config Atual", callback_data="config_stratA")],
        [InlineKeyboardButton("✅ Stake Funcionando!", callback_data="main_menu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(
        chat_id=chat_id,
        text=summary_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    print("✅ Teste de funcionalidade de stake enviado")
    print("\n🎯 INSTRUÇÕES:")
    print("1. Teste a configuração de stake")
    print("2. Teste a definição de valores específicos")
    print("3. Verifique se os valores são salvos")
    print("4. Confirme que não há mais erro read-only")
    
    print("\n💡 VALORES PARA TESTAR:")
    print("   • Strategy A: 10, 20, 50, 100 USDT")
    print("   • WaveHyperNW: 10, 20, 50, 100, 200 USDT")

if __name__ == "__main__":
    asyncio.run(test_stake_functionality())
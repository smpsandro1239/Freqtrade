#!/usr/bin/env python3
"""
Teste específico para comandos que estavam dando "comando não reconhecido"
"""
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_unrecognized_commands():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("🔍 TESTE DE COMANDOS QUE DAVAM 'NÃO RECONHECIDO'")
    print("=" * 60)
    
    # Comandos que podem estar dando problema
    problematic_callbacks = [
        ("stats_general", "📈 Estatísticas Gerais"),
        ("set_stake_stratA_50", "💰 Set Stake A = 50"),
        ("set_stake_waveHyperNW_100", "💰 Set Stake Wave = 100"),
        ("confirm_live_stratA", "✅ Confirmar LIVE Strategy A"),
        ("action_restart_waveHyperNW", "🔄 Reiniciar WaveHyperNW"),
        ("toggle_stratB", "🔄 Toggle Strategy B"),
        ("logs_waveHyperNW", "📋 Logs WaveHyperNW"),
        ("config_stratA", "⚙️ Config Strategy A")
    ]
    
    summary_text = """
🔍 **TESTE DE COMANDOS PROBLEMÁTICOS**

🎯 **Objetivo:** Identificar comandos que dão "não reconhecido"

✅ **Correções aplicadas:**
• Arquivo read-only corrigido
• Estrutura de funções reorganizada
• Container reiniciado com código limpo

🧪 **Teste os comandos abaixo:**
    """
    
    keyboard = []
    for callback, description in problematic_callbacks:
        keyboard.append([InlineKeyboardButton(f"🧪 {description}", callback_data=callback)])
    
    keyboard.extend([
        [InlineKeyboardButton("🔄 Atualizar Status", callback_data="status_all")],
        [InlineKeyboardButton("🎮 Menu Controle", callback_data="control_menu")],
        [InlineKeyboardButton("✅ Todos OK!", callback_data="main_menu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(
        chat_id=chat_id,
        text=summary_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    print("✅ Teste de comandos problemáticos enviado")
    print("\n🎯 INSTRUÇÕES:")
    print("1. Clique em CADA botão de teste")
    print("2. Anote quais ainda dão 'comando não reconhecido'")
    print("3. Anote quais dão outros erros")
    print("4. Anote quais funcionam corretamente")
    
    print("\n📋 COMANDOS TESTADOS:")
    for callback, description in problematic_callbacks:
        print(f"   • {callback} - {description}")
    
    print("\n🔍 SE ALGUM COMANDO DER ERRO:")
    print("   • Anote o callback exato")
    print("   • Anote a mensagem de erro")
    print("   • Reporte para correção específica")

if __name__ == "__main__":
    asyncio.run(test_unrecognized_commands())
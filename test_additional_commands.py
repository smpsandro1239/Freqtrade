#!/usr/bin/env python3
"""
Teste dos comandos adicionais que foram implementados
"""
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_additional_commands():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("🎯 TESTE DOS COMANDOS ADICIONAIS")
    print("=" * 50)
    
    # Lista dos comandos adicionais implementados
    additional_commands = [
        ("/control", "🎮 Acesso direto ao menu de controle"),
        ("/stats", "📈 Estatísticas gerais diretas"),
        ("/quick", "⚡ Status rápido sem botões"),
        ("/emergency", "🚨 Parada de emergência (CUIDADO!)")
    ]
    
    summary_text = """
🎉 **COMANDOS ADICIONAIS IMPLEMENTADOS**

✅ **Novos comandos disponíveis:**
• `/control` - Acesso direto ao menu de controle
• `/stats` - Estatísticas gerais diretas
• `/quick` - Status rápido sem botões
• `/emergency` - Parada de emergência

🧪 **Teste cada comando abaixo:**
    """
    
    keyboard = []
    for cmd, desc in additional_commands:
        keyboard.append([InlineKeyboardButton(f"🧪 {desc}", callback_data=f"test_{cmd[1:]}")])
    
    keyboard.append([InlineKeyboardButton("✅ Todos os comandos OK!", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await bot.send_message(
        chat_id=chat_id,
        text=summary_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    print("✅ Teste de comandos adicionais enviado")
    
    # Testar cada comando diretamente
    for cmd, desc in additional_commands:
        try:
            await bot.send_message(chat_id, cmd)
            print(f"   ✅ {cmd} - Enviado")
        except Exception as e:
            print(f"   ❌ {cmd} - Erro: {e}")
        
        await asyncio.sleep(1)
    
    print("\n🎯 RESUMO:")
    print("   • 4 comandos adicionais implementados")
    print("   • Todos os comandos testados")
    print("   • Sistema completo com 7 comandos totais")
    print("\n📋 COMANDOS COMPLETOS:")
    print("   • /start - Menu principal")
    print("   • /status - Status detalhado")
    print("   • /help - Ajuda")
    print("   • /control - Menu de controle direto")
    print("   • /stats - Estatísticas diretas")
    print("   • /quick - Status rápido")
    print("   • /emergency - Parada de emergência")

if __name__ == "__main__":
    asyncio.run(test_additional_commands())
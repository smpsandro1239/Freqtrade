#!/usr/bin/env python3
"""
Teste automatizado de todas as funções do Telegram Commander
"""
import os
import asyncio
import time
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_all_functions():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados")
        return
    
    bot = Bot(token=token)
    
    print("🧪 INICIANDO TESTE COMPLETO DO TELEGRAM COMMANDER")
    print("=" * 60)
    
    # Lista de todos os callbacks para testar
    test_callbacks = [
        # Menus principais
        ("status_all", "📊 Status Geral"),
        ("control_menu", "🎮 Menu de Controle"),
        ("stats_menu", "📈 Menu de Estatísticas"),
        ("config_menu", "⚙️ Menu de Configurações"),
        ("help", "🆘 Ajuda"),
        ("main_menu", "🏠 Menu Principal"),
        
        # Controles de estratégias
        ("strategy_stratA", "🎮 Controle StratA"),
        ("strategy_stratB", "🎮 Controle StratB"),
        ("strategy_waveHyperNW", "🎮 Controle WaveHyperNW"),
        
        # Ações específicas
        ("logs_stratA", "📋 Logs StratA"),
        ("config_stratA", "⚙️ Config StratA"),
        ("stats_stratA", "📈 Stats StratA"),
        ("logs_waveHyperNW", "📋 Logs WaveHyperNW"),
        ("config_waveHyperNW", "⚙️ Config WaveHyperNW"),
        ("stats_waveHyperNW", "📈 Stats WaveHyperNW"),
        
        # Estatísticas
        ("stats_general", "📈 Estatísticas Gerais"),
    ]
    
    results = []
    
    for callback_data, description in test_callbacks:
        print(f"\n🔍 Testando: {description}")
        print(f"   Callback: {callback_data}")
        
        try:
            # Criar botão de teste
            keyboard = [[InlineKeyboardButton(f"🧪 TESTE: {description}", callback_data=callback_data)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Enviar mensagem de teste
            message = await bot.send_message(
                chat_id=chat_id,
                text=f"🧪 **TESTE AUTOMÁTICO**\n\n**Função**: {description}\n**Callback**: `{callback_data}`\n\n**Clique no botão abaixo para testar:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            print(f"   ✅ Mensagem enviada: ID {message.message_id}")
            results.append((callback_data, description, "✅ Enviado", message.message_id))
            
            # Aguardar um pouco entre testes
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            results.append((callback_data, description, f"❌ Erro: {e}", None))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    success_count = 0
    for callback, desc, status, msg_id in results:
        print(f"{status} {desc}")
        if "✅" in status:
            success_count += 1
    
    print(f"\n📈 RESULTADO: {success_count}/{len(results)} testes enviados com sucesso")
    print("\n🔍 AGORA TESTE MANUALMENTE:")
    print("1. Vá para o Telegram")
    print("2. Clique em cada botão de teste")
    print("3. Verifique se a função responde corretamente")
    print("4. Anote quais funções não funcionam")

if __name__ == "__main__":
    asyncio.run(test_all_functions())
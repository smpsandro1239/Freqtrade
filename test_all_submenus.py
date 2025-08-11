#!/usr/bin/env python3
"""
Teste completo de TODOS os submenus do Telegram Commander
Identifica exatamente quais submenus não estão funcionando
"""
import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def test_all_submenus():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Configuração não encontrada")
        return
    
    bot = Bot(token=token)
    
    print("🔍 TESTE COMPLETO DE TODOS OS SUBMENUS")
    print("=" * 60)
    
    # Lista COMPLETA de todos os callbacks possíveis
    all_callbacks = {
        "Menus Principais": [
            ("status_all", "📊 Status Geral"),
            ("control_menu", "🎮 Menu de Controle"),
            ("stats_menu", "📈 Menu de Estatísticas"),
            ("config_menu", "⚙️ Menu de Configurações"),
            ("help", "🆘 Menu de Ajuda"),
            ("main_menu", "🏠 Menu Principal")
        ],
        
        "Controle de Estratégias": [
            ("strategy_stratA", "🎮 Controle Strategy A"),
            ("strategy_stratB", "🎮 Controle Strategy B"),
            ("strategy_waveHyperNW", "🎮 Controle WaveHyperNW")
        ],
        
        "Ações de Controle": [
            ("action_start_stratA", "▶️ Iniciar Strategy A"),
            ("action_stop_stratA", "⏹️ Parar Strategy A"),
            ("action_restart_stratA", "🔄 Reiniciar Strategy A"),
            ("action_start_stratB", "▶️ Iniciar Strategy B"),
            ("action_stop_stratB", "⏹️ Parar Strategy B"),
            ("action_restart_stratB", "🔄 Reiniciar Strategy B"),
            ("action_start_waveHyperNW", "▶️ Iniciar WaveHyperNW"),
            ("action_stop_waveHyperNW", "⏹️ Parar WaveHyperNW"),
            ("action_restart_waveHyperNW", "🔄 Reiniciar WaveHyperNW")
        ],
        
        "Visualização de Logs": [
            ("logs_stratA", "📋 Logs Strategy A"),
            ("logs_stratB", "📋 Logs Strategy B"),
            ("logs_waveHyperNW", "📋 Logs WaveHyperNW")
        ],
        
        "Configurações": [
            ("config_stratA", "⚙️ Config Strategy A"),
            ("config_stratB", "⚙️ Config Strategy B"),
            ("config_waveHyperNW", "⚙️ Config WaveHyperNW")
        ],
        
        "Estatísticas": [
            ("stats_stratA", "📈 Stats Strategy A"),
            ("stats_stratB", "📈 Stats Strategy B"),
            ("stats_waveHyperNW", "📈 Stats WaveHyperNW"),
            ("stats_general", "📈 Estatísticas Gerais")
        ],
        
        "Toggle DRY/LIVE": [
            ("toggle_stratA", "🔄 Toggle Strategy A"),
            ("toggle_stratB", "🔄 Toggle Strategy B"),
            ("toggle_waveHyperNW", "🔄 Toggle WaveHyperNW")
        ],
        
        "Confirmações LIVE": [
            ("confirm_live_stratA", "✅ Confirmar LIVE Strategy A"),
            ("confirm_live_stratB", "✅ Confirmar LIVE Strategy B"),
            ("confirm_live_waveHyperNW", "✅ Confirmar LIVE WaveHyperNW")
        ],
        
        "Configuração de Stake": [
            ("stake_stratA", "💰 Stake Strategy A"),
            ("stake_stratB", "💰 Stake Strategy B"),
            ("stake_waveHyperNW", "💰 Stake WaveHyperNW")
        ],
        
        "Definir Stake Amount": [
            ("set_stake_stratA_10", "💰 Set Stake A = 10"),
            ("set_stake_stratA_20", "💰 Set Stake A = 20"),
            ("set_stake_stratA_50", "💰 Set Stake A = 50"),
            ("set_stake_waveHyperNW_10", "💰 Set Stake Wave = 10"),
            ("set_stake_waveHyperNW_20", "💰 Set Stake Wave = 20"),
            ("set_stake_waveHyperNW_50", "💰 Set Stake Wave = 50")
        ]
    }
    
    # Enviar resumo inicial
    summary_text = """
🔍 **TESTE COMPLETO DE SUBMENUS**

Vou testar TODOS os submenus do Telegram Commander para identificar quais não estão funcionando.

📋 **Categorias a testar:**
• Menus Principais (6 itens)
• Controle de Estratégias (3 itens)
• Ações de Controle (9 itens)
• Visualização de Logs (3 itens)
• Configurações (3 itens)
• Estatísticas (4 itens)
• Toggle DRY/LIVE (3 itens)
• Confirmações LIVE (3 itens)
• Configuração de Stake (3 itens)
• Definir Stake Amount (6 itens)

**Total: 42 submenus diferentes**

🧪 **Clique nos botões abaixo para testar:**
    """
    
    await bot.send_message(
        chat_id=chat_id,
        text=summary_text,
        parse_mode='Markdown'
    )
    
    # Testar cada categoria
    for category, callbacks in all_callbacks.items():
        print(f"\n🔍 TESTANDO CATEGORIA: {category}")
        print("-" * 50)
        
        # Criar mensagem para a categoria
        category_text = f"🧪 **TESTE: {category}**\n\n"
        category_text += f"Testando {len(callbacks)} submenus desta categoria:\n\n"
        
        keyboard = []
        for callback, description in callbacks:
            keyboard.append([InlineKeyboardButton(f"🧪 {description}", callback_data=callback)])
            print(f"   ✅ {callback} - {description}")
        
        # Adicionar botão de próxima categoria
        keyboard.append([InlineKeyboardButton("➡️ Próxima Categoria", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=category_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            print(f"   ✅ Categoria {category} enviada com sucesso")
            
        except Exception as e:
            print(f"   ❌ Erro ao enviar categoria {category}: {e}")
        
        # Aguardar entre categorias
        await asyncio.sleep(2)
    
    # Mensagem final
    final_text = """
🎯 **TESTE COMPLETO ENVIADO**

📋 **Instruções:**
1. Teste CADA botão enviado acima
2. Anote quais botões NÃO respondem
3. Anote quais botões dão erro
4. Anote quais botões funcionam corretamente

📊 **Relatório:**
• Se um botão não responder = Função não implementada
• Se um botão der erro = Problema na implementação
• Se um botão funcionar = OK

🔍 **Foque especialmente em:**
• Submenus de configuração
• Ações de controle específicas
• Configurações de stake
• Confirmações LIVE

**Reporte quais submenus específicos não funcionam!**
    """
    
    await bot.send_message(
        chat_id=chat_id,
        text=final_text,
        parse_mode='Markdown'
    )
    
    print("\n" + "=" * 60)
    print("🎯 TESTE COMPLETO ENVIADO PARA O TELEGRAM")
    print("=" * 60)
    print("\n📋 TOTAL DE SUBMENUS TESTADOS:")
    
    total_callbacks = 0
    for category, callbacks in all_callbacks.items():
        print(f"   • {category}: {len(callbacks)} submenus")
        total_callbacks += len(callbacks)
    
    print(f"\n🎯 TOTAL GERAL: {total_callbacks} submenus diferentes")
    print("\n🔍 AGORA TESTE MANUALMENTE:")
    print("1. Vá para o Telegram")
    print("2. Clique em CADA botão de teste")
    print("3. Anote quais NÃO funcionam")
    print("4. Reporte os problemas específicos")

if __name__ == "__main__":
    asyncio.run(test_all_submenus())
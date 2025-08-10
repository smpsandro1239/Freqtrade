#!/usr/bin/env python3
"""
Teste Abrangente do Telegram Commander
Testa todas as funções e identifica problemas
"""
import os
import asyncio
import time
import json
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

class TelegramTester:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        self.test_results = []
        
    async def initialize(self):
        """Inicializar bot e verificar conectividade"""
        if not self.token or not self.chat_id:
            print("❌ TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados")
            return False
            
        self.bot = Bot(token=self.token)
        
        try:
            # Testar conectividade básica
            me = await self.bot.get_me()
            print(f"✅ Bot conectado: @{me.username}")
            
            # Testar envio de mensagem
            test_msg = await self.bot.send_message(
                chat_id=self.chat_id,
                text="🧪 **TESTE DE CONECTIVIDADE**\n\nBot conectado e funcionando!",
                parse_mode='Markdown'
            )
            print(f"✅ Mensagem de teste enviada: ID {test_msg.message_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def add_result(self, category, function, status, details=""):
        """Adicionar resultado do teste"""
        self.test_results.append({
            'category': category,
            'function': function,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_basic_commands(self):
        """Testar comandos básicos"""
        print("\n🔍 TESTANDO COMANDOS BÁSICOS")
        print("-" * 40)
        
        basic_commands = [
            ("/start", "Menu Principal"),
            ("/status", "Status Geral"),
            ("/help", "Ajuda")
        ]
        
        for command, description in basic_commands:
            try:
                # Simular comando enviando mensagem com botão
                keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data="test_basic")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🧪 **TESTE COMANDO BÁSICO**\n\n**Comando**: `{command}`\n**Função**: {description}\n\n**Status**: Mensagem enviada com sucesso",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                print(f"   ✅ {command} - {description}")
                self.add_result("Comandos Básicos", command, "✅ Sucesso", f"Message ID: {message.message_id}")
                
            except Exception as e:
                print(f"   ❌ {command} - Erro: {e}")
                self.add_result("Comandos Básicos", command, "❌ Erro", str(e))
            
            await asyncio.sleep(0.5)
    
    async def test_menu_callbacks(self):
        """Testar callbacks dos menus"""
        print("\n🔍 TESTANDO CALLBACKS DOS MENUS")
        print("-" * 40)
        
        menu_callbacks = [
            ("status_all", "📊 Status Geral"),
            ("control_menu", "🎮 Menu de Controle"),
            ("stats_menu", "📈 Menu de Estatísticas"),
            ("config_menu", "⚙️ Menu de Configurações"),
            ("help", "🆘 Menu de Ajuda"),
            ("main_menu", "🏠 Menu Principal")
        ]
        
        for callback, description in menu_callbacks:
            try:
                keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data=callback)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🧪 **TESTE CALLBACK MENU**\n\n**Callback**: `{callback}`\n**Função**: {description}\n\n**Instruções**: Clique no botão para testar",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                print(f"   ✅ {callback} - {description}")
                self.add_result("Menu Callbacks", callback, "✅ Enviado", f"Message ID: {message.message_id}")
                
            except Exception as e:
                print(f"   ❌ {callback} - Erro: {e}")
                self.add_result("Menu Callbacks", callback, "❌ Erro", str(e))
            
            await asyncio.sleep(0.5)
    
    async def test_strategy_controls(self):
        """Testar controles de estratégias"""
        print("\n🔍 TESTANDO CONTROLES DE ESTRATÉGIAS")
        print("-" * 40)
        
        strategies = ["stratA", "stratB", "waveHyperNW"]
        actions = ["strategy", "logs", "config", "stats", "toggle"]
        
        for strategy in strategies:
            print(f"\n   📋 Testando estratégia: {strategy}")
            
            for action in actions:
                callback = f"{action}_{strategy}"
                description = f"{action.title()} - {strategy}"
                
                try:
                    keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data=callback)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    message = await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=f"🧪 **TESTE CONTROLE ESTRATÉGIA**\n\n**Estratégia**: {strategy}\n**Ação**: {action}\n**Callback**: `{callback}`\n\n**Instruções**: Clique no botão para testar",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                    print(f"      ✅ {callback}")
                    self.add_result("Controles Estratégia", callback, "✅ Enviado", f"Message ID: {message.message_id}")
                    
                except Exception as e:
                    print(f"      ❌ {callback} - Erro: {e}")
                    self.add_result("Controles Estratégia", callback, "❌ Erro", str(e))
                
                await asyncio.sleep(0.3)
    
    async def test_action_callbacks(self):
        """Testar callbacks de ações"""
        print("\n🔍 TESTANDO CALLBACKS DE AÇÕES")
        print("-" * 40)
        
        strategies = ["stratA", "stratB", "waveHyperNW"]
        actions = ["start", "stop", "restart"]
        
        for strategy in strategies:
            print(f"\n   🎮 Testando ações para: {strategy}")
            
            for action in actions:
                callback = f"action_{action}_{strategy}"
                description = f"{action.title()} {strategy}"
                
                try:
                    keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data=callback)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    message = await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=f"🧪 **TESTE AÇÃO ESTRATÉGIA**\n\n**Estratégia**: {strategy}\n**Ação**: {action}\n**Callback**: `{callback}`\n\n⚠️ **ATENÇÃO**: Este é um teste. A ação será simulada.",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                    print(f"      ✅ {callback}")
                    self.add_result("Ações Estratégia", callback, "✅ Enviado", f"Message ID: {message.message_id}")
                    
                except Exception as e:
                    print(f"      ❌ {callback} - Erro: {e}")
                    self.add_result("Ações Estratégia", callback, "❌ Erro", str(e))
                
                await asyncio.sleep(0.3)
    
    async def test_special_functions(self):
        """Testar funções especiais"""
        print("\n🔍 TESTANDO FUNÇÕES ESPECIAIS")
        print("-" * 40)
        
        special_callbacks = [
            ("stats_general", "📈 Estatísticas Gerais"),
            ("confirm_live_stratA", "⚠️ Confirmar LIVE StratA"),
            ("confirm_live_waveHyperNW", "⚠️ Confirmar LIVE WaveHyperNW"),
        ]
        
        for callback, description in special_callbacks:
            try:
                keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data=callback)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🧪 **TESTE FUNÇÃO ESPECIAL**\n\n**Callback**: `{callback}`\n**Função**: {description}\n\n⚠️ **ATENÇÃO**: Função crítica - teste com cuidado",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                print(f"   ✅ {callback} - {description}")
                self.add_result("Funções Especiais", callback, "✅ Enviado", f"Message ID: {message.message_id}")
                
            except Exception as e:
                print(f"   ❌ {callback} - Erro: {e}")
                self.add_result("Funções Especiais", callback, "❌ Erro", str(e))
            
            await asyncio.sleep(0.5)
    
    async def test_error_handling(self):
        """Testar tratamento de erros"""
        print("\n🔍 TESTANDO TRATAMENTO DE ERROS")
        print("-" * 40)
        
        error_callbacks = [
            ("invalid_callback", "Callback Inválido"),
            ("strategy_invalid", "Estratégia Inexistente"),
            ("action_invalid_stratA", "Ação Inválida"),
            ("", "Callback Vazio")
        ]
        
        for callback, description in error_callbacks:
            try:
                keyboard = [[InlineKeyboardButton(f"🧪 {description}", callback_data=callback)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🧪 **TESTE TRATAMENTO DE ERRO**\n\n**Callback**: `{callback}`\n**Teste**: {description}\n\n**Objetivo**: Verificar se o bot trata erros corretamente",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                print(f"   ✅ {callback} - {description}")
                self.add_result("Tratamento de Erros", callback, "✅ Enviado", f"Message ID: {message.message_id}")
                
            except Exception as e:
                print(f"   ❌ {callback} - Erro: {e}")
                self.add_result("Tratamento de Erros", callback, "❌ Erro", str(e))
            
            await asyncio.sleep(0.5)
    
    async def generate_report(self):
        """Gerar relatório final"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        # Estatísticas por categoria
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'success': 0, 'error': 0}
            
            categories[cat]['total'] += 1
            if '✅' in result['status']:
                categories[cat]['success'] += 1
            else:
                categories[cat]['error'] += 1
        
        # Mostrar estatísticas
        total_tests = len(self.test_results)
        total_success = sum(1 for r in self.test_results if '✅' in r['status'])
        total_errors = total_tests - total_success
        
        print(f"\n📈 RESUMO GERAL:")
        print(f"   Total de testes: {total_tests}")
        print(f"   Sucessos: {total_success} ({total_success/total_tests*100:.1f}%)")
        print(f"   Erros: {total_errors} ({total_errors/total_tests*100:.1f}%)")
        
        print(f"\n📋 POR CATEGORIA:")
        for cat, stats in categories.items():
            success_rate = stats['success'] / stats['total'] * 100
            print(f"   {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Salvar relatório detalhado
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'total_success': total_success,
                'total_errors': total_errors,
                'success_rate': total_success/total_tests*100
            },
            'categories': categories,
            'detailed_results': self.test_results
        }
        
        with open('telegram_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório detalhado salvo em: telegram_test_report.json")
        
        # Enviar resumo para o Telegram
        summary_text = f"""
🧪 **RELATÓRIO DE TESTES COMPLETO**

📊 **Resumo:**
• Total de testes: {total_tests}
• Sucessos: {total_success} ({total_success/total_tests*100:.1f}%)
• Erros: {total_errors} ({total_errors/total_tests*100:.1f}%)

📋 **Por categoria:**
"""
        
        for cat, stats in categories.items():
            success_rate = stats['success'] / stats['total'] * 100
            summary_text += f"• {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        summary_text += f"""
⏰ **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔍 **Próximos passos:**
1. Clique nos botões de teste enviados
2. Verifique quais funções não respondem
3. Anote os erros encontrados
4. Reporte problemas específicos
        """
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=summary_text,
            parse_mode='Markdown'
        )
    
    async def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 INICIANDO TESTE ABRANGENTE DO TELEGRAM COMMANDER")
        print("=" * 60)
        
        # Inicializar
        if not await self.initialize():
            return
        
        # Executar testes
        await self.test_basic_commands()
        await self.test_menu_callbacks()
        await self.test_strategy_controls()
        await self.test_action_callbacks()
        await self.test_special_functions()
        await self.test_error_handling()
        
        # Gerar relatório
        await self.generate_report()
        
        print("\n✅ TESTE COMPLETO FINALIZADO!")
        print("📱 Verifique seu Telegram para testar as funções manualmente")

async def main():
    """Função principal"""
    tester = TelegramTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
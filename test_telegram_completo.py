#!/usr/bin/env python3
"""
Teste Completo do Telegram - Verificar e Estabelecer Comunicação
"""
import os
import sys
import requests
import json
import time
from datetime import datetime

# Configurações do .env
TELEGRAM_TOKEN = "7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs"
TELEGRAM_CHAT_ID = "1555333079"

def test_bot_info():
    """Testar informações do bot"""
    print("🤖 TESTANDO INFORMAÇÕES DO BOT...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print(f"✅ Bot ativo: @{bot_info['username']}")
                print(f"   Nome: {bot_info['first_name']}")
                print(f"   ID: {bot_info['id']}")
                return True
            else:
                print(f"❌ Erro na API: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_send_message():
    """Testar envio de mensagem"""
    print("\n📱 TESTANDO ENVIO DE MENSAGEM...")
    
    message = f"""🎉 TESTE DE COMUNICAÇÃO TELEGRAM

✅ Bot funcionando corretamente!
🕐 Horário: {datetime.now().strftime('%H:%M:%S')}
📅 Data: {datetime.now().strftime('%d/%m/%Y')}

🚀 Sistema Freqtrade Commander ativo!

Comandos disponíveis:
/start - Menu principal
/status - Status das estratégias
/predict - Previsões de IA
/stats - Estatísticas
/help - Ajuda"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print("✅ Mensagem enviada com sucesso!")
                print(f"   Message ID: {data['result']['message_id']}")
                return True
            else:
                print(f"❌ Erro ao enviar: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def test_get_updates():
    """Testar recebimento de mensagens"""
    print("\n📥 TESTANDO RECEBIMENTO DE MENSAGENS...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                updates = data['result']
                print(f"✅ {len(updates)} mensagens encontradas")
                
                if updates:
                    last_update = updates[-1]
                    if 'message' in last_update:
                        msg = last_update['message']
                        print(f"   Última mensagem: '{msg.get('text', 'N/A')}'")
                        print(f"   De: {msg['from']['first_name']} (ID: {msg['from']['id']})")
                        print(f"   Chat ID: {msg['chat']['id']}")
                        
                        # Verificar se o chat ID está correto
                        if str(msg['chat']['id']) == TELEGRAM_CHAT_ID:
                            print("✅ Chat ID correto!")
                        else:
                            print(f"⚠️  Chat ID diferente! Configurado: {TELEGRAM_CHAT_ID}, Real: {msg['chat']['id']}")
                
                return True
            else:
                print(f"❌ Erro na API: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter updates: {e}")
        return False

def test_keyboard():
    """Testar teclado inline"""
    print("\n⌨️ TESTANDO TECLADO INLINE...")
    
    message = "🎮 TESTE DO MENU INTERATIVO\n\nEscolha uma opção:"
    
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '📊 Status', 'callback_data': 'status'},
                {'text': '📈 Stats', 'callback_data': 'stats'}
            ],
            [
                {'text': '🔮 Previsões', 'callback_data': 'predict'},
                {'text': '💰 Trading', 'callback_data': 'trading'}
            ],
            [
                {'text': '✅ Teste OK', 'callback_data': 'test_ok'}
            ]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': json.dumps(keyboard)
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print("✅ Menu interativo enviado!")
                print("   Clique nos botões para testar")
                return True
            else:
                print(f"❌ Erro ao enviar menu: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar menu: {e}")
        return False

def send_system_status():
    """Enviar status do sistema"""
    print("\n🏥 ENVIANDO STATUS DO SISTEMA...")
    
    message = f"""🏥 STATUS DO SISTEMA FREQTRADE

🕐 Verificação: {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}

🤖 Telegram Bot: ✅ Funcionando
📡 Comunicação: ✅ Estabelecida
⚙️ Sistema: 🔄 Inicializando

📋 Próximos passos:
1. Iniciar containers Docker
2. Configurar estratégias
3. Ativar monitoramento

💡 Para iniciar o sistema completo:
   Execute: docker compose up -d

🎯 Comandos disponíveis após inicialização:
/start - Menu principal
/status - Status das estratégias  
/predict - Previsões de IA
/stats - Estatísticas detalhadas
/help - Lista completa de comandos"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print("✅ Status do sistema enviado!")
                return True
            else:
                print(f"❌ Erro ao enviar status: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar status: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 TESTE COMPLETO DE COMUNICAÇÃO TELEGRAM")
    print("=" * 60)
    
    print(f"\n🔧 CONFIGURAÇÕES:")
    print(f"   Token: {TELEGRAM_TOKEN[:10]}...")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Executar testes
    tests_passed = 0
    total_tests = 5
    
    if test_bot_info():
        tests_passed += 1
    
    if test_send_message():
        tests_passed += 1
    
    if test_get_updates():
        tests_passed += 1
    
    if test_keyboard():
        tests_passed += 1
    
    if send_system_status():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📋 RESULTADO DOS TESTES:")
    print("=" * 60)
    
    print(f"✅ Testes passaram: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 COMUNICAÇÃO TELEGRAM 100% FUNCIONAL!")
        print("\n📱 VERIFIQUE SEU TELEGRAM:")
        print("   - Você deve ter recebido mensagens de teste")
        print("   - Deve haver um menu interativo")
        print("   - Status do sistema foi enviado")
        print("\n🚀 PRÓXIMO PASSO:")
        print("   Execute: docker compose up -d")
        print("   Depois teste: /start no Telegram")
    elif tests_passed >= 3:
        print("⚠️  COMUNICAÇÃO PARCIALMENTE FUNCIONAL")
        print("   Alguns testes falharam, mas o básico funciona")
    else:
        print("❌ PROBLEMAS NA COMUNICAÇÃO")
        print("   Verifique TOKEN e CHAT_ID")
    
    print("\n💡 COMANDOS PARA TESTAR NO TELEGRAM:")
    print("   /start - Menu principal")
    print("   /status - Status das estratégias")
    print("   /predict - Previsões de IA")
    print("   /help - Ajuda completa")

if __name__ == "__main__":
    main()
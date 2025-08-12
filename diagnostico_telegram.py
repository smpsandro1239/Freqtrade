#!/usr/bin/env python3
"""
Diagnóstico Completo do Telegram - Identificar e Resolver Problemas
"""
import os
import sys
import requests
import json
import time
from datetime import datetime

# Configurações
TELEGRAM_TOKEN = "7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs"
TELEGRAM_CHAT_ID = "1555333079"

def check_internet_connection():
    """Verificar conexão com internet"""
    print("🌐 VERIFICANDO CONEXÃO COM INTERNET...")
    
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✅ Conexão com internet OK")
            return True
        else:
            print(f"⚠️  Conexão instável - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sem conexão com internet: {e}")
        return False

def check_telegram_api():
    """Verificar acesso à API do Telegram"""
    print("\n📡 VERIFICANDO ACESSO À API DO TELEGRAM...")
    
    try:
        response = requests.get("https://api.telegram.org", timeout=10)
        if response.status_code == 200:
            print("✅ API do Telegram acessível")
            return True
        else:
            print(f"⚠️  API com problemas - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar API do Telegram: {e}")
        return False

def validate_token_format():
    """Validar formato do token"""
    print("\n🔑 VALIDANDO FORMATO DO TOKEN...")
    
    if not TELEGRAM_TOKEN:
        print("❌ Token vazio!")
        return False
    
    # Formato esperado: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    parts = TELEGRAM_TOKEN.split(':')
    
    if len(parts) != 2:
        print("❌ Formato do token inválido! Deve ser: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        return False
    
    bot_id, auth_token = parts
    
    if not bot_id.isdigit():
        print("❌ ID do bot deve ser numérico!")
        return False
    
    if len(auth_token) != 35:
        print(f"❌ Token de autenticação deve ter 35 caracteres! Atual: {len(auth_token)}")
        return False
    
    print(f"✅ Formato do token válido")
    print(f"   Bot ID: {bot_id}")
    print(f"   Token: {auth_token[:10]}...{auth_token[-5:]}")
    return True

def validate_chat_id():
    """Validar Chat ID"""
    print("\n👤 VALIDANDO CHAT ID...")
    
    if not TELEGRAM_CHAT_ID:
        print("❌ Chat ID vazio!")
        return False
    
    try:
        chat_id_int = int(TELEGRAM_CHAT_ID)
        print(f"✅ Chat ID válido: {chat_id_int}")
        return True
    except ValueError:
        print(f"❌ Chat ID deve ser numérico! Atual: {TELEGRAM_CHAT_ID}")
        return False

def test_bot_token():
    """Testar token do bot"""
    print("\n🤖 TESTANDO TOKEN DO BOT...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=15)
        
        print(f"   Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot = data['result']
                print(f"✅ Token válido!")
                print(f"   Nome: {bot['first_name']}")
                print(f"   Username: @{bot['username']}")
                print(f"   ID: {bot['id']}")
                print(f"   Pode receber mensagens: {bot.get('can_read_all_group_messages', 'N/A')}")
                return True, bot
            else:
                print(f"❌ Token inválido: {data.get('description', 'Erro desconhecido')}")
                return False, None
        elif response.status_code == 401:
            print("❌ Token não autorizado! Verifique se o token está correto.")
            return False, None
        elif response.status_code == 404:
            print("❌ Bot não encontrado! Token pode estar incorreto.")
            return False, None
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na conexão com Telegram")
        return False, None
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão com Telegram")
        return False, None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False, None

def test_chat_access():
    """Testar acesso ao chat"""
    print("\n💬 TESTANDO ACESSO AO CHAT...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
    
    params = {
        'chat_id': TELEGRAM_CHAT_ID
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                chat = data['result']
                print(f"✅ Chat acessível!")
                print(f"   Tipo: {chat['type']}")
                print(f"   ID: {chat['id']}")
                if 'first_name' in chat:
                    print(f"   Nome: {chat['first_name']} {chat.get('last_name', '')}")
                if 'username' in chat:
                    print(f"   Username: @{chat['username']}")
                return True
            else:
                error_desc = data.get('description', 'Erro desconhecido')
                print(f"❌ Erro ao acessar chat: {error_desc}")
                
                if 'chat not found' in error_desc.lower():
                    print("💡 SOLUÇÃO: Chat ID incorreto ou bot não foi iniciado pelo usuário")
                    print("   1. Abra o Telegram")
                    print("   2. Procure pelo seu bot")
                    print("   3. Digite /start")
                    print("   4. Execute este diagnóstico novamente")
                
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar chat: {e}")
        return False

def send_diagnostic_message():
    """Enviar mensagem de diagnóstico"""
    print("\n📤 ENVIANDO MENSAGEM DE DIAGNÓSTICO...")
    
    message = f"""🔧 DIAGNÓSTICO DO SISTEMA

✅ Comunicação estabelecida com sucesso!

🕐 Teste realizado: {datetime.now().strftime('%H:%M:%S')}
📅 Data: {datetime.now().strftime('%d/%m/%Y')}

🤖 Bot: Funcionando
💬 Chat: Acessível
📡 API: Conectada

🎯 Próximos passos:
1. Iniciar sistema: docker compose up -d
2. Testar comandos: /start, /status, /predict

🚀 Sistema Freqtrade Commander pronto!"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, data=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print("✅ Mensagem de diagnóstico enviada!")
                print("   Verifique seu Telegram")
                return True
            else:
                print(f"❌ Erro ao enviar: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def get_recent_messages():
    """Obter mensagens recentes"""
    print("\n📥 VERIFICANDO MENSAGENS RECENTES...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    params = {
        'limit': 5,
        'offset': -5
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                updates = data['result']
                print(f"✅ {len(updates)} mensagens recentes encontradas")
                
                for update in updates[-3:]:  # Últimas 3
                    if 'message' in update:
                        msg = update['message']
                        text = msg.get('text', 'N/A')[:50]
                        from_user = msg['from']['first_name']
                        date = datetime.fromtimestamp(msg['date']).strftime('%H:%M:%S')
                        print(f"   {date} - {from_user}: {text}")
                
                return True
            else:
                print(f"❌ Erro: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter mensagens: {e}")
        return False

def main():
    """Função principal de diagnóstico"""
    print("=" * 70)
    print("🔧 DIAGNÓSTICO COMPLETO DO TELEGRAM")
    print("=" * 70)
    
    print(f"\n📋 CONFIGURAÇÕES ATUAIS:")
    print(f"   Token: {TELEGRAM_TOKEN[:15]}...{TELEGRAM_TOKEN[-10:]}")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Executar diagnósticos
    tests = []
    
    tests.append(("Conexão Internet", check_internet_connection()))
    tests.append(("API Telegram", check_telegram_api()))
    tests.append(("Formato Token", validate_token_format()))
    tests.append(("Chat ID", validate_chat_id()))
    
    bot_valid, bot_info = test_bot_token()
    tests.append(("Token Bot", bot_valid))
    
    tests.append(("Acesso Chat", test_chat_access()))
    tests.append(("Envio Mensagem", send_diagnostic_message()))
    tests.append(("Mensagens Recentes", get_recent_messages()))
    
    # Resultado final
    print("\n" + "=" * 70)
    print("📊 RESULTADO DO DIAGNÓSTICO:")
    print("=" * 70)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TELEGRAM 100% FUNCIONAL!")
        print("\n📱 VERIFIQUE SEU TELEGRAM:")
        print("   - Você deve ter recebido uma mensagem de diagnóstico")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute: iniciar_sistema_telegram.bat")
        print("   2. Ou: docker compose up -d")
        print("   3. Teste: /start no Telegram")
        
    elif passed >= 6:
        print("\n⚠️  TELEGRAM FUNCIONANDO COM PEQUENOS PROBLEMAS")
        print("   A comunicação básica funciona")
        
    else:
        print("\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS")
        print("\n🔧 SOLUÇÕES POSSÍVEIS:")
        
        if not tests[0][1]:  # Internet
            print("   1. Verifique sua conexão com internet")
            
        if not tests[2][1] or not tests[4][1]:  # Token
            print("   2. Verifique o TELEGRAM_TOKEN no arquivo .env")
            print("      - Obtenha novo token do @BotFather")
            
        if not tests[3][1] or not tests[5][1]:  # Chat
            print("   3. Verifique o TELEGRAM_CHAT_ID no arquivo .env")
            print("      - Envie /start para o bot")
            print("      - Acesse: https://api.telegram.org/bot<TOKEN>/getUpdates")
            print("      - Copie o chat_id da resposta")
    
    print(f"\n💡 COMANDOS PARA TESTAR APÓS CORREÇÃO:")
    print("   python test_telegram_completo.py")
    print("   iniciar_sistema_telegram.bat")

if __name__ == "__main__":
    main()
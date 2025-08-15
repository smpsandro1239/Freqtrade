#!/usr/bin/env python3
"""
🧪 Teste Seguro de Credenciais - FreqTrade Multi-Strategy
Testa credenciais sem expor dados sensíveis
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class CredentialTester:
    """Testador seguro de credenciais"""
    
    def __init__(self):
        self.results = {}
        
    def test_env_file(self):
        """Testa se arquivo .env existe e tem as variáveis necessárias"""
        print("🔍 1. TESTANDO ARQUIVO .ENV")
        print("-" * 30)
        
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ Arquivo .env não encontrado!")
            return False
            
        required_vars = [
            'EXCHANGE_KEY', 'EXCHANGE_SECRET', 'EXCHANGE_NAME',
            'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID',
            'DASHBOARD_SECRET_KEY', 'DASHBOARD_USERNAME', 'DASHBOARD_PASSWORD'
        ]
        
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif value in ['YOUR_EXCHANGE_API_KEY_HERE', 'YOUR_EXCHANGE_SECRET_KEY_HERE', 
                          'YOUR_TELEGRAM_BOT_TOKEN_HERE', 'YOUR_TELEGRAM_CHAT_ID_HERE',
                          'GENERATE_A_VERY_SECURE_SECRET_KEY_HERE', 'CHANGE_THIS_SECURE_PASSWORD']:
                placeholder_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variáveis faltando: {', '.join(missing_vars)}")
            return False
            
        if placeholder_vars:
            print(f"⚠️  Variáveis não configuradas: {', '.join(placeholder_vars)}")
            print("   Execute: python setup_credentials.py")
            return False
            
        print("✅ Arquivo .env configurado corretamente")
        return True
    
    def test_exchange_format(self):
        """Testa formato das credenciais da exchange"""
        print("\n💱 2. TESTANDO FORMATO DAS CREDENCIAIS DA EXCHANGE")
        print("-" * 50)
        
        exchange_key = os.getenv('EXCHANGE_KEY')
        exchange_secret = os.getenv('EXCHANGE_SECRET')
        exchange_name = os.getenv('EXCHANGE_NAME')
        
        if not all([exchange_key, exchange_secret, exchange_name]):
            print("❌ Credenciais da exchange incompletas")
            return False
            
        # Validações básicas de formato
        if len(exchange_key) < 20:
            print("❌ API Key muito curta (deve ter pelo menos 20 caracteres)")
            return False
            
        if len(exchange_secret) < 20:
            print("❌ Secret Key muito curta (deve ter pelo menos 20 caracteres)")
            return False
            
        if exchange_name not in ['binance', 'coinbase', 'kraken', 'bybit']:
            print(f"⚠️  Exchange '{exchange_name}' pode não ser suportada")
            
        print(f"✅ Formato das credenciais da {exchange_name.upper()} OK")
        print(f"   API Key: {exchange_key[:8]}...{exchange_key[-4:]}")
        print(f"   Secret: {exchange_secret[:8]}...{exchange_secret[-4:]}")
        return True
    
    def test_telegram_format(self):
        """Testa formato das credenciais do Telegram"""
        print("\n🤖 3. TESTANDO FORMATO DAS CREDENCIAIS DO TELEGRAM")
        print("-" * 50)
        
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not all([token, chat_id]):
            print("❌ Credenciais do Telegram incompletas")
            return False
            
        # Validar formato do token
        if ':' not in token or len(token) < 40:
            print("❌ Token do Telegram inválido")
            print("   Formato correto: 123456789:ABC-DEF...")
            return False
            
        # Validar Chat ID
        try:
            int(chat_id)
        except ValueError:
            print("❌ Chat ID deve ser um número")
            return False
            
        print("✅ Formato das credenciais do Telegram OK")
        print(f"   Bot ID: {token.split(':')[0]}")
        print(f"   Chat ID: {chat_id}")
        return True
    
    async def test_telegram_connection(self):
        """Testa conexão com o Telegram"""
        print("\n📡 4. TESTANDO CONEXÃO COM TELEGRAM")
        print("-" * 40)
        
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("❌ Token do Telegram não configurado")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            bot_info = data.get('result', {})
                            print("✅ Conexão com Telegram OK")
                            print(f"   Bot: @{bot_info.get('username', 'N/A')}")
                            print(f"   Nome: {bot_info.get('first_name', 'N/A')}")
                            return True
                        else:
                            print("❌ Token do Telegram inválido")
                            return False
                    else:
                        print(f"❌ Erro HTTP {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            print("❌ Timeout na conexão com Telegram")
            return False
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def test_dashboard_config(self):
        """Testa configuração do dashboard"""
        print("\n🌐 5. TESTANDO CONFIGURAÇÃO DO DASHBOARD")
        print("-" * 40)
        
        secret_key = os.getenv('DASHBOARD_SECRET_KEY')
        username = os.getenv('DASHBOARD_USERNAME')
        password = os.getenv('DASHBOARD_PASSWORD')
        
        if not all([secret_key, username, password]):
            print("❌ Configuração do dashboard incompleta")
            return False
            
        if len(secret_key) < 32:
            print("❌ Chave secreta muito fraca (deve ter pelo menos 32 caracteres)")
            return False
            
        if len(password) < 8:
            print("❌ Password muito fraca (deve ter pelo menos 8 caracteres)")
            return False
            
        print("✅ Configuração do dashboard OK")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password)}")
        print(f"   Secret Key: {secret_key[:16]}...{secret_key[-8:]}")
        return True
    
    def test_security_settings(self):
        """Testa configurações de segurança"""
        print("\n🔒 6. TESTANDO CONFIGURAÇÕES DE SEGURANÇA")
        print("-" * 40)
        
        dry_run = os.getenv('DEFAULT_DRY_RUN', 'true').lower()
        max_loss = os.getenv('MAX_DAILY_LOSS_PERCENT', '5.0')
        emergency_stop = os.getenv('EMERGENCY_STOP_ENABLED', 'true').lower()
        
        if dry_run != 'true':
            print("⚠️  ATENÇÃO: DEFAULT_DRY_RUN não está ativado!")
            print("   Recomendado manter 'true' para testes iniciais")
        else:
            print("✅ Modo dry-run ativado (seguro para testes)")
            
        try:
            max_loss_float = float(max_loss)
            if max_loss_float > 10.0:
                print(f"⚠️  ATENÇÃO: Limite de perda diária muito alto ({max_loss}%)")
            else:
                print(f"✅ Limite de perda diária: {max_loss}%")
        except ValueError:
            print("❌ MAX_DAILY_LOSS_PERCENT deve ser um número")
            return False
            
        if emergency_stop == 'true':
            print("✅ Parada de emergência ativada")
        else:
            print("⚠️  Parada de emergência desativada")
            
        return True
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 TESTE COMPLETO DE CREDENCIAIS")
        print("=" * 50)
        print()
        
        tests = [
            self.test_env_file(),
            self.test_exchange_format(),
            self.test_telegram_format(),
            await self.test_telegram_connection(),
            self.test_dashboard_config(),
            self.test_security_settings()
        ]
        
        passed = sum(tests)
        total = len(tests)
        
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema pronto para inicialização")
            print()
            print("🚀 PRÓXIMOS PASSOS:")
            print("   1. Execute: .\\run.ps1 setup")
            print("   2. Ou execute: docker-compose up -d")
            return True
        else:
            print(f"❌ {total - passed} teste(s) falharam de {total}")
            print("🔧 Corrija os problemas antes de continuar")
            return False

async def main():
    """Função principal"""
    try:
        tester = CredentialTester()
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
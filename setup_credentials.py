#!/usr/bin/env python3
"""
🔒 Setup Seguro de Credenciais - FreqTrade Multi-Strategy
Configura credenciais de forma segura sem expor dados sensíveis
"""

import os
import secrets
import string
import getpass
from pathlib import Path

def generate_secure_key(length=64):
    """Gera uma chave segura aleatória"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_secure_input(prompt, is_password=False):
    """Obtém input seguro do usuário"""
    if is_password:
        return getpass.getpass(prompt)
    return input(prompt).strip()

def validate_telegram_token(token):
    """Valida formato do token do Telegram"""
    if not token or len(token) < 40:
        return False
    if ':' not in token:
        return False
    parts = token.split(':')
    if len(parts) != 2:
        return False
    try:
        int(parts[0])  # Bot ID deve ser numérico
        return len(parts[1]) >= 35  # Token deve ter pelo menos 35 chars
    except ValueError:
        return False

def validate_chat_id(chat_id):
    """Valida formato do Chat ID"""
    try:
        int(chat_id)
        return True
    except ValueError:
        return False

def setup_credentials():
    """Configura credenciais de forma segura"""
    print("🔒 SETUP SEGURO DE CREDENCIAIS - FreqTrade Multi-Strategy")
    print("=" * 60)
    print()
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Ler template atual
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📋 Vamos configurar suas credenciais passo a passo:")
    print()
    
    # 1. Exchange Configuration
    print("💱 1. CONFIGURAÇÃO DA EXCHANGE")
    print("-" * 30)
    
    exchange_name = input("Exchange (binance/coinbase/kraken) [binance]: ").strip() or "binance"
    
    print(f"\n📝 Para obter suas chaves API da {exchange_name.upper()}:")
    print(f"   1. Acesse sua conta na {exchange_name}")
    print("   2. Vá em 'API Management' ou 'API Keys'")
    print("   3. Crie uma nova API Key com permissões de trading")
    print("   4. ⚠️  IMPORTANTE: Habilite apenas 'Spot Trading' (não Futures)")
    print()
    
    exchange_key = get_secure_input("API Key da Exchange: ")
    exchange_secret = get_secure_input("Secret Key da Exchange: ", is_password=True)
    
    if not exchange_key or not exchange_secret:
        print("❌ Chaves da exchange são obrigatórias!")
        return False
    
    # 2. Telegram Configuration
    print("\n🤖 2. CONFIGURAÇÃO DO TELEGRAM")
    print("-" * 30)
    
    print("📝 Para configurar o bot do Telegram:")
    print("   1. Abra o Telegram e procure por @BotFather")
    print("   2. Envie /newbot e siga as instruções")
    print("   3. Copie o token fornecido")
    print("   4. Para obter seu Chat ID, envie /start para @userinfobot")
    print()
    
    telegram_token = get_secure_input("Token do Bot Telegram: ")
    
    if not validate_telegram_token(telegram_token):
        print("❌ Token do Telegram inválido! Formato: 123456789:ABC-DEF...")
        return False
    
    telegram_chat_id = get_secure_input("Seu Chat ID do Telegram: ")
    
    if not validate_chat_id(telegram_chat_id):
        print("❌ Chat ID inválido! Deve ser um número.")
        return False
    
    # 3. Dashboard Configuration
    print("\n🌐 3. CONFIGURAÇÃO DO DASHBOARD WEB")
    print("-" * 30)
    
    dashboard_username = input("Username do Dashboard [admin]: ").strip() or "admin"
    dashboard_password = get_secure_input("Password do Dashboard: ", is_password=True)
    
    if not dashboard_password or len(dashboard_password) < 8:
        print("❌ Password deve ter pelo menos 8 caracteres!")
        return False
    
    # Gerar chave secreta segura
    dashboard_secret = generate_secure_key(64)
    
    # 4. Aplicar configurações
    print("\n🔧 4. APLICANDO CONFIGURAÇÕES")
    print("-" * 30)
    
    # Substituir valores no arquivo .env
    replacements = {
        'YOUR_EXCHANGE_API_KEY_HERE': exchange_key,
        'YOUR_EXCHANGE_SECRET_KEY_HERE': exchange_secret,
        'binance': exchange_name,
        'YOUR_TELEGRAM_BOT_TOKEN_HERE': telegram_token,
        'YOUR_TELEGRAM_CHAT_ID_HERE': telegram_chat_id,
        'admin': dashboard_username,
        'CHANGE_THIS_SECURE_PASSWORD': dashboard_password,
        'GENERATE_A_VERY_SECURE_SECRET_KEY_HERE': dashboard_secret
    }
    
    for old_value, new_value in replacements.items():
        content = content.replace(old_value, new_value)
    
    # Salvar arquivo .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Credenciais configuradas com sucesso!")
    print()
    print("🔒 IMPORTANTE - SEGURANÇA:")
    print("   ✅ Arquivo .env foi atualizado")
    print("   ✅ Credenciais NÃO serão commitadas (protegido pelo .gitignore)")
    print("   ✅ Chave secreta do dashboard foi gerada automaticamente")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("   1. Execute: python test_credentials.py")
    print("   2. Se tudo estiver OK, execute: .\\run.ps1 setup")
    print()
    
    return True

def main():
    """Função principal"""
    try:
        if setup_credentials():
            print("🎉 Setup concluído com sucesso!")
        else:
            print("❌ Setup falhou. Tente novamente.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")

if __name__ == "__main__":
    main()
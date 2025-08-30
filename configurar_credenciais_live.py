#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR DE CREDENCIAIS PARA MODO LIVE
Script simplificado para configurar credenciais reais
"""

import os
import getpass
from pathlib import Path

def configurar_credenciais():
    """Configura credenciais para modo live"""
    print("CONFIGURAÇÃO DE CREDENCIAIS PARA MODO LIVE")
    print("="*50)
    print()
    print("ATENÇÃO: Configure apenas credenciais REAIS para trading LIVE")
    print()
    
    # Ler arquivo .env atual
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    print("1. TELEGRAM BOT (Para controle remoto)")
    print("   - Acesse @BotFather no Telegram")
    print("   - Crie um novo bot com /newbot")
    print("   - Copie o token fornecido")
    print()
    
    telegram_token = input("Token do Telegram Bot: ").strip()
    if telegram_token:
        content = update_env_value(content, 'TELEGRAM_TOKEN', telegram_token)
        print("✅ Token do Telegram configurado")
    
    print("\n2. TELEGRAM CHAT ID (Seu ID pessoal)")
    print("   - Acesse @userinfobot no Telegram")
    print("   - Envie /start")
    print("   - Copie o ID fornecido")
    print()
    
    chat_id = input("Seu Chat ID do Telegram: ").strip()
    if chat_id:
        content = update_env_value(content, 'TELEGRAM_CHAT_ID', chat_id)
        print("✅ Chat ID configurado")
    
    print("\n3. BINANCE API (Para trading real)")
    print("   - Acesse sua conta Binance")
    print("   - Vá em API Management")
    print("   - Crie uma nova API Key")
    print("   - IMPORTANTE: Habilite apenas 'Spot Trading'")
    print()
    
    api_key = input("Binance API Key: ").strip()
    if api_key:
        content = update_env_value(content, 'EXCHANGE_KEY', api_key)
        print("✅ API Key configurada")
    
    api_secret = getpass.getpass("Binance API Secret (oculto): ").strip()
    if api_secret:
        content = update_env_value(content, 'EXCHANGE_SECRET', api_secret)
        print("✅ API Secret configurada")
    
    # Configurações de segurança
    print("\n4. CONFIGURAÇÕES DE SEGURANÇA")
    print()
    
    max_trades = input("Máximo de trades simultâneos (recomendado: 3): ").strip() or "3"
    content = update_env_value(content, 'MAX_OPEN_TRADES', max_trades)
    
    stake_amount = input("Valor por trade em USDT (recomendado: 50): ").strip() or "50"
    content = update_env_value(content, 'STAKE_AMOUNT', stake_amount)
    
    # Manter DRY_RUN como true por segurança
    content = update_env_value(content, 'DRY_RUN', 'true')
    
    # Configurações do dashboard
    dashboard_user = input("Usuário do dashboard (padrão: admin): ").strip() or "admin"
    content = update_env_value(content, 'DASHBOARD_USERNAME', dashboard_user)
    
    dashboard_pass = getpass.getpass("Senha do dashboard (oculta): ").strip()
    if not dashboard_pass:
        dashboard_pass = "admin123"
    content = update_env_value(content, 'DASHBOARD_PASSWORD', dashboard_pass)
    
    # Salvar arquivo
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*50)
    print("✅ CREDENCIAIS CONFIGURADAS COM SUCESSO!")
    print()
    print("PRÓXIMOS PASSOS:")
    print("1. Teste o sistema: python launcher_simples.py")
    print("2. Acesse o dashboard: http://localhost:5000")
    print("3. Teste o bot do Telegram")
    print("4. Quando estiver pronto: python converter_para_live.py")
    print()
    print("⚠️ IMPORTANTE:")
    print("• Sistema ainda está em DRY-RUN (seguro)")
    print("• Para modo LIVE, use o conversor")
    print("• Monitore sempre os trades")

def update_env_value(content, key, value):
    """Atualiza valor no conteúdo do .env"""
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}'
            updated = True
            break
    
    if not updated:
        lines.append(f'{key}={value}')
    
    return '\n'.join(lines)

def main():
    """Função principal"""
    try:
        configurar_credenciais()
    except KeyboardInterrupt:
        print("\n\nConfiguração cancelada pelo usuário.")
    except Exception as e:
        print(f"\nErro durante configuração: {e}")

if __name__ == "__main__":
    main()
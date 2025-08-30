#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STATUS FINAL DO SISTEMA
Mostra o estado atual de todos os componentes
"""

import os
import json
import requests
import subprocess
from pathlib import Path

def check_docker_containers():
    """Verifica containers Docker"""
    print("CONTAINERS DOCKER")
    print("-" * 30)
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            ft_containers = [line for line in lines if 'ft-' in line]
            
            print(f"Containers FreqTrade ativos: {len(ft_containers)}")
            for container in ft_containers:
                print(f"  ✅ {container}")
            
            return len(ft_containers)
        else:
            print("❌ Erro ao verificar containers")
            return 0
            
    except Exception as e:
        print(f"❌ Docker não disponível: {e}")
        return 0

def check_apis():
    """Verifica APIs das estratégias"""
    print("\nAPIS DAS ESTRATÉGIAS")
    print("-" * 30)
    
    apis = [
        (8081, "Strategy A"),
        (8082, "Strategy B"),
        (8083, "WaveHyperNW"),
        (8084, "ML Strategy"),
        (8085, "ML Simple"),
        (8086, "Multi Timeframe"),
        (8087, "Wave Enhanced")
    ]
    
    working = 0
    
    for port, name in apis:
        try:
            response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=3)
            if response.status_code == 200:
                print(f"  ✅ {name} (:{port})")
                working += 1
            else:
                print(f"  ❌ {name} (:{port}) - Status {response.status_code}")
        except:
            print(f"  ❌ {name} (:{port}) - Não responde")
    
    print(f"\nAPIs funcionando: {working}/{len(apis)}")
    return working

def check_configurations():
    """Verifica configurações"""
    print("\nCONFIGURAÇÕES")
    print("-" * 30)
    
    configs = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/multiTimeframe.json',
        'user_data/configs/waveHyperNWEnhanced.json'
    ]
    
    dry_run_count = 0
    live_count = 0
    
    for config_file in configs:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if config.get('dry_run', True):
                    print(f"  🟡 {Path(config_file).name}: DRY-RUN")
                    dry_run_count += 1
                else:
                    print(f"  🔴 {Path(config_file).name}: LIVE")
                    live_count += 1
                    
            except Exception as e:
                print(f"  ❌ {Path(config_file).name}: Erro - {e}")
        else:
            print(f"  ❌ {Path(config_file).name}: Não encontrado")
    
    print(f"\nDRY-RUN: {dry_run_count} | LIVE: {live_count}")
    return dry_run_count, live_count

def check_credentials():
    """Verifica credenciais"""
    print("\nCREDENCIAIS")
    print("-" * 30)
    
    env_file = Path('.env')
    if not env_file.exists():
        print("  ❌ Arquivo .env não encontrado")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar credenciais
        checks = [
            ('TELEGRAM_TOKEN', 'Token do Telegram'),
            ('TELEGRAM_CHAT_ID', 'Chat ID do Telegram'),
            ('EXCHANGE_KEY', 'API Key da Binance'),
            ('EXCHANGE_SECRET', 'Secret da Binance'),
            ('DASHBOARD_USERNAME', 'Usuário do Dashboard'),
            ('DASHBOARD_PASSWORD', 'Senha do Dashboard')
        ]
        
        configured = 0
        
        for key, desc in checks:
            if f'{key}=' in content:
                line = [l for l in content.split('\n') if l.startswith(f'{key}=')][0]
                value = line.split('=', 1)[1]
                
                if value and 'YOUR_' not in value and 'your-' not in value:
                    print(f"  ✅ {desc}")
                    configured += 1
                else:
                    print(f"  ⚠️ {desc}: Placeholder")
            else:
                print(f"  ❌ {desc}: Não configurado")
        
        print(f"\nCredenciais configuradas: {configured}/{len(checks)}")
        return configured == len(checks)
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar credenciais: {e}")
        return False

def check_dashboard():
    """Verifica dashboard"""
    print("\nDASHBOARD WEB")
    print("-" * 30)
    
    try:
        response = requests.get('http://127.0.0.1:5000', timeout=3)
        if response.status_code in [200, 302]:  # 302 = redirect para login
            print("  ✅ Dashboard acessível em http://localhost:5000")
            return True
        else:
            print(f"  ❌ Dashboard retornou status {response.status_code}")
            return False
    except:
        print("  ⚠️ Dashboard não está rodando")
        print("     Execute: python launcher_simples.py -> opção 1")
        return False

def show_next_steps(containers, apis, creds_ok, dry_run, live):
    """Mostra próximos passos baseado no status"""
    print("\nPRÓXIMOS PASSOS")
    print("=" * 50)
    
    if containers < 7:
        print("1. ❌ Iniciar containers Docker:")
        print("   docker-compose -f docker-compose-simple.yml up -d")
        return
    
    if apis < 7:
        print("1. ⚠️ Algumas APIs não respondem:")
        print("   docker-compose -f docker-compose-simple.yml restart")
        return
    
    if not creds_ok:
        print("1. 🔧 Configurar credenciais:")
        print("   python configurar_credenciais_live.py")
        print()
    
    print("2. 📊 Testar dashboard:")
    print("   python launcher_simples.py -> opção 1")
    print("   Acesse: http://localhost:5000")
    print()
    
    if creds_ok:
        print("3. 🤖 Testar Telegram:")
        print("   Envie /start para seu bot")
        print()
    
    if dry_run > 0 and creds_ok:
        print("4. 🔴 Para modo LIVE (CUIDADO!):")
        print("   python converter_para_live.py")
        print()
    
    if live > 0:
        print("⚠️ SISTEMA EM MODO LIVE!")
        print("   Monitore constantemente!")
        print("   Dashboard: http://localhost:5000")

def main():
    """Função principal"""
    print("STATUS FINAL DO SISTEMA FREQTRADE")
    print("=" * 50)
    
    # Verificações
    containers = check_docker_containers()
    apis = check_apis()
    dry_run, live = check_configurations()
    creds_ok = check_credentials()
    dashboard_ok = check_dashboard()
    
    # Resumo
    print("\nRESUMO GERAL")
    print("=" * 50)
    
    status_items = [
        (containers >= 7, f"Containers Docker: {containers}/7"),
        (apis >= 7, f"APIs funcionando: {apis}/7"),
        (creds_ok, "Credenciais configuradas"),
        (dashboard_ok, "Dashboard acessível"),
        (dry_run > 0, f"Modo seguro (DRY-RUN): {dry_run} configs")
    ]
    
    for status, desc in status_items:
        icon = "✅" if status else "❌"
        print(f"  {icon} {desc}")
    
    # Determinar status geral
    all_good = containers >= 7 and apis >= 7
    
    if all_good and creds_ok:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
    elif all_good:
        print("\n⚠️ Sistema funcional - Configure credenciais para funcionalidade completa")
    else:
        print("\n❌ Sistema com problemas - Veja próximos passos")
    
    # Próximos passos
    show_next_steps(containers, apis, creds_ok, dry_run, live)

if __name__ == "__main__":
    main()
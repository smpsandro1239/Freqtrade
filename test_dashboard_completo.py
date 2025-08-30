#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do dashboard integrado
"""

import os
import sys
import time
import requests
import threading
from pathlib import Path

def start_dashboard():
    """Inicia o dashboard em thread separada"""
    try:
        # Configurar variáveis de ambiente
        os.environ['DASHBOARD_USERNAME'] = 'sandro'
        os.environ['DASHBOARD_PASSWORD'] = 'sandro2020'
        os.environ['DASHBOARD_SECRET_KEY'] = 'Benfica456!!!'
        
        # Importar e iniciar dashboard
        sys.path.append('scripts')
        from dashboard_main import app
        
        print("🌐 Iniciando dashboard em http://localhost:5000")
        print("👤 Login: sandro")
        print("🔑 Senha: sandro2020")
        
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def test_dashboard_endpoints():
    """Testa endpoints do dashboard"""
    print("\n🔍 TESTANDO ENDPOINTS DO DASHBOARD")
    print("=" * 50)
    
    # Aguardar dashboard inicializar
    print("⏳ Aguardando dashboard inicializar...")
    time.sleep(5)
    
    base_url = "http://localhost:5000"
    
    # Teste 1: Página inicial (deve redirecionar para login)
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ Página inicial: {response.status_code}")
        if response.status_code == 302:
            print("   (Redirecionamento para login - OK)")
    except Exception as e:
        print(f"❌ Página inicial: {e}")
        return False
    
    # Teste 2: Página de login
    try:
        response = requests.get(f"{base_url}/login", timeout=10)
        print(f"✅ Página de login: {response.status_code}")
    except Exception as e:
        print(f"❌ Página de login: {e}")
        return False
    
    # Teste 3: Login com credenciais
    try:
        session = requests.Session()
        
        # Fazer login
        login_data = {
            'username': 'sandro',
            'password': 'sandro2020'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, timeout=10)
        print(f"✅ Login: {response.status_code}")
        
        if response.status_code == 302:  # Redirecionamento após login
            # Testar página principal após login
            response = session.get(base_url, timeout=10)
            print(f"✅ Dashboard principal: {response.status_code}")
            
            # Testar API de status
            response = session.get(f"{base_url}/api/strategies/status", timeout=10)
            print(f"✅ API Status: {response.status_code}")
            
            # Testar API de resumo
            response = session.get(f"{base_url}/api/summary", timeout=10)
            print(f"✅ API Summary: {response.status_code}")
            
            return True
        else:
            print("❌ Login falhou")
            return False
            
    except Exception as e:
        print(f"❌ Teste de login: {e}")
        return False

def test_freqtrade_apis():
    """Testa conectividade com APIs FreqTrade"""
    print("\n🔍 TESTANDO CONECTIVIDADE COM FREQTRADE")
    print("=" * 50)
    
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
            response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} (:{port}): OK")
                working += 1
            else:
                print(f"❌ {name} (:{port}): Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} (:{port}): {str(e)[:50]}...")
    
    print(f"\n📊 APIs FreqTrade funcionando: {working}/{len(apis)}")
    return working == len(apis)

def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DO SISTEMA COM DASHBOARD")
    print("=" * 60)
    
    # Teste 1: APIs FreqTrade
    freqtrade_ok = test_freqtrade_apis()
    
    if not freqtrade_ok:
        print("\n❌ APIs FreqTrade não estão funcionando!")
        print("Execute: docker-compose -f docker-compose-simple.yml restart")
        return
    
    # Teste 2: Iniciar dashboard em thread separada
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Teste 3: Testar dashboard
    dashboard_ok = test_dashboard_endpoints()
    
    # Resultado final
    print(f"\n🎯 RESULTADO FINAL")
    print("=" * 60)
    print(f"✅ APIs FreqTrade: {'OK' if freqtrade_ok else 'ERRO'}")
    print(f"✅ Dashboard Web: {'OK' if dashboard_ok else 'ERRO'}")
    
    if freqtrade_ok and dashboard_ok:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("🌐 Acesse: http://localhost:5000")
        print("👤 Login: sandro / Senha: sandro2020")
        print("\n🔄 Pressione Ctrl+C para parar")
        
        try:
            # Manter dashboard rodando
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Sistema parado pelo usuário")
    else:
        print("\n❌ Sistema com problemas")

if __name__ == "__main__":
    main()
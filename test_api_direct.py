#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto das APIs FreqTrade
"""

import requests
import time
import json

def test_single_api(port, name):
    """Testa uma API específica com mais detalhes"""
    print(f"\n🔍 Testando {name} (porta {port})")
    print("-" * 40)
    
    base_url = f"http://127.0.0.1:{port}"
    
    # Teste 1: Ping básico
    try:
        response = requests.get(f"{base_url}/api/v1/ping", timeout=10)
        print(f"  Ping: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  Ping: ERRO - {e}")
        return False
    
    # Teste 2: Status
    try:
        response = requests.get(f"{base_url}/api/v1/status", timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    State: {data.get('state', 'N/A')}")
            print(f"    Dry Run: {data.get('dry_run', 'N/A')}")
    except Exception as e:
        print(f"  Status: ERRO - {e}")
    
    # Teste 3: Home page
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"  Home: {response.status_code}")
    except Exception as e:
        print(f"  Home: ERRO - {e}")
    
    return True

def test_container_health():
    """Testa saúde dos containers"""
    print("🐳 TESTANDO CONTAINERS")
    print("=" * 50)
    
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'ft-' in line:
                    print(f"  {line}")
        else:
            print("  ❌ Erro ao verificar containers")
            
    except Exception as e:
        print(f"  ❌ Docker não disponível: {e}")

def main():
    """Função principal"""
    print("🔍 TESTE DIRETO DAS APIS FREQTRADE")
    print("=" * 50)
    
    # Testar containers primeiro
    test_container_health()
    
    # Aguardar um pouco
    print("\n⏳ Aguardando 10 segundos...")
    time.sleep(10)
    
    # Testar APIs
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
        if test_single_api(port, name):
            working += 1
        time.sleep(2)  # Pausa entre testes
    
    print(f"\n📊 RESULTADO FINAL")
    print("=" * 50)
    print(f"APIs funcionando: {working}/{len(apis)}")
    
    if working == 0:
        print("\n🚨 NENHUMA API FUNCIONANDO!")
        print("Possíveis causas:")
        print("1. Containers não inicializaram completamente")
        print("2. Problema nas configurações")
        print("3. Problema com credenciais da exchange")
        print("4. Problema de rede/portas")
        
        print("\nSoluções:")
        print("1. Aguarde mais tempo (containers podem demorar)")
        print("2. Verifique logs: docker logs ft-stratA")
        print("3. Reinicie: docker-compose -f docker-compose-simple.yml restart")

if __name__ == "__main__":
    main()
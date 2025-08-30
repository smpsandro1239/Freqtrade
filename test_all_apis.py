#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido de todas as APIs
"""
import requests
import time

def test_api(port, name):
    """Testa uma API específica"""
    try:
        response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} (:{port}): {response.json()}")
            return True
        else:
            print(f"❌ {name} (:{port}): Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} (:{port}): {str(e)[:50]}...")
        return False

def main():
    """Função principal"""
    print("🔍 TESTANDO TODAS AS APIS")
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
    total = len(apis)
    
    for port, name in apis:
        if test_api(port, name):
            working += 1
        time.sleep(1)  # Pequena pausa entre testes
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {working}/{total} APIs funcionando")
    
    if working == total:
        print("🎉 TODAS AS APIS ESTÃO FUNCIONANDO!")
    elif working > 0:
        print("⚠️ Algumas APIs estão funcionando")
    else:
        print("❌ Nenhuma API está funcionando")

if __name__ == "__main__":
    main()
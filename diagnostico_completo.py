#!/usr/bin/env python3
"""
Diagnóstico Completo do Sistema Freqtrade
Identifica e reporta todos os problemas
"""
import os
import sys
import json
import requests
import subprocess
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_docker_status():
    """Verificar status do Docker"""
    print_section("DOCKER STATUS")
    
    try:
        # Verificar se Docker está rodando
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker não está rodando ou não está instalado")
            return False
        
        # Listar containers
        containers = result.stdout
        print("📋 Containers ativos:")
        print(containers)
        
        # Verificar containers específicos
        required = ['ft-stratA', 'ft-stratB', 'ft-waveHyperNW', 'ft-mlStrategy', 
                   'ft-mlStrategySimple', 'ft-multiTimeframe', 'ft-waveHyperNWEnhanced']
        
        found = []
        for container in required:
            if container in containers:
                print(f"✅ {container} - Encontrado")
                found.append(container)
            else:
                print(f"❌ {container} - Não encontrado")
        
        return len(found) > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar Docker: {e}")
        return False

def check_container_logs():
    """Verificar logs dos containers"""
    print_section("LOGS DOS CONTAINERS")
    
    containers = ['ft-stratA', 'ft-stratB', 'ft-waveHyperNW']
    
    for container in containers:
        print(f"\n--- LOGS {container} ---")
        try:
            result = subprocess.run(['docker', 'logs', container, '--tail', '5'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
            else:
                print(f"❌ Erro ao obter logs de {container}")
        except Exception as e:
            print(f"❌ Erro: {e}")

def check_api_endpoints():
    """Verificar endpoints das APIs"""
    print_section("TESTE DAS APIS")
    
    apis = {
        'Strategy A': 'http://127.0.0.1:8081',
        'Strategy B': 'http://127.0.0.1:8082',
        'WaveHyperNW': 'http://127.0.0.1:8083',
        'ML Strategy': 'http://127.0.0.1:8084',
        'ML Simple': 'http://127.0.0.1:8085',
        'Multi Timeframe': 'http://127.0.0.1:8086',
        'Wave Enhanced': 'http://127.0.0.1:8087'
    }
    
    working_apis = []
    
    for name, url in apis.items():
        print(f"\n🔍 Testando {name} ({url})...")
        
        # Testar ping
        try:
            response = requests.get(f"{url}/api/v1/ping", timeout=5)
            print(f"   Ping: {response.status_code}")
        except Exception as e:
            print(f"   Ping: ❌ {e}")
        
        # Testar página principal
        try:
            response = requests.get(url, timeout=5)
            print(f"   Home: {response.status_code}")
            if response.status_code == 200:
                working_apis.append(name)
        except Exception as e:
            print(f"   Home: ❌ {e}")
    
    print(f"\n📊 APIs funcionando: {len(working_apis)}/{len(apis)}")
    return working_apisdef che
ck_config_files():
    """Verificar arquivos de configuração"""
    print_section("CONFIGURAÇÕES")
    
    configs = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/multiTimeframe.json',
        'user_data/configs/waveHyperNWEnhanced.json'
    ]
    
    for config_file in configs:
        print(f"\n🔍 Verificando {config_file}...")
        
        if not os.path.exists(config_file):
            print(f"   ❌ Arquivo não existe")
            continue
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Verificar campos essenciais
            required_fields = ['exchange', 'entry_pricing', 'exit_pricing', 'api_server']
            missing = []
            
            for field in required_fields:
                if field not in config:
                    missing.append(field)
            
            if missing:
                print(f"   ⚠️ Campos faltando: {', '.join(missing)}")
            else:
                print(f"   ✅ Configuração válida")
                
            # Verificar API server
            if 'api_server' in config:
                api = config['api_server']
                enabled = api.get('enabled', False)
                port = api.get('listen_port', 'N/A')
                print(f"   API: {'✅' if enabled else '❌'} Enabled, Port: {port}")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON inválido: {e}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def check_strategy_files():
    """Verificar arquivos de estratégia"""
    print_section("ESTRATÉGIAS")
    
    strategies = [
        'user_data/strategies/SampleStrategyA.py',
        'user_data/strategies/SampleStrategyB.py',
        'user_data/strategies/WaveHyperNWStrategy.py',
        'user_data/strategies/MLStrategy.py',
        'user_data/strategies/MLStrategySimple.py',
        'user_data/strategies/MultiTimeframeStrategy.py',
        'user_data/strategies/WaveHyperNWEnhanced.py'
    ]
    
    for strategy_file in strategies:
        print(f"\n🔍 Verificando {strategy_file}...")
        
        if not os.path.exists(strategy_file):
            print(f"   ❌ Arquivo não existe")
            continue
        
        try:
            with open(strategy_file, 'r') as f:
                content = f.read()
            
            # Verificar se contém classe de estratégia
            if 'class ' in content and 'IStrategy' in content:
                print(f"   ✅ Estratégia válida")
            else:
                print(f"   ⚠️ Pode não ser uma estratégia válida")
                
        except Exception as e:
            print(f"   ❌ Erro ao ler: {e}")

def check_ports():
    """Verificar se as portas estão sendo usadas"""
    print_section("PORTAS")
    
    ports = [8081, 8082, 8083, 8084, 8085, 8086, 8087]
    
    for port in ports:
        try:
            response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
            print(f"✅ Porta {port}: Respondendo (HTTP {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ Porta {port}: Conexão recusada")
        except requests.exceptions.Timeout:
            print(f"⏰ Porta {port}: Timeout")
        except Exception as e:
            print(f"❌ Porta {port}: {e}")

def generate_fix_script():
    """Gerar script de correção"""
    print_section("GERANDO SCRIPT DE CORREÇÃO")
    
    fix_script = """@echo off
echo 🔧 SCRIPT DE CORREÇÃO AUTOMÁTICA
echo.

echo 1. Parando containers...
docker-compose -f docker-compose-simples.yml down

echo 2. Removendo containers antigos...
docker container prune -f

echo 3. Recriando containers...
docker-compose -f docker-compose-simples.yml up -d --force-recreate

echo 4. Aguardando inicialização...
timeout /t 60 /nobreak >nul

echo 5. Verificando status...
docker-compose -f docker-compose-simples.yml ps

echo ✅ Correção concluída!
pause
"""
    
    with open('corrigir_sistema.bat', 'w') as f:
        f.write(fix_script)
    
    print("✅ Script 'corrigir_sistema.bat' criado")

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO COMPLETO DO SISTEMA FREQTRADE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar verificações
    docker_ok = check_docker_status()
    check_container_logs()
    working_apis = check_api_endpoints()
    check_config_files()
    check_strategy_files()
    check_ports()
    
    # Resumo final
    print_section("RESUMO FINAL")
    
    if len(working_apis) >= 5:
        print("🎉 Sistema funcionando bem!")
        print(f"✅ {len(working_apis)} APIs respondendo")
    elif len(working_apis) >= 3:
        print("⚠️ Sistema parcialmente funcional")
        print(f"🔧 {len(working_apis)} APIs funcionando, algumas precisam de atenção")
    else:
        print("❌ Sistema com problemas críticos")
        print("🚨 Poucas ou nenhuma API funcionando")
        generate_fix_script()
    
    print("\n💡 PRÓXIMOS PASSOS:")
    if len(working_apis) < 5:
        print("1. Execute: reiniciar_sistema_corrigido.bat")
        print("2. Aguarde 2-3 minutos para inicialização")
        print("3. Execute este diagnóstico novamente")
    else:
        print("1. Teste no Telegram: /start")
        print("2. Acesse as APIs no navegador")
        print("3. Use os comandos: /status, /predict, /charts")

if __name__ == "__main__":
    main()
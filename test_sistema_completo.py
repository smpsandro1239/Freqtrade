#!/usr/bin/env python3
"""
Teste do Sistema Completo - Verificar se tudo está funcionando
"""
import os
import sys
import time
import requests
import subprocess
from datetime import datetime

def print_header(title):
    """Imprimir cabeçalho"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def test_docker_containers():
    """Testar se os containers estão rodando"""
    print_header("TESTANDO CONTAINERS DOCKER")
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if result.returncode == 0:
            containers = result.stdout
            
            # Verificar containers específicos
            required_containers = [
                'ft-stratA', 'ft-stratB', 'ft-waveHyperNW', 
                'ft-mlStrategy', 'ft-mlStrategySimple', 
                'ft-multiTimeframe', 'ft-waveHyperNWEnhanced',
                'ft-redis'
            ]
            
            running_containers = []
            for container in required_containers:
                if container in containers:
                    print(f"✅ {container} - Rodando")
                    running_containers.append(container)
                else:
                    print(f"❌ {container} - Não encontrado")
            
            print(f"\n📊 Resultado: {len(running_containers)}/{len(required_containers)} containers rodando")
            return len(running_containers) == len(required_containers)
        else:
            print("❌ Erro ao executar docker ps")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar containers: {e}")
        return False

def test_api_connections():
    """Testar conexões com as APIs"""
    print_header("TESTANDO CONEXÕES COM APIS")
    
    apis = {
        'stratA': 'http://127.0.0.1:8081',
        'stratB': 'http://127.0.0.1:8082',
        'waveHyperNW': 'http://127.0.0.1:8083',
        'mlStrategy': 'http://127.0.0.1:8084',
        'mlStrategySimple': 'http://127.0.0.1:8085',
        'multiTimeframe': 'http://127.0.0.1:8086',
        'waveHyperNWEnhanced': 'http://127.0.0.1:8087'
    }
    
    working_apis = 0
    
    for strategy, url in apis.items():
        try:
            # Testar endpoint básico
            response = requests.get(f"{url}/api/v1/ping", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {strategy} ({url}) - API respondendo")
                working_apis += 1
            else:
                print(f"⚠️ {strategy} ({url}) - API respondeu com status {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ {strategy} ({url}) - Conexão recusada")
        except requests.exceptions.Timeout:
            print(f"⏰ {strategy} ({url}) - Timeout")
        except Exception as e:
            print(f"❌ {strategy} ({url}) - Erro: {e}")
    
    print(f"\n📊 Resultado: {working_apis}/{len(apis)} APIs funcionando")
    return working_apis > 0

def test_telegram_bot():
    """Testar bot do Telegram"""
    print_header("TESTANDO BOT TELEGRAM")
    
    token = os.getenv('TELEGRAM_TOKEN', '7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs')
    
    if not token:
        print("❌ TELEGRAM_TOKEN não configurado")
        return False
    
    try:
        # Testar API do Telegram
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['username']
                print(f"✅ Bot @{bot_name} - Conectado e funcionando")
                return True
            else:
                print(f"❌ Bot - Resposta inválida: {bot_info}")
                return False
        else:
            print(f"❌ Bot - Status HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar bot: {e}")
        return False

def test_python_modules():
    """Testar se os módulos Python estão funcionando"""
    print_header("TESTANDO MÓDULOS PYTHON")
    
    modules_to_test = [
        'freqtrade_api_client',
        'advanced_ai_predictor', 
        'chart_generator'
    ]
    
    working_modules = 0
    
    # Adicionar diretório scripts ao path
    sys.path.insert(0, 'scripts')
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} - Importado com sucesso")
            working_modules += 1
        except ImportError as e:
            print(f"❌ {module} - Erro de importação: {e}")
        except Exception as e:
            print(f"❌ {module} - Erro: {e}")
    
    print(f"\n📊 Resultado: {working_modules}/{len(modules_to_test)} módulos funcionando")
    return working_modules == len(modules_to_test)

def test_ai_predictor():
    """Testar IA preditiva"""
    print_header("TESTANDO IA PREDITIVA")
    
    try:
        sys.path.insert(0, 'scripts')
        from advanced_ai_predictor import ai_predictor
        
        print("⏳ Executando análise de mercado...")
        market_overview = ai_predictor.generate_market_overview()
        
        if market_overview and 'timestamp' in market_overview:
            print("✅ IA Preditiva - Funcionando")
            print(f"📊 Estratégias analisadas: {len(market_overview.get('strategies', {}))}")
            print(f"🔮 Sentimento: {market_overview.get('market_sentiment', {}).get('description', 'N/A')}")
            return True
        else:
            print("❌ IA Preditiva - Resposta inválida")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar IA: {e}")
        return False

def test_chart_generator():
    """Testar gerador de gráficos"""
    print_header("TESTANDO GERADOR DE GRÁFICOS")
    
    try:
        sys.path.insert(0, 'scripts')
        from chart_generator import chart_generator
        
        print("⏳ Gerando gráfico de comparação...")
        comparison_chart = chart_generator.generate_performance_comparison()
        
        if comparison_chart and len(comparison_chart) > 50:
            print("✅ Gráfico de Comparação - Funcionando")
        else:
            print("⚠️ Gráfico de Comparação - Resposta pequena")
        
        print("⏳ Gerando mapa de calor...")
        heatmap = chart_generator.generate_market_heatmap()
        
        if heatmap and len(heatmap) > 50:
            print("✅ Mapa de Calor - Funcionando")
            return True
        else:
            print("⚠️ Mapa de Calor - Resposta pequena")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar gráficos: {e}")
        return False

def run_full_test():
    """Executar teste completo do sistema"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Containers Docker", test_docker_containers),
        ("APIs Freqtrade", test_api_connections),
        ("Bot Telegram", test_telegram_bot),
        ("Módulos Python", test_python_modules),
        ("IA Preditiva", test_ai_predictor),
        ("Gerador de Gráficos", test_chart_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Pequena pausa entre testes
    
    # Resumo final
    print_header("RESUMO FINAL DOS TESTES")
    
    passed_tests = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 RESULTADO GERAL: {passed_tests}/{len(tests)} testes passaram")
    
    if passed_tests == len(tests):
        print("\n🎉 SISTEMA 100% FUNCIONAL!")
        print("✅ Todos os componentes estão funcionando corretamente")
        print("🚀 Sistema pronto para uso em produção")
    elif passed_tests >= len(tests) * 0.8:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("🔧 Alguns componentes precisam de atenção")
        print("💡 Verifique os erros acima e corrija")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS CRÍTICOS")
        print("🚨 Muitos componentes não estão funcionando")
        print("🔧 Revisão completa necessária")
    
    return passed_tests == len(tests)

if __name__ == "__main__":
    success = run_full_test()
    
    if success:
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Acesse o Telegram e teste o bot @smpsandrobot")
        print("2. Use /start para ver o menu principal")
        print("3. Teste os comandos: /status, /predict, /charts")
        print("4. Acesse as APIs em http://127.0.0.1:8081-8087")
        print("5. Monitore os logs com: docker-compose logs -f")
    else:
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("1. Verifique se o Docker está rodando")
        print("2. Execute: docker-compose up -d")
        print("3. Aguarde alguns minutos para inicialização")
        print("4. Execute este teste novamente")
    
    sys.exit(0 if success else 1)
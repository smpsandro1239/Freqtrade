#!/usr/bin/env python3
"""
Controlar Estratégias - Script para ativar/desativar estratégias individualmente
"""
import subprocess
import sys
import time

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🎮 {title}")
    print('='*50)

def list_strategies():
    """Listar todas as estratégias disponíveis"""
    strategies = {
        '1': {'name': 'Strategy A', 'container': 'ft-stratA', 'port': '8081'},
        '2': {'name': 'Strategy B', 'container': 'ft-stratB', 'port': '8082'},
        '3': {'name': 'WaveHyperNW', 'container': 'ft-waveHyperNW', 'port': '8083'},
        '4': {'name': 'ML Strategy', 'container': 'ft-mlStrategy', 'port': '8084'},
        '5': {'name': 'ML Simple', 'container': 'ft-mlStrategySimple', 'port': '8085'},
        '6': {'name': 'Multi Timeframe', 'container': 'ft-multiTimeframe', 'port': '8086'},
        '7': {'name': 'Wave Enhanced', 'container': 'ft-waveHyperNWEnhanced', 'port': '8087'}
    }
    return strategies

def get_container_status(container_name):
    """Obter status de um container"""
    try:
        result = subprocess.run(['docker', 'ps', '--filter', f'name={container_name}', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        
        if container_name in result.stdout:
            if 'Up' in result.stdout:
                return '🟢 Ativo'
            else:
                return '🟡 Parado'
        else:
            return '🔴 Não encontrado'
    except:
        return '❌ Erro'

def start_strategy(container_name):
    """Iniciar uma estratégia"""
    try:
        print(f"🚀 Iniciando {container_name}...")
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'start', container_name.replace('ft-', '')], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {container_name} iniciado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao iniciar {container_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def stop_strategy(container_name):
    """Parar uma estratégia"""
    try:
        print(f"🛑 Parando {container_name}...")
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'stop', container_name.replace('ft-', '')], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {container_name} parado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao parar {container_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def restart_strategy(container_name):
    """Reiniciar uma estratégia"""
    try:
        print(f"🔄 Reiniciando {container_name}...")
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'restart', container_name.replace('ft-', '')], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {container_name} reiniciado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao reiniciar {container_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def show_logs(container_name):
    """Mostrar logs de uma estratégia"""
    try:
        print(f"📋 Logs de {container_name} (últimas 20 linhas):")
        print("-" * 60)
        result = subprocess.run(['docker', 'logs', container_name, '--tail', '20'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
        else:
            print(f"❌ Erro ao obter logs")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main_menu():
    """Menu principal"""
    strategies = list_strategies()
    
    while True:
        print_header("CONTROLE DE ESTRATÉGIAS")
        
        print("📊 STATUS ATUAL:")
        for key, strategy in strategies.items():
            status = get_container_status(strategy['container'])
            print(f"{key}. {strategy['name']:<20} {status} (Porta: {strategy['port']})")
        
        print("\n🎮 AÇÕES DISPONÍVEIS:")
        print("s[número] - Iniciar estratégia (ex: s1)")
        print("p[número] - Parar estratégia (ex: p1)")
        print("r[número] - Reiniciar estratégia (ex: r1)")
        print("l[número] - Ver logs (ex: l1)")
        print("all_start - Iniciar todas")
        print("all_stop - Parar todas")
        print("all_restart - Reiniciar todas")
        print("status - Atualizar status")
        print("q - Sair")
        
        choice = input("\n🎯 Escolha uma ação: ").strip().lower()
        
        if choice == 'q':
            print("👋 Saindo...")
            break
        elif choice == 'status':
            continue
        elif choice == 'all_start':
            print("🚀 Iniciando todas as estratégias...")
            subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'start'])
            print("✅ Comando executado!")
            time.sleep(2)
        elif choice == 'all_stop':
            print("🛑 Parando todas as estratégias...")
            subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'stop'])
            print("✅ Comando executado!")
            time.sleep(2)
        elif choice == 'all_restart':
            print("🔄 Reiniciando todas as estratégias...")
            subprocess.run(['docker-compose', '-f', 'docker-compose-simples.yml', 'restart'])
            print("✅ Comando executado!")
            time.sleep(2)
        elif choice.startswith('s') and len(choice) == 2:
            strategy_num = choice[1]
            if strategy_num in strategies:
                start_strategy(strategies[strategy_num]['container'])
                time.sleep(2)
        elif choice.startswith('p') and len(choice) == 2:
            strategy_num = choice[1]
            if strategy_num in strategies:
                stop_strategy(strategies[strategy_num]['container'])
                time.sleep(2)
        elif choice.startswith('r') and len(choice) == 2:
            strategy_num = choice[1]
            if strategy_num in strategies:
                restart_strategy(strategies[strategy_num]['container'])
                time.sleep(2)
        elif choice.startswith('l') and len(choice) == 2:
            strategy_num = choice[1]
            if strategy_num in strategies:
                show_logs(strategies[strategy_num]['container'])
                input("\nPressione Enter para continuar...")
        else:
            print("❌ Opção inválida!")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n👋 Saindo...")
        sys.exit(0)
#!/usr/bin/env python3
"""
🚀 Inicializador do Sistema - FreqTrade Multi-Strategy
Script principal para iniciar todo o sistema de forma simples
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Verificar se dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import flask
        import redis
        import docker
        import pandas
        import numpy
        print("✅ Dependências Python OK")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def check_credentials():
    """Verificar status das credenciais"""
    print("🔐 Verificando credenciais...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    # Verificar se tem credenciais reais
    with open(env_file, 'r') as f:
        content = f.read()
    
    if 'YOUR_TELEGRAM_BOT_TOKEN_HERE' in content:
        print("⚠️  Credenciais não configuradas (usando placeholders)")
        return False
    
    print("✅ Credenciais configuradas")
    return True

def show_menu():
    """Mostrar menu de opções"""
    print("\n🎮 FREQTRADE MULTI-STRATEGY - MENU PRINCIPAL")
    print("=" * 60)
    print()
    print("Escolha uma opção:")
    print()
    print("1. 🔧 Configurar Credenciais")
    print("2. 🧪 Testar Credenciais")
    print("3. 📊 Iniciar Dashboard Web (Demo)")
    print("4. 🤖 Iniciar Sistema Telegram (Requer credenciais)")
    print("5. 🔗 Iniciar Sistema Completo (Requer credenciais)")
    print("6. 🎮 Ver Demonstração do Sistema")
    print("7. 📋 Validar Estratégias")
    print("8. ❌ Sair")
    print()

def run_command(command, description):
    """Executar comando com feedback"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} concluído com sucesso!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Erro em {description}:")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar {description}: {e}")
        return False

def start_dashboard_demo():
    """Iniciar dashboard em modo demo"""
    print("📊 INICIANDO DASHBOARD WEB (MODO DEMO)")
    print("-" * 40)
    print()
    print("🌐 O dashboard será aberto em: http://localhost:5000")
    print("👤 Login: admin")
    print("🔑 Senha: admin123")
    print()
    print("⚠️  MODO DEMO: Dados simulados para demonstração")
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    try:
        # Definir variáveis de ambiente para demo
        os.environ['DASHBOARD_USERNAME'] = 'admin'
        os.environ['DASHBOARD_PASSWORD'] = 'admin123'
        os.environ['DASHBOARD_SECRET_KEY'] = 'demo-secret-key-for-testing'
        
        # Importar e executar dashboard
        from scripts.dashboard_main import app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def start_telegram_system():
    """Iniciar sistema Telegram"""
    if not check_credentials():
        print("❌ Configure suas credenciais primeiro (opção 1)")
        return
    
    print("🤖 INICIANDO SISTEMA TELEGRAM")
    print("-" * 40)
    print()
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    try:
        from scripts.telegram_system_main import main as telegram_main
        telegram_main()
    except KeyboardInterrupt:
        print("\n🛑 Sistema Telegram parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema Telegram: {e}")

def start_complete_system():
    """Iniciar sistema completo"""
    if not check_credentials():
        print("❌ Configure suas credenciais primeiro (opção 1)")
        return
    
    print("🔗 INICIANDO SISTEMA COMPLETO")
    print("-" * 40)
    print()
    print("🌐 Dashboard: http://localhost:5000")
    print("🤖 Telegram: Envie /start para seu bot")
    print("🔄 Pressione Ctrl+C para parar")
    print()
    
    try:
        from scripts.integrated_system import IntegratedSystem
        system = IntegratedSystem()
        system.start_complete_system()
    except KeyboardInterrupt:
        print("\n🛑 Sistema completo parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema completo: {e}")

def main():
    """Função principal"""
    print("🚀 FREQTRADE MULTI-STRATEGY - INICIALIZADOR")
    print("=" * 60)
    print()
    print("Sistema de Trading Automatizado com:")
    print("• 7 Estratégias Validadas")
    print("• Controle via Telegram")
    print("• Dashboard Web com Gráficos")
    print("• IA Preditiva")
    print("• Monitoramento 24/7")
    print()
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Instale as dependências primeiro!")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Digite sua escolha (1-8): ").strip()
            
            if choice == '1':
                print("\n🔧 CONFIGURANDO CREDENCIAIS")
                print("-" * 40)
                run_command("python setup_credentials.py", "Configuração de credenciais")
                
            elif choice == '2':
                print("\n🧪 TESTANDO CREDENCIAIS")
                print("-" * 40)
                run_command("python test_credentials.py", "Teste de credenciais")
                
            elif choice == '3':
                print("\n📊 DASHBOARD WEB (DEMO)")
                print("-" * 40)
                start_dashboard_demo()
                
            elif choice == '4':
                print("\n🤖 SISTEMA TELEGRAM")
                print("-" * 40)
                start_telegram_system()
                
            elif choice == '5':
                print("\n🔗 SISTEMA COMPLETO")
                print("-" * 40)
                start_complete_system()
                
            elif choice == '6':
                print("\n🎮 DEMONSTRAÇÃO DO SISTEMA")
                print("-" * 40)
                run_command("python demo_system.py", "Demonstração do sistema")
                
            elif choice == '7':
                print("\n📋 VALIDANDO ESTRATÉGIAS")
                print("-" * 40)
                run_command("python validate_strategies.py", "Validação de estratégias")
                
            elif choice == '8':
                print("\n👋 Saindo do sistema...")
                break
                
            else:
                print("\n❌ Opção inválida! Digite um número de 1 a 8.")
            
            if choice != '8':
                input("\n⏳ Pressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            input("\n⏳ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
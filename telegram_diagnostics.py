#!/usr/bin/env python3
"""
Diagnóstico do Telegram Commander
Verifica configuração e identifica problemas
"""
import os
import sys
import json
import subprocess
import docker
from pathlib import Path

def check_environment():
    """Verificar variáveis de ambiente"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO AMBIENTE")
    print("-" * 50)
    
    required_vars = ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    issues = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mascarar token para segurança
            if var == 'TELEGRAM_TOKEN':
                display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADO")
            issues.append(f"{var} não está configurado")
    
    return issues

def check_files():
    """Verificar arquivos necessários"""
    print("\n🔍 VERIFICANDO ARQUIVOS NECESSÁRIOS")
    print("-" * 50)
    
    required_files = [
        'scripts/telegram_commander.py',
        'scripts/strategy_controller.py',
        'scripts/freqtrade_stats.py',
        'docker-compose.yml',
        '.env'
    ]
    
    issues = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path}: ARQUIVO NÃO ENCONTRADO")
            issues.append(f"Arquivo {file_path} não encontrado")
    
    return issues

def check_docker():
    """Verificar Docker e containers"""
    print("\n🔍 VERIFICANDO DOCKER E CONTAINERS")
    print("-" * 50)
    
    issues = []
    
    try:
        # Verificar se Docker está rodando
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Docker está rodando")
        else:
            print("   ❌ Docker não está rodando")
            issues.append("Docker não está rodando")
            return issues
    except FileNotFoundError:
        print("   ❌ Docker não está instalado")
        issues.append("Docker não está instalado")
        return issues
    
    # Verificar containers das estratégias
    strategies = ['ft-stratA', 'ft-stratB', 'ft-waveHyperNW', 'telegram_commander']
    
    for container in strategies:
        try:
            result = subprocess.run(['docker', 'ps', '-a', '--filter', f'name={container}', '--format', 'table {{.Names}}\t{{.Status}}'], 
                                  capture_output=True, text=True)
            if container in result.stdout:
                status_line = [line for line in result.stdout.split('\n') if container in line]
                if status_line:
                    status = status_line[0].split('\t')[1] if '\t' in status_line[0] else 'unknown'
                    if 'Up' in status:
                        print(f"   🟢 {container}: {status}")
                    else:
                        print(f"   🔴 {container}: {status}")
                        if container == 'telegram_commander':
                            issues.append(f"Container {container} não está rodando")
            else:
                print(f"   ❌ {container}: NÃO ENCONTRADO")
                issues.append(f"Container {container} não encontrado")
        except Exception as e:
            print(f"   ❌ {container}: ERRO - {e}")
            issues.append(f"Erro ao verificar container {container}: {e}")
    
    return issues

def check_python_dependencies():
    """Verificar dependências Python"""
    print("\n🔍 VERIFICANDO DEPENDÊNCIAS PYTHON")
    print("-" * 50)
    
    required_packages = [
        'telegram',
        'docker',
        'asyncio'
    ]
    
    issues = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}: INSTALADO")
        except ImportError:
            print(f"   ❌ {package}: NÃO INSTALADO")
            issues.append(f"Pacote Python {package} não está instalado")
    
    return issues

def check_strategy_configs():
    """Verificar configurações das estratégias"""
    print("\n🔍 VERIFICANDO CONFIGURAÇÕES DAS ESTRATÉGIAS")
    print("-" * 50)
    
    config_files = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json'
    ]
    
    issues = []
    
    for config_file in config_files:
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Verificar campos essenciais
                essential_fields = ['dry_run', 'stake_amount', 'max_open_trades']
                missing_fields = [field for field in essential_fields if field not in config]
                
                if missing_fields:
                    print(f"   ⚠️ {config_file}: Campos faltando: {missing_fields}")
                    issues.append(f"Configuração {config_file} está incompleta")
                else:
                    dry_run = "DRY" if config.get('dry_run', True) else "LIVE"
                    print(f"   ✅ {config_file}: {dry_run}, Stake: {config.get('stake_amount', 0)}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ {config_file}: JSON INVÁLIDO - {e}")
                issues.append(f"Configuração {config_file} tem JSON inválido")
            except Exception as e:
                print(f"   ❌ {config_file}: ERRO - {e}")
                issues.append(f"Erro ao ler configuração {config_file}: {e}")
        else:
            print(f"   ❌ {config_file}: NÃO ENCONTRADO")
            issues.append(f"Arquivo de configuração {config_file} não encontrado")
    
    return issues

def check_telegram_connectivity():
    """Verificar conectividade com Telegram"""
    print("\n🔍 VERIFICANDO CONECTIVIDADE COM TELEGRAM")
    print("-" * 50)
    
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    issues = []
    
    if not token or not chat_id:
        print("   ❌ Token ou Chat ID não configurados")
        issues.append("Configuração do Telegram incompleta")
        return issues
    
    try:
        import requests
        
        # Testar API do Telegram
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✅ Bot conectado: @{bot_info.get('username', 'unknown')}")
                
                # Testar envio de mensagem
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                test_data = {
                    'chat_id': chat_id,
                    'text': '🧪 Teste de conectividade - Bot funcionando!'
                }
                
                send_response = requests.post(send_url, json=test_data, timeout=10)
                if send_response.status_code == 200:
                    print("   ✅ Mensagem de teste enviada com sucesso")
                else:
                    print(f"   ❌ Erro ao enviar mensagem: {send_response.status_code}")
                    issues.append("Não foi possível enviar mensagem de teste")
            else:
                print(f"   ❌ Resposta da API inválida: {data}")
                issues.append("Token do Telegram inválido")
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
            issues.append(f"Erro na API do Telegram: {response.status_code}")
    
    except ImportError:
        print("   ⚠️ Biblioteca 'requests' não disponível - pulando teste de conectividade")
    except Exception as e:
        print(f"   ❌ Erro na conectividade: {e}")
        issues.append(f"Erro de conectividade: {e}")
    
    return issues

def generate_diagnostic_report(all_issues):
    """Gerar relatório de diagnóstico"""
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE DIAGNÓSTICO")
    print("=" * 60)
    
    if not all_issues:
        print("\n🎉 PARABÉNS! Nenhum problema encontrado!")
        print("✅ Todas as verificações passaram com sucesso")
        print("🚀 O Telegram Commander deve estar funcionando corretamente")
    else:
        print(f"\n⚠️ PROBLEMAS ENCONTRADOS: {len(all_issues)}")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 SUGESTÕES DE CORREÇÃO:")
        
        # Sugestões específicas baseadas nos problemas
        if any("TELEGRAM_TOKEN" in issue for issue in all_issues):
            print("   • Configure TELEGRAM_TOKEN no arquivo .env")
            print("   • Obtenha o token do @BotFather no Telegram")
        
        if any("TELEGRAM_CHAT_ID" in issue for issue in all_issues):
            print("   • Configure TELEGRAM_CHAT_ID no arquivo .env")
            print("   • Use @userinfobot para descobrir seu Chat ID")
        
        if any("Docker" in issue for issue in all_issues):
            print("   • Instale e inicie o Docker Desktop")
            print("   • Execute: docker compose up -d")
        
        if any("Container" in issue for issue in all_issues):
            print("   • Execute: docker compose up -d telegram_commander")
            print("   • Verifique logs: docker compose logs telegram_commander")
        
        if any("Python" in issue for issue in all_issues):
            print("   • Instale dependências: pip install python-telegram-bot docker")
        
        if any("configuração" in issue.lower() for issue in all_issues):
            print("   • Verifique arquivos de configuração JSON")
            print("   • Execute: python scripts/strategy_controller.py --validate")
    
    print(f"\n📅 Diagnóstico executado em: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO DO TELEGRAM COMMANDER")
    print("=" * 60)
    
    all_issues = []
    
    # Executar todas as verificações
    all_issues.extend(check_environment())
    all_issues.extend(check_files())
    all_issues.extend(check_docker())
    all_issues.extend(check_python_dependencies())
    all_issues.extend(check_strategy_configs())
    all_issues.extend(check_telegram_connectivity())
    
    # Gerar relatório final
    generate_diagnostic_report(all_issues)
    
    # Código de saída
    return len(all_issues)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
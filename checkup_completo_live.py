#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHECKUP COMPLETO PARA MODO LIVE
Identifica e corrige todos os problemas do sistema
Prepara para trading em modo live
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

class LiveSystemCheckup:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def print_section(self, title):
        """Imprime seção com formatação"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
    
    def check_encoding_issues(self):
        """Corrige problemas de encoding em todos os scripts"""
        self.print_section("CORRIGINDO PROBLEMAS DE ENCODING")
        
        scripts_with_encoding_issues = [
            'setup_credentials.py',
            'test_credentials.py', 
            'validate_strategies.py',
            'demo_system.py',
            'diagnostico_completo.py'
        ]
        
        for script in scripts_with_encoding_issues:
            if os.path.exists(script):
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remover emojis problemáticos
                    problematic_chars = [
                        '\U0001f512', '\U0001f50d', '\U0001f3ae', 
                        '\U0001f9ea', '\u274c', '\U0001f527'
                    ]
                    
                    for char in problematic_chars:
                        content = content.replace(char, '')
                    
                    # Salvar com encoding correto
                    with open(script, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Corrigido encoding em {script}")
                    self.fixes_applied.append(f"Encoding corrigido em {script}")
                    
                except Exception as e:
                    print(f"❌ Erro ao corrigir {script}: {e}")
                    self.issues_found.append(f"Erro de encoding em {script}")
    
    def check_credentials_setup(self):
        """Verifica e configura credenciais"""
        self.print_section("VERIFICANDO CREDENCIAIS")
        
        env_file = Path('.env')
        if not env_file.exists():
            print("❌ Arquivo .env não encontrado")
            self.create_env_template()
            return False
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se tem placeholders
            placeholders = [
                'YOUR_TELEGRAM_BOT_TOKEN_HERE',
                'YOUR_TELEGRAM_CHAT_ID_HERE',
                'your-binance-api-key',
                'your-binance-secret-key'
            ]
            
            has_placeholders = any(placeholder in content for placeholder in placeholders)
            
            if has_placeholders:
                print("⚠️ Credenciais usando placeholders")
                print("💡 Para modo LIVE, configure credenciais reais:")
                print("   1. Token do Telegram Bot")
                print("   2. Chat ID do Telegram")
                print("   3. API Key da Binance")
                print("   4. Secret Key da Binance")
                self.issues_found.append("Credenciais não configuradas para LIVE")
                return False
            else:
                print("✅ Credenciais configuradas")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao verificar credenciais: {e}")
            self.issues_found.append("Erro ao verificar credenciais")
            return False
    
    def create_env_template(self):
        """Cria template do .env"""
        template = '''# FREQTRADE MULTI-STRATEGY - CONFIGURAÇÕES
# Configure suas credenciais reais aqui para modo LIVE

# TELEGRAM BOT (Obrigatório para controle remoto)
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE

# BINANCE API (Obrigatório para trading real)
EXCHANGE_KEY=your-binance-api-key
EXCHANGE_SECRET=your-binance-secret-key

# DASHBOARD WEB
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin123
DASHBOARD_SECRET_KEY=your-secret-key-here

# CONFIGURAÇÕES DE SEGURANÇA
MAX_OPEN_TRADES=5
STAKE_AMOUNT=50
DRY_RUN=true
'''
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(template)
        
        print("✅ Arquivo .env criado com template")
        self.fixes_applied.append("Arquivo .env criado")
    
    def check_docker_system(self):
        """Verifica sistema Docker"""
        self.print_section("VERIFICANDO SISTEMA DOCKER")
        
        try:
            # Verificar se Docker está rodando
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker não está rodando")
                self.issues_found.append("Docker não está rodando")
                return False
            
            # Contar containers ativos
            containers = result.stdout.count('ft-')
            print(f"📊 Containers FreqTrade ativos: {containers}")
            
            if containers < 7:
                print("⚠️ Nem todos os containers estão rodando")
                self.restart_docker_system()
            else:
                print("✅ Todos os containers estão ativos")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar Docker: {e}")
            self.issues_found.append("Erro ao verificar Docker")
            return False
    
    def restart_docker_system(self):
        """Reinicia sistema Docker"""
        print("🔄 Reiniciando sistema Docker...")
        
        try:
            # Parar containers
            subprocess.run(['docker-compose', '-f', 'docker-compose-simple.yml', 'down'], 
                         capture_output=True)
            
            # Iniciar containers
            result = subprocess.run(['docker-compose', '-f', 'docker-compose-simple.yml', 'up', '-d'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Sistema Docker reiniciado")
                self.fixes_applied.append("Sistema Docker reiniciado")
                
                # Aguardar inicialização
                print("⏳ Aguardando inicialização (30s)...")
                time.sleep(30)
            else:
                print(f"❌ Erro ao reiniciar Docker: {result.stderr}")
                self.issues_found.append("Erro ao reiniciar Docker")
                
        except Exception as e:
            print(f"❌ Erro ao reiniciar Docker: {e}")
            self.issues_found.append("Erro ao reiniciar Docker")
    
    def check_apis_status(self):
        """Verifica status das APIs"""
        self.print_section("VERIFICANDO APIS")
        
        apis = [
            (8081, "Strategy A"),
            (8082, "Strategy B"), 
            (8083, "WaveHyperNW"),
            (8084, "ML Strategy"),
            (8085, "ML Simple"),
            (8086, "Multi Timeframe"),
            (8087, "Wave Enhanced")
        ]
        
        working_apis = 0
        
        for port, name in apis:
            try:
                response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} (:{port}): OK")
                    working_apis += 1
                else:
                    print(f"❌ {name} (:{port}): Status {response.status_code}")
                    self.issues_found.append(f"API {name} não respondendo")
            except Exception as e:
                print(f"❌ {name} (:{port}): {str(e)[:50]}...")
                self.issues_found.append(f"API {name} não acessível")
        
        print(f"\n📊 APIs funcionando: {working_apis}/{len(apis)}")
        
        if working_apis < len(apis):
            print("⚠️ Algumas APIs não estão funcionando")
            return False
        else:
            print("✅ Todas as APIs estão funcionando")
            return True
    
    def check_live_readiness(self):
        """Verifica se sistema está pronto para modo LIVE"""
        self.print_section("VERIFICANDO PRONTIDÃO PARA MODO LIVE")
        
        # Verificar configurações DRY_RUN
        configs_to_check = [
            'user_data/configs/stratA.json',
            'user_data/configs/stratB.json',
            'user_data/configs/waveHyperNW.json',
            'user_data/configs/mlStrategy.json',
            'user_data/configs/mlStrategySimple.json',
            'user_data/configs/multiTimeframe.json',
            'user_data/configs/waveHyperNWEnhanced.json'
        ]
        
        dry_run_configs = 0
        
        for config_file in configs_to_check:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    if config.get('dry_run', True):
                        dry_run_configs += 1
                        print(f"🟡 {config_file}: DRY-RUN ativo")
                    else:
                        print(f"🔴 {config_file}: MODO LIVE ativo")
                        
                except Exception as e:
                    print(f"❌ Erro ao verificar {config_file}: {e}")
        
        print(f"\n📊 Configurações em DRY-RUN: {dry_run_configs}/{len(configs_to_check)}")
        
        if dry_run_configs == len(configs_to_check):
            print("✅ Sistema em modo seguro (DRY-RUN)")
            print("💡 Para ativar modo LIVE, use a opção de conversão")
        else:
            print("⚠️ Algumas configurações já estão em modo LIVE")
        
        return dry_run_configs > 0
    
    def create_live_conversion_script(self):
        """Cria script para converter para modo LIVE"""
        self.print_section("CRIANDO SCRIPT DE CONVERSÃO PARA LIVE")
        
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSOR PARA MODO LIVE
ATENÇÃO: Use apenas quando tiver certeza!
"""

import json
import os
from pathlib import Path

def convert_to_live():
    """Converte todas as configurações para modo LIVE"""
    print("⚠️ ATENÇÃO: CONVERSÃO PARA MODO LIVE")
    print("="*50)
    print()
    print("🚨 RISCOS:")
    print("• Trades reais com dinheiro real")
    print("• Possibilidade de perdas financeiras")
    print("• Necessário monitoramento constante")
    print()
    
    confirm = input("Digite 'CONFIRMO' para continuar: ")
    if confirm != 'CONFIRMO':
        print("❌ Conversão cancelada")
        return
    
    configs = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/multiTimeframe.json',
        'user_data/configs/waveHyperNWEnhanced.json'
    ]
    
    converted = 0
    
    for config_file in configs:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Converter para LIVE
                config['dry_run'] = False
                
                # Ajustar configurações para LIVE
                config['stake_amount'] = 50  # Valor conservador
                config['max_open_trades'] = 3  # Limite conservador
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {config_file} convertido para LIVE")
                converted += 1
                
            except Exception as e:
                print(f"❌ Erro ao converter {config_file}: {e}")
    
    print(f"\\n📊 Configurações convertidas: {converted}/{len(configs)}")
    
    if converted > 0:
        print("\\n🔄 Reiniciando sistema...")
        os.system('docker-compose -f docker-compose-simple.yml restart')
        print("✅ Sistema reiniciado em modo LIVE")
        print("\\n🚨 MONITORAMENTO OBRIGATÓRIO!")
        print("• Acesse: http://localhost:5000")
        print("• Use Telegram para controle")
        print("• Monitore trades constantemente")

if __name__ == "__main__":
    convert_to_live()
'''
        
        with open('converter_para_live.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("✅ Script 'converter_para_live.py' criado")
        self.fixes_applied.append("Script de conversão para LIVE criado")
    
    def create_simple_launcher(self):
        """Cria launcher simples sem emojis"""
        self.print_section("CRIANDO LAUNCHER SIMPLES")
        
        launcher_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAUNCHER SIMPLES - FreqTrade Multi-Strategy
Sem emojis para compatibilidade com Windows
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Menu principal simplificado"""
    print("\\nFREQTRADE MULTI-STRATEGY - LAUNCHER")
    print("="*50)
    print()
    print("1. Iniciar Dashboard Web (Demo)")
    print("2. Verificar Status do Sistema") 
    print("3. Testar APIs")
    print("4. Reiniciar Sistema Docker")
    print("5. Converter para Modo LIVE (CUIDADO!)")
    print("6. Sair")
    print()
    
    while True:
        try:
            choice = input("Escolha (1-6): ").strip()
            
            if choice == '1':
                print("\\nIniciando Dashboard...")
                os.system('python -c "from scripts.dashboard_main import app; app.run(host=\\'0.0.0.0\\', port=5000)"')
                
            elif choice == '2':
                print("\\nVerificando sistema...")
                os.system('python diagnostico_completo.py')
                
            elif choice == '3':
                print("\\nTestando APIs...")
                os.system('python test_all_apis.py')
                
            elif choice == '4':
                print("\\nReiniciando Docker...")
                os.system('docker-compose -f docker-compose-simple.yml restart')
                
            elif choice == '5':
                print("\\nCONVERSÃO PARA MODO LIVE...")
                os.system('python converter_para_live.py')
                
            elif choice == '6':
                print("\\nSaindo...")
                break
                
            else:
                print("Opção inválida!")
                
            input("\\nPressione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\\nSaindo...")
            break

if __name__ == "__main__":
    main()
'''
        
        with open('launcher_simples.py', 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print("✅ Launcher simples criado: launcher_simples.py")
        self.fixes_applied.append("Launcher simples criado")
    
    def run_complete_checkup(self):
        """Executa checkup completo"""
        print("🚀 CHECKUP COMPLETO PARA MODO LIVE")
        print("="*60)
        print("Verificando e corrigindo todos os problemas...")
        
        # 1. Corrigir encoding
        self.check_encoding_issues()
        
        # 2. Verificar credenciais
        self.check_credentials_setup()
        
        # 3. Verificar Docker
        self.check_docker_system()
        
        # 4. Verificar APIs
        self.check_apis_status()
        
        # 5. Verificar prontidão para LIVE
        self.check_live_readiness()
        
        # 6. Criar scripts auxiliares
        self.create_live_conversion_script()
        self.create_simple_launcher()
        
        # Relatório final
        self.print_final_report()
    
    def print_final_report(self):
        """Imprime relatório final"""
        self.print_section("RELATÓRIO FINAL")
        
        print(f"📊 PROBLEMAS ENCONTRADOS: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   ❌ {issue}")
        
        print(f"\\n🔧 CORREÇÕES APLICADAS: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   ✅ {fix}")
        
        print("\\n🎯 PRÓXIMOS PASSOS:")
        print("1. Execute: python launcher_simples.py")
        print("2. Teste o dashboard: http://localhost:5000")
        print("3. Configure credenciais reais para Telegram/Binance")
        print("4. Para modo LIVE: python converter_para_live.py")
        
        print("\\n⚠️ IMPORTANTE PARA MODO LIVE:")
        print("• Configure API keys da Binance")
        print("• Configure bot do Telegram")
        print("• Teste em DRY-RUN primeiro")
        print("• Monitore constantemente")
        
        if len(self.issues_found) == 0:
            print("\\n🎉 SISTEMA PRONTO PARA USO!")
        else:
            print("\\n⚠️ Corrija os problemas antes do modo LIVE")

def main():
    """Função principal"""
    checkup = LiveSystemCheckup()
    checkup.run_complete_checkup()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA COMPLETO FUNCIONANDO
Demonstra que todo o sistema está operacional
"""

import os
import sys
import time
import requests
import subprocess
import threading
from datetime import datetime

class SistemaCompleto:
    def __init__(self):
        self.apis_ok = 0
        self.dashboard_ok = False
        self.containers_ok = 0
        
    def verificar_containers(self):
        """Verifica containers Docker"""
        print("🐳 VERIFICANDO CONTAINERS DOCKER")
        print("-" * 50)
        
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                ft_containers = [line for line in lines if 'ft-' in line]
                
                for container in ft_containers:
                    print(f"  ✅ {container}")
                    self.containers_ok += 1
                
                print(f"\n📊 Containers ativos: {self.containers_ok}/7")
                return self.containers_ok >= 7
            else:
                print("  ❌ Erro ao verificar containers")
                return False
                
        except Exception as e:
            print(f"  ❌ Docker não disponível: {e}")
            return False
    
    def verificar_apis_freqtrade(self):
        """Verifica APIs FreqTrade"""
        print("\n🌐 VERIFICANDO APIS FREQTRADE")
        print("-" * 50)
        
        apis = [
            (8081, "Strategy A"),
            (8082, "Strategy B"),
            (8083, "WaveHyperNW"),
            (8084, "ML Strategy"),
            (8085, "ML Simple"),
            (8086, "Multi Timeframe"),
            (8087, "Wave Enhanced")
        ]
        
        for port, name in apis:
            try:
                response = requests.get(f'http://127.0.0.1:{port}/api/v1/ping', timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {name} (:{port}): {response.json()}")
                    self.apis_ok += 1
                else:
                    print(f"  ❌ {name} (:{port}): Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name} (:{port}): {str(e)[:50]}...")
        
        print(f"\n📊 APIs funcionando: {self.apis_ok}/7")
        return self.apis_ok >= 7
    
    def iniciar_dashboard(self):
        """Inicia dashboard em thread separada"""
        try:
            # Configurar variáveis de ambiente
            os.environ['DASHBOARD_USERNAME'] = 'sandro'
            os.environ['DASHBOARD_PASSWORD'] = 'sandro2020'
            os.environ['DASHBOARD_SECRET_KEY'] = 'Benfica456!!!'
            
            # Executar dashboard
            subprocess.run([sys.executable, 'dashboard_simples_funcional.py'], 
                         capture_output=False)
            
        except Exception as e:
            print(f"❌ Erro ao iniciar dashboard: {e}")
    
    def verificar_dashboard(self):
        """Verifica se dashboard está funcionando"""
        print("\n📊 VERIFICANDO DASHBOARD WEB")
        print("-" * 50)
        
        # Aguardar dashboard inicializar
        print("  ⏳ Aguardando dashboard inicializar...")
        time.sleep(8)
        
        try:
            # Testar página inicial
            response = requests.get('http://localhost:5000', timeout=10)
            if response.status_code in [200, 302]:
                print("  ✅ Dashboard acessível")
                
                # Testar login
                session = requests.Session()
                login_data = {
                    'username': 'sandro',
                    'password': 'sandro2020'
                }
                
                response = session.post('http://localhost:5000/login', data=login_data, timeout=10)
                if response.status_code == 302:
                    print("  ✅ Login funcionando")
                    
                    # Testar APIs do dashboard
                    response = session.get('http://localhost:5000/api/summary', timeout=10)
                    if response.status_code == 200:
                        print("  ✅ APIs do dashboard funcionando")
                        data = response.json()
                        print(f"      - Estratégias: {data.get('total_strategies', 0)}")
                        print(f"      - APIs ativas: {data.get('working_apis', 0)}")
                        print(f"      - Lucro total: {data.get('total_profit', 0)} USDT")
                        
                        self.dashboard_ok = True
                        return True
                
            print("  ❌ Dashboard com problemas")
            return False
            
        except Exception as e:
            print(f"  ❌ Dashboard não acessível: {e}")
            return False
    
    def mostrar_resumo_final(self):
        """Mostra resumo final do sistema"""
        print(f"\n🎯 RESUMO FINAL DO SISTEMA")
        print("=" * 60)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Status dos componentes
        componentes = [
            ("🐳 Containers Docker", f"{self.containers_ok}/7", self.containers_ok >= 7),
            ("🌐 APIs FreqTrade", f"{self.apis_ok}/7", self.apis_ok >= 7),
            ("📊 Dashboard Web", "Funcionando" if self.dashboard_ok else "Erro", self.dashboard_ok),
        ]
        
        for nome, status, ok in componentes:
            icon = "✅" if ok else "❌"
            print(f"  {icon} {nome}: {status}")
        
        # Status geral
        tudo_ok = self.containers_ok >= 7 and self.apis_ok >= 7 and self.dashboard_ok
        
        print(f"\n🚀 STATUS GERAL: {'✅ SISTEMA 100% FUNCIONAL' if tudo_ok else '❌ SISTEMA COM PROBLEMAS'}")
        
        if tudo_ok:
            print(f"\n🎉 PARABÉNS! SEU SISTEMA ESTÁ COMPLETAMENTE OPERACIONAL!")
            print(f"")
            print(f"🌐 ACESSE O DASHBOARD:")
            print(f"   URL: http://localhost:5000")
            print(f"   Usuário: sandro")
            print(f"   Senha: sandro2020")
            print(f"")
            print(f"🔗 APIS FREQTRADE DISPONÍVEIS:")
            for i in range(8081, 8088):
                print(f"   http://127.0.0.1:{i}/api/v1/ping")
            print(f"")
            print(f"💰 TRADING:")
            print(f"   Modo: DRY-RUN (Simulação segura)")
            print(f"   Estratégias: 7 rodando simultaneamente")
            print(f"   Monitoramento: 24/7 via dashboard")
            print(f"")
            print(f"🔄 PARA PARAR O SISTEMA:")
            print(f"   docker-compose -f docker-compose-simple.yml down")
        else:
            print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
            if self.containers_ok < 7:
                print(f"   - Containers: Execute 'docker-compose -f docker-compose-simple.yml up -d'")
            if self.apis_ok < 7:
                print(f"   - APIs: Aguarde inicialização ou reinicie containers")
            if not self.dashboard_ok:
                print(f"   - Dashboard: Execute 'python dashboard_simples_funcional.py'")
    
    def executar_verificacao_completa(self):
        """Executa verificação completa do sistema"""
        print("🚀 VERIFICAÇÃO COMPLETA DO SISTEMA FREQTRADE")
        print("=" * 60)
        print("Verificando todos os componentes...")
        print()
        
        # Verificações sequenciais
        containers_ok = self.verificar_containers()
        
        if containers_ok:
            apis_ok = self.verificar_apis_freqtrade()
            
            if apis_ok:
                # Iniciar dashboard em thread separada
                dashboard_thread = threading.Thread(target=self.iniciar_dashboard, daemon=True)
                dashboard_thread.start()
                
                # Verificar dashboard
                self.verificar_dashboard()
        
        # Mostrar resumo
        self.mostrar_resumo_final()
        
        # Se tudo estiver funcionando, manter dashboard rodando
        if self.containers_ok >= 7 and self.apis_ok >= 7 and self.dashboard_ok:
            print(f"\n🔄 Dashboard rodando... Pressione Ctrl+C para parar")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n👋 Sistema parado pelo usuário")

def main():
    """Função principal"""
    sistema = SistemaCompleto()
    sistema.executar_verificacao_completa()

if __name__ == "__main__":
    main()
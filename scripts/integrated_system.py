#!/usr/bin/env python3
"""
🔗 Sistema Integrado - FreqTrade Multi-Strategy
Conecta Telegram + Dashboard + Estratégias em um sistema único
"""

import os
import asyncio
import threading
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Importar componentes do sistema
from telegram_system_main import main as telegram_main
from dashboard_main import app as dashboard_app

# Configuração
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedSystem:
    """Sistema integrado completo"""
    
    def __init__(self):
        self.telegram_thread = None
        self.dashboard_thread = None
        self.running = False
        
    def start_telegram_system(self):
        """Iniciar sistema Telegram em thread separada"""
        def run_telegram():
            try:
                logger.info("🤖 Iniciando sistema Telegram...")
                telegram_main()
            except Exception as e:
                logger.error(f"❌ Erro no sistema Telegram: {e}")
        
        self.telegram_thread = threading.Thread(target=run_telegram, daemon=True)
        self.telegram_thread.start()
        logger.info("✅ Sistema Telegram iniciado em thread separada")
    
    def start_dashboard_system(self):
        """Iniciar dashboard web em thread separada"""
        def run_dashboard():
            try:
                logger.info("📊 Iniciando dashboard web...")
                dashboard_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"❌ Erro no dashboard: {e}")
        
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        logger.info("✅ Dashboard web iniciado em thread separada")
    
    def check_system_health(self):
        """Verificar saúde do sistema"""
        health_status = {
            'telegram': self.telegram_thread and self.telegram_thread.is_alive(),
            'dashboard': self.dashboard_thread and self.dashboard_thread.is_alive(),
            'timestamp': datetime.now().isoformat()
        }
        
        return health_status
    
    def start_complete_system(self):
        """Iniciar sistema completo"""
        logger.info("🚀 INICIANDO SISTEMA INTEGRADO COMPLETO")
        logger.info("=" * 60)
        
        # Verificar credenciais
        if not self._check_credentials():
            logger.error("❌ Credenciais não configuradas!")
            logger.error("Execute: python setup_credentials.py")
            return False
        
        # Iniciar componentes
        self.running = True
        
        try:
            # 1. Iniciar Dashboard Web
            logger.info("📊 Iniciando Dashboard Web...")
            self.start_dashboard_system()
            time.sleep(2)  # Aguardar inicialização
            
            # 2. Iniciar Sistema Telegram
            logger.info("🤖 Iniciando Sistema Telegram...")
            self.start_telegram_system()
            time.sleep(2)  # Aguardar inicialização
            
            # 3. Mostrar status
            self._show_startup_status()
            
            # 4. Loop principal de monitoramento
            self._main_monitoring_loop()
            
        except KeyboardInterrupt:
            logger.info("🛑 Sistema interrompido pelo usuário")
            self.stop_system()
        except Exception as e:
            logger.error(f"❌ Erro crítico no sistema: {e}")
            self.stop_system()
            return False
        
        return True
    
    def _check_credentials(self) -> bool:
        """Verificar se credenciais estão configuradas"""
        required_vars = ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value in ['YOUR_TELEGRAM_BOT_TOKEN_HERE', 'YOUR_TELEGRAM_CHAT_ID_HERE']:
                return False
        
        return True
    
    def _show_startup_status(self):
        """Mostrar status de inicialização"""
        time.sleep(3)  # Aguardar inicialização completa
        
        health = self.check_system_health()
        
        logger.info("📊 STATUS DO SISTEMA INTEGRADO")
        logger.info("=" * 60)
        logger.info(f"🤖 Telegram Bot: {'✅ Ativo' if health['telegram'] else '❌ Inativo'}")
        logger.info(f"📊 Dashboard Web: {'✅ Ativo' if health['dashboard'] else '❌ Inativo'}")
        logger.info("")
        logger.info("🌐 ACESSO AO SISTEMA:")
        logger.info("   📊 Dashboard Web: http://localhost:5000")
        logger.info("   🤖 Bot Telegram: Envie /start para seu bot")
        logger.info("")
        logger.info("🎯 FUNCIONALIDADES DISPONÍVEIS:")
        logger.info("   • 7 Estratégias de Trading")
        logger.info("   • Controle via Telegram")
        logger.info("   • Dashboard com Gráficos")
        logger.info("   • IA Preditiva")
        logger.info("   • Monitoramento 24/7")
        logger.info("")
        logger.info("🔐 MODO: DRY-RUN (Simulação)")
        logger.info("=" * 60)
    
    def _main_monitoring_loop(self):
        """Loop principal de monitoramento"""
        logger.info("🔄 Iniciando monitoramento do sistema...")
        
        while self.running:
            try:
                # Verificar saúde do sistema a cada 30 segundos
                time.sleep(30)
                
                health = self.check_system_health()
                
                # Log de status (apenas se houver problemas)
                if not health['telegram']:
                    logger.warning("⚠️ Sistema Telegram não está respondendo")
                
                if not health['dashboard']:
                    logger.warning("⚠️ Dashboard Web não está respondendo")
                
                # Se ambos falharam, tentar reiniciar
                if not health['telegram'] and not health['dashboard']:
                    logger.error("🚨 Ambos os sistemas falharam! Tentando reiniciar...")
                    self._restart_failed_systems()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
    
    def _restart_failed_systems(self):
        """Reiniciar sistemas que falharam"""
        health = self.check_system_health()
        
        if not health['telegram']:
            logger.info("🔄 Reiniciando sistema Telegram...")
            self.start_telegram_system()
        
        if not health['dashboard']:
            logger.info("🔄 Reiniciando dashboard web...")
            self.start_dashboard_system()
    
    def stop_system(self):
        """Parar sistema completo"""
        logger.info("🛑 Parando sistema integrado...")
        self.running = False
        
        # Aguardar threads terminarem
        if self.telegram_thread and self.telegram_thread.is_alive():
            logger.info("⏳ Aguardando sistema Telegram parar...")
        
        if self.dashboard_thread and self.dashboard_thread.is_alive():
            logger.info("⏳ Aguardando dashboard web parar...")
        
        logger.info("✅ Sistema integrado parado")

def show_system_info():
    """Mostrar informações do sistema"""
    print("🔗 SISTEMA INTEGRADO - FreqTrade Multi-Strategy")
    print("=" * 60)
    print()
    print("Este sistema integra todos os componentes:")
    print()
    print("🤖 TELEGRAM BOT:")
    print("   • Menu interativo completo")
    print("   • Comandos de trading manual")
    print("   • IA preditiva integrada")
    print("   • Monitoramento em tempo real")
    print()
    print("📊 DASHBOARD WEB:")
    print("   • Interface moderna com gráficos")
    print("   • Controles para estratégias")
    print("   • Visualização de indicadores")
    print("   • Estatísticas em tempo real")
    print()
    print("🏗️ ESTRATÉGIAS:")
    print("   • 7 estratégias validadas")
    print("   • Configurações otimizadas")
    print("   • Modo DRY-RUN seguro")
    print("   • Backup automático")
    print()
    print("🔐 SEGURANÇA:")
    print("   • Credenciais protegidas")
    print("   • Autenticação obrigatória")
    print("   • Logs de auditoria")
    print("   • Monitoramento de saúde")
    print()
    print("=" * 60)

def main():
    """Função principal"""
    show_system_info()
    
    # Verificar se credenciais estão configuradas
    if not os.getenv('TELEGRAM_TOKEN') or os.getenv('TELEGRAM_TOKEN') == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
        print("❌ CREDENCIAIS NÃO CONFIGURADAS!")
        print()
        print("🔧 CONFIGURE SUAS CREDENCIAIS PRIMEIRO:")
        print("   1. Execute: python setup_credentials.py")
        print("   2. Configure suas chaves reais")
        print("   3. Execute: python test_credentials.py")
        print("   4. Execute novamente este script")
        print()
        return
    
    # Inicializar sistema integrado
    system = IntegratedSystem()
    
    try:
        success = system.start_complete_system()
        
        if success:
            logger.info("🎉 Sistema integrado executado com sucesso!")
        else:
            logger.error("❌ Falha na execução do sistema integrado")
            
    except KeyboardInterrupt:
        logger.info("🛑 Sistema interrompido pelo usuário")
        system.stop_system()
    except Exception as e:
        logger.error(f"🚨 Erro crítico: {e}")
        system.stop_system()

if __name__ == "__main__":
    main()
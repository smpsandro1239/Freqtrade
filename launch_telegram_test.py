#!/usr/bin/env python3
"""
🚀 Lançador de Teste do Sistema Telegram
Testa o sistema com credenciais simuladas para demonstração
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_credentials():
    """Verificar se credenciais estão configuradas"""
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or token == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
        return False, "Token do Telegram não configurado"
    
    if not chat_id or chat_id == 'YOUR_TELEGRAM_CHAT_ID_HERE':
        return False, "Chat ID do Telegram não configurado"
    
    return True, "Credenciais OK"

def show_telegram_setup_guide():
    """Mostrar guia de configuração do Telegram"""
    print("🤖 GUIA DE CONFIGURAÇÃO DO TELEGRAM")
    print("=" * 50)
    print()
    print("Para receber mensagens no Telegram, você precisa:")
    print()
    print("1️⃣ CRIAR UM BOT:")
    print("   • Abra o Telegram")
    print("   • Procure por @BotFather")
    print("   • Envie /newbot")
    print("   • Siga as instruções")
    print("   • Copie o TOKEN fornecido")
    print()
    print("2️⃣ OBTER SEU CHAT ID:")
    print("   • Procure por @userinfobot")
    print("   • Envie /start")
    print("   • Copie o ID fornecido")
    print()
    print("3️⃣ CONFIGURAR NO SISTEMA:")
    print("   • Execute: python setup_credentials.py")
    print("   • Cole o TOKEN e CHAT ID")
    print()
    print("4️⃣ TESTAR:")
    print("   • Execute este script novamente")
    print("   • Você receberá mensagens no Telegram!")
    print()

def simulate_telegram_messages():
    """Simular mensagens que seriam enviadas ao Telegram"""
    print("📱 SIMULAÇÃO DE MENSAGENS TELEGRAM")
    print("=" * 50)
    print()
    print("🤖 As seguintes mensagens seriam enviadas ao seu Telegram:")
    print()
    
    # Mensagem de inicialização
    print("📨 MENSAGEM 1 - Inicialização:")
    print("─" * 30)
    print("🤖 SISTEMA TELEGRAM ATIVO!")
    print()
    print("✅ Bot principal inicializado")
    print("✅ Trading manual habilitado")
    print("✅ IA preditiva ativa")
    print("✅ Monitoramento 24/7")
    print()
    print("Digite /start para começar!")
    print()
    
    time.sleep(2)
    
    # Mensagem de status
    print("📨 MENSAGEM 2 - Status das Estratégias:")
    print("─" * 30)
    print("📊 STATUS DAS ESTRATÉGIAS")
    print()
    print("🟢 Sample Strategy A")
    print("   Status: RODANDO")
    print("   Descrição: RSI básico - 15m")
    print("   Container: ft-stratA")
    print("   API Port: 8081")
    print()
    print("🟢 WaveHyperNW Strategy")
    print("   Status: RODANDO")
    print("   Descrição: WaveTrend + Nadaraya-Watson - 5m")
    print("   Container: ft-waveHyperNW")
    print("   API Port: 8083")
    print()
    print("📈 RESUMO GERAL:")
    print("• Estratégias Ativas: 7/7")
    print("• Sistema: 🟢 Operacional")
    print("• Modo: 🟡 DRY-RUN (Simulação)")
    print("• Última Verificação: " + datetime.now().strftime('%H:%M:%S'))
    print()
    
    time.sleep(2)
    
    # Mensagem de IA preditiva
    print("📨 MENSAGEM 3 - IA Preditiva:")
    print("─" * 30)
    print("🔮 PREVISÕES RÁPIDAS - IA")
    print()
    print("🔥 TOP OPORTUNIDADES:")
    print("1. 🟢 BTC/USDT - 78% (ALTA)")
    print("2. 🟢 ETH/USDT - 72% (ALTA)")
    print("3. 🔴 ADA/USDT - 68% (BAIXA)")
    print()
    print("📊 RESUMO:")
    print("• Pares Analisados: 10")
    print("• Alta Confiança: 3")
    print("• Timestamp: " + datetime.now().strftime('%H:%M:%S'))
    print()
    print("💡 Use /predict <PAR> para análise detalhada")
    print()
    
    time.sleep(2)
    
    # Mensagem de estatísticas
    print("📨 MENSAGEM 4 - Estatísticas:")
    print("─" * 30)
    print("📈 ESTATÍSTICAS DETALHADAS")
    print()
    print("📊 Sample Strategy A")
    print("   Trades: 5")
    print("   🟢 P&L: 2.5 USDT")
    print("   Win Rate: 80.0%")
    print()
    print("📊 WaveHyperNW Strategy")
    print("   Trades: 12")
    print("   🟢 P&L: 5.8 USDT")
    print("   Win Rate: 75.0%")
    print()
    print("🎯 RESUMO GERAL:")
    print("• Total Trades: 45")
    print("• Lucro Total: 24.7 USDT")
    print("• Win Rate Médio: 78.5%")
    print("• Período: Últimas 24h")
    print("• Modo: DRY-RUN (Simulação)")
    print()

def simulate_telegram_commands():
    """Simular comandos disponíveis no Telegram"""
    print("🎮 COMANDOS DISPONÍVEIS NO TELEGRAM")
    print("=" * 50)
    print()
    print("📱 COMANDOS BÁSICOS:")
    print("   /start - Menu principal interativo")
    print("   /status - Status de todas as estratégias")
    print("   /stats - Estatísticas detalhadas")
    print("   /help - Ajuda completa")
    print()
    print("💰 TRADING MANUAL:")
    print("   /forcebuy stratA BTC/USDT - Compra forçada")
    print("   /forcesell stratA BTC/USDT - Venda forçada")
    print("   /adjust stratA aggressive - Modo agressivo")
    print("   /emergency - Parada de emergência")
    print()
    print("🔮 IA PREDITIVA:")
    print("   /predict - Previsões rápidas")
    print("   /predict BTC/USDT - Análise específica")
    print("   /ai_analysis - Análise completa")
    print("   /opportunities - Oportunidades de alta confiança")
    print()
    print("⚙️ CONTROLE DE ESTRATÉGIAS:")
    print("   /start_strategy stratA - Iniciar estratégia")
    print("   /stop_strategy stratA - Parar estratégia")
    print("   /restart_strategy stratA - Reiniciar estratégia")
    print()

def launch_dashboard_demo():
    """Lançar dashboard em modo demo"""
    print("📊 LANÇANDO DASHBOARD WEB...")
    print("=" * 50)
    print()
    print("🌐 Dashboard disponível em: http://localhost:5000")
    print("👤 Login: admin")
    print("🔑 Senha: admin123")
    print()
    print("🔄 Iniciando servidor Flask...")
    
    try:
        # Configurar variáveis de ambiente para demo
        os.environ['DASHBOARD_USERNAME'] = 'admin'
        os.environ['DASHBOARD_PASSWORD'] = 'admin123'
        os.environ['DASHBOARD_SECRET_KEY'] = 'demo-secret-key-for-testing'
        
        # Importar e executar dashboard em thread separada
        def run_dashboard():
            try:
                from scripts.dashboard_main import app
                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Erro no dashboard: {e}")
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        print("✅ Dashboard iniciado com sucesso!")
        print("🌐 Acesse: http://localhost:5000")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 LANÇADOR DE TESTE - FREQTRADE MULTI-STRATEGY")
    print("=" * 60)
    print()
    print("Este script testa o sistema e mostra o que você receberia no Telegram")
    print()
    
    # Verificar credenciais
    has_credentials, message = check_credentials()
    
    if not has_credentials:
        print("⚠️  CREDENCIAIS NÃO CONFIGURADAS")
        print("=" * 50)
        print(f"❌ {message}")
        print()
        show_telegram_setup_guide()
        
        print("🎮 DEMONSTRAÇÃO DO SISTEMA")
        print("=" * 50)
        print("Como você ainda não tem credenciais configuradas,")
        print("vou mostrar uma simulação do que aconteceria:")
        print()
        
        # Simular mensagens
        simulate_telegram_messages()
        simulate_telegram_commands()
        
        # Lançar dashboard demo
        print("📊 LANÇANDO DASHBOARD DEMO")
        print("=" * 50)
        if launch_dashboard_demo():
            print()
            print("🎉 SISTEMA DEMO ATIVO!")
            print("=" * 50)
            print("🌐 Dashboard: http://localhost:5000 (admin/admin123)")
            print("📱 Telegram: Configure suas credenciais para usar")
            print()
            print("🔄 Pressione Ctrl+C para parar")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Sistema parado pelo usuário")
        
    else:
        print("✅ CREDENCIAIS CONFIGURADAS!")
        print("=" * 50)
        print(f"✅ {message}")
        print()
        print("🚀 INICIANDO SISTEMA COMPLETO...")
        print()
        
        # Lançar dashboard
        print("📊 Iniciando Dashboard Web...")
        dashboard_success = launch_dashboard_demo()
        
        if dashboard_success:
            print("✅ Dashboard ativo em http://localhost:5000")
        
        # Tentar lançar sistema Telegram
        print("🤖 Iniciando Sistema Telegram...")
        try:
            from scripts.telegram_system_main import main as telegram_main
            
            # Executar em thread separada
            def run_telegram():
                try:
                    telegram_main()
                except Exception as e:
                    logger.error(f"Erro no Telegram: {e}")
            
            telegram_thread = threading.Thread(target=run_telegram, daemon=True)
            telegram_thread.start()
            
            print("✅ Sistema Telegram iniciado!")
            print()
            print("🎉 SISTEMA COMPLETO ATIVO!")
            print("=" * 50)
            print("🌐 Dashboard: http://localhost:5000")
            print("🤖 Telegram: Envie /start para seu bot")
            print()
            print("📱 Você deve receber uma mensagem no Telegram agora!")
            print("🔄 Pressione Ctrl+C para parar")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Sistema parado pelo usuário")
                
        except Exception as e:
            print(f"❌ Erro ao iniciar sistema Telegram: {e}")
            print("💡 Verifique suas credenciais com: python test_credentials.py")

if __name__ == "__main__":
    main()
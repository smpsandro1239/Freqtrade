#!/usr/bin/env python3
"""
Script de Inicialização do Dashboard
Inicia o dashboard web com todas as funcionalidades
"""
import os
import subprocess
import sys
import time
from pathlib import Path


def check_requirements():
    """Verificar se todos os requisitos estão instalados"""
    print("🔍 Verificando requisitos...")

    required_packages = [
        "flask",
        "flask-cors",
        "flask-limiter",
        "pandas",
        "numpy",
        "redis",
        "PyJWT",
        "python-telegram-bot",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Pacotes ausentes: {missing_packages}")
        print("💡 Instale com: pip install " + " ".join(missing_packages))
        return False

    print("✅ Todos os requisitos estão instalados")
    return True


def check_env_file():
    """Verificar arquivo .env"""
    print("🔐 Verificando arquivo .env...")

    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado")

        # Copiar do exemplo
        example_file = Path(".env.example")
        if example_file.exists():
            print("📋 Copiando .env.example para .env...")
            with open(example_file, "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
            print("✅ Arquivo .env criado")
        else:
            print("❌ .env.example também não encontrado")
            return False

    # Verificar variáveis essenciais
    with open(env_file, "r") as f:
        env_content = f.read()

    required_vars = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = []

    for var in required_vars:
        if var not in env_content or f"{var}=xxx" in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️ Configure estas variáveis no .env: {missing_vars}")
        print("💡 Edite o arquivo .env com suas credenciais reais")

    print("✅ Arquivo .env verificado")
    return True


def start_dashboard():
    """Iniciar o dashboard"""
    print("🚀 Iniciando Dashboard Web...")

    # Verificar se a porta 5000 está livre
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 5000))
    sock.close()

    if result == 0:
        print("⚠️ Porta 5000 já está em uso")
        print("💡 Pare outros serviços na porta 5000 ou altere a porta no código")
        return False

    # Iniciar o dashboard
    dashboard_script = Path("scripts/dashboard_api.py")
    if not dashboard_script.exists():
        print("❌ Script dashboard_api.py não encontrado")
        return False

    print("🌐 Dashboard será acessível em: http://localhost:5000")
    print("👤 Login padrão: admin / admin123")
    print("🔒 ALTERE A SENHA PADRÃO EM PRODUÇÃO!")
    print("")
    print("📊 Funcionalidades disponíveis:")
    print("   • Gráficos multi-timeframe (1m, 5m, 15m, 1h, 4h, 1d)")
    print("   • Indicadores técnicos (RSI, MACD, EMAs, Bollinger Bands)")
    print("   • Estatísticas de trading em tempo real")
    print("   • Histórico de trades")
    print("   • Auto-refresh automático")
    print("")
    print("⏹️ Pressione Ctrl+C para parar")
    print("=" * 60)

    try:
        # Executar o dashboard
        os.chdir("scripts")
        subprocess.run([sys.executable, "dashboard_api.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")
        return False

    return True


def main():
    """Função principal"""
    print("🎯 FREQTRADE DASHBOARD - INICIALIZAÇÃO")
    print("=" * 50)

    # Verificações
    if not check_requirements():
        return False

    if not check_env_file():
        return False

    # Iniciar dashboard
    return start_dashboard()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

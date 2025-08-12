#!/usr/bin/env python3
"""
Teste do Sistema Completo via Docker
Verifica se todas as estratégias funcionam no ambiente Docker
"""
import json
import subprocess
import time
from pathlib import Path


def run_command(cmd, timeout=30):
    """Executar comando com timeout"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def check_docker():
    """Verificar se Docker está disponível"""
    print("🐳 Verificando Docker...")
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker disponível: {stdout.strip()}")
        return True
    else:
        print(f"❌ Docker não disponível: {stderr}")
        return False

def check_docker_compose():
    """Verificar se docker-compose está disponível"""
    print("🐳 Verificando docker-compose...")
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print(f"✅ docker-compose disponível: {stdout.strip()}")
        return True
    else:
        print(f"❌ docker-compose não disponível: {stderr}")
        return False

def validate_configs():
    """Validar arquivos de configuração"""
    print("\n📋 Validando configurações...")

    config_dir = Path("user_data/configs")
    configs = list(config_dir.glob("*.json"))

    valid_configs = 0
    total_configs = len(configs)

    for config_file in configs:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Verificar campos obrigatórios
            required_fields = ['stake_currency', 'stake_amount', 'dry_run', 'exchange']
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                print(f"❌ {config_file.name}: Campos ausentes: {missing_fields}")
            else:
                print(f"✅ {config_file.name}: Configuração válida")
                valid_configs += 1

        except json.JSONDecodeError as e:
            print(f"❌ {config_file.name}: JSON inválido: {e}")
        except Exception as e:
            print(f"❌ {config_file.name}: Erro: {e}")

    print(f"\n📊 Configurações: {valid_configs}/{total_configs} válidas")
    return valid_configs == total_configs

def test_docker_build():
    """Testar build das imagens Docker"""
    print("\n🔨 Testando build das imagens...")

    # Testar build da imagem ML
    print("🤖 Testando build da imagem ML...")
    success, stdout, stderr = run_command(
        "docker build -f scripts/Dockerfile.ml -t freqtrade-ml .",
        timeout=300
    )

    if success:
        print("✅ Imagem ML construída com sucesso")
    else:
        print(f"❌ Erro no build ML: {stderr}")
        return False

    # Testar build das outras imagens
    images_to_build = [
        ("scripts/Dockerfile", "freqtrade-telegram"),
        ("scripts/Dockerfile.monitor", "freqtrade-monitor"),
        ("scripts/Dockerfile.risk", "freqtrade-risk"),
        ("scripts/Dockerfile.commander", "freqtrade-commander")
    ]

    for dockerfile, tag in images_to_build:
        if Path(dockerfile).exists():
            print(f"🔨 Testando build: {tag}...")
            success, stdout, stderr = run_command(
                f"docker build -f {dockerfile} -t {tag} .",
                timeout=180
            )

            if success:
                print(f"✅ {tag} construída com sucesso")
            else:
                print(f"❌ Erro no build {tag}: {stderr}")
                return False

    return True

def test_syntax_validation():
    """Testar validação de sintaxe"""
    print("\n🔍 Testando validação de sintaxe...")

    success, stdout, stderr = run_command("python scripts/syntax_validator.py")

    if success:
        print("✅ Todas as estratégias têm sintaxe válida")
        return True
    else:
        print(f"❌ Problemas de sintaxe encontrados:")
        print(stderr)
        return False

def check_env_file():
    """Verificar arquivo .env"""
    print("\n🔐 Verificando arquivo .env...")

    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado - usando .env.example")

        example_file = Path(".env.example")
        if example_file.exists():
            print("📋 Copiando .env.example para .env...")
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Arquivo .env criado")
        else:
            print("❌ .env.example também não encontrado")
            return False

    # Verificar conteúdo do .env
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()

        required_vars = ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID', 'EXCHANGE_NAME']
        missing_vars = []

        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)

        if missing_vars:
            print(f"⚠️ Variáveis ausentes no .env: {missing_vars}")
            print("💡 Configure essas variáveis antes de usar em produção")
        else:
            print("✅ Arquivo .env contém variáveis necessárias")

        return True

    except Exception as e:
        print(f"❌ Erro ao ler .env: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DO SISTEMA FREQTRADE MULTI-STRATEGY")
    print("=" * 70)

    tests_passed = 0
    total_tests = 6

    # Teste 1: Docker
    if check_docker():
        tests_passed += 1

    # Teste 2: Docker Compose
    if check_docker_compose():
        tests_passed += 1

    # Teste 3: Configurações
    if validate_configs():
        tests_passed += 1

    # Teste 4: Arquivo .env
    if check_env_file():
        tests_passed += 1

    # Teste 5: Sintaxe
    if test_syntax_validation():
        tests_passed += 1

    # Teste 6: Build Docker (opcional - pode ser lento)
    print(f"\n🤔 Deseja testar o build das imagens Docker? (pode demorar alguns minutos)")
    print("Digite 'y' para sim ou qualquer tecla para pular:")

    try:
        user_input = input().lower().strip()
        if user_input == 'y':
            if test_docker_build():
                tests_passed += 1
        else:
            print("⏭️ Pulando teste de build Docker")
            total_tests -= 1
    except KeyboardInterrupt:
        print("\n⏭️ Pulando teste de build Docker")
        total_tests -= 1

    # Resumo final
    print(f"\n📊 RESUMO FINAL")
    print("=" * 50)
    print(f"✅ Testes passaram: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("\n🎉 SISTEMA PRONTO PARA USO!")
        print("💡 Execute 'docker-compose up -d' para iniciar")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} TESTES FALHARAM")
        print("🔧 Corrija os problemas antes de usar o sistema")

    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Verificação Completa do Setup - Freqtrade Multi-Strategy
Verifica se todos os arquivos necessários estão presentes e corretos
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


class SetupVerifier:
    """Verificador completo do setup"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def check_file_exists(self, file_path: str, description: str) -> bool:
        """Verificar se arquivo existe"""
        self.total_checks += 1
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
            self.success_count += 1
            return True
        else:
            error_msg = f"❌ {description}: {file_path} NÃO ENCONTRADO"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def check_json_valid(self, file_path: str, description: str) -> bool:
        """Verificar se JSON é válido"""
        self.total_checks += 1
        try:
            with open(file_path, "r") as f:
                json.load(f)
            print(f"✅ {description}: JSON válido")
            self.success_count += 1
            return True
        except json.JSONDecodeError as e:
            error_msg = f"❌ {description}: JSON inválido - {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
        except FileNotFoundError:
            error_msg = f"❌ {description}: Arquivo não encontrado"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def verify_strategies(self) -> bool:
        """Verificar todas as estratégias"""
        print("\n🎯 VERIFICANDO ESTRATÉGIAS")
        print("=" * 50)

        strategies = [
            ("SampleStrategyA", "user_data/strategies/SampleStrategyA.py"),
            ("SampleStrategyB", "user_data/strategies/SampleStrategyB.py"),
            ("WaveHyperNWStrategy", "user_data/strategies/WaveHyperNWStrategy.py"),
            ("MLStrategy", "user_data/strategies/MLStrategy.py"),
            ("MLStrategySimple", "user_data/strategies/MLStrategySimple.py"),
            (
                "MultiTimeframeStrategy",
                "user_data/strategies/MultiTimeframeStrategy.py",
            ),
            ("WaveHyperNWEnhanced", "user_data/strategies/WaveHyperNWEnhanced.py"),
        ]

        all_present = True
        for name, path in strategies:
            if not self.check_file_exists(path, f"Estratégia {name}"):
                all_present = False

        return all_present

    def verify_configs(self) -> bool:
        """Verificar todas as configurações"""
        print("\n⚙️ VERIFICANDO CONFIGURAÇÕES")
        print("=" * 50)

        configs = [
            ("stratA", "user_data/configs/stratA.json"),
            ("stratB", "user_data/configs/stratB.json"),
            ("waveHyperNW", "user_data/configs/waveHyperNW.json"),
            ("mlStrategy", "user_data/configs/mlStrategy.json"),
            ("mlStrategySimple", "user_data/configs/mlStrategySimple.json"),
            ("multiTimeframe", "user_data/configs/multiTimeframe.json"),
            ("waveHyperNWEnhanced", "user_data/configs/waveHyperNWEnhanced.json"),
        ]

        all_valid = True
        for name, path in configs:
            if self.check_file_exists(path, f"Config {name}"):
                if not self.check_json_valid(path, f"Config {name}"):
                    all_valid = False
            else:
                all_valid = False

        return all_valid

    def verify_docker_files(self) -> bool:
        """Verificar arquivos Docker"""
        print("\n🐳 VERIFICANDO ARQUIVOS DOCKER")
        print("=" * 50)

        docker_files = [
            ("docker-compose.yml", "Docker Compose principal"),
            ("scripts/Dockerfile", "Dockerfile Telegram Bot"),
            ("scripts/Dockerfile.ml", "Dockerfile ML Strategy"),
            ("scripts/Dockerfile.monitor", "Dockerfile Health Monitor"),
            ("scripts/Dockerfile.risk", "Dockerfile Risk Manager"),
            ("scripts/Dockerfile.commander", "Dockerfile Telegram Commander"),
        ]

        all_present = True
        for path, description in docker_files:
            if not self.check_file_exists(path, description):
                all_present = False

        return all_present

    def verify_scripts(self) -> bool:
        """Verificar scripts essenciais"""
        print("\n📜 VERIFICANDO SCRIPTS")
        print("=" * 50)

        scripts = [
            ("scripts/telegram_bot.py", "Bot Telegram principal"),
            ("scripts/health_monitor.py", "Monitor de saúde"),
            ("scripts/risk_manager.py", "Gerenciador de risco"),
            ("scripts/telegram_commander.py", "Comandante Telegram"),
            ("scripts/syntax_validator.py", "Validador de sintaxe"),
            ("scripts/strategy_validator.py", "Validador de estratégias"),
            ("run.ps1", "Script PowerShell principal"),
        ]

        all_present = True
        for path, description in scripts:
            if not self.check_file_exists(path, description):
                all_present = False

        return all_present

    def verify_env_setup(self) -> bool:
        """Verificar configuração de ambiente"""
        print("\n🔐 VERIFICANDO CONFIGURAÇÃO DE AMBIENTE")
        print("=" * 50)

        # Verificar .env.example
        if self.check_file_exists(".env.example", "Template de ambiente"):
            # Verificar se .env existe
            if Path(".env").exists():
                print("✅ Arquivo .env: Presente")
                self.success_count += 1
            else:
                warning_msg = (
                    "⚠️ Arquivo .env: Não encontrado (será criado automaticamente)"
                )
                print(warning_msg)
                self.warnings.append(warning_msg)
            self.total_checks += 1
            return True
        else:
            return False

    def verify_documentation(self) -> bool:
        """Verificar documentação"""
        print("\n📚 VERIFICANDO DOCUMENTAÇÃO")
        print("=" * 50)

        docs = [
            ("README.md", "Documentação principal"),
            ("COMO_EXECUTAR.md", "Guia de execução"),
            ("INSTALACAO_WINDOWS.md", "Guia de instalação Windows"),
            ("SEGURANCA.md", "Guia de segurança"),
            ("TELEGRAM_COMANDOS.md", "Comandos Telegram"),
            ("DEVELOPMENT_PLAN.md", "Plano de desenvolvimento"),
            ("MELHORIAS_IMPLEMENTADAS.md", "Resumo das melhorias"),
        ]

        all_present = True
        for path, description in docs:
            if not self.check_file_exists(path, description):
                all_present = False

        return all_present

    def verify_test_files(self) -> bool:
        """Verificar arquivos de teste"""
        print("\n🧪 VERIFICANDO ARQUIVOS DE TESTE")
        print("=" * 50)

        tests = [
            ("test_all_strategies.py", "Teste de todas as estratégias"),
            ("test_docker_system.py", "Teste do sistema Docker"),
            ("test_ml_simple.py", "Teste ML Strategy Simple"),
            ("test_wave_enhanced.py", "Teste Wave Enhanced"),
            ("test_multi_timeframe.py", "Teste Multi Timeframe"),
        ]

        all_present = True
        for path, description in tests:
            if not self.check_file_exists(path, description):
                all_present = False

        return all_present

    def verify_docker_compose_config(self) -> bool:
        """Verificar configuração do docker-compose"""
        print("\n🔧 VERIFICANDO CONFIGURAÇÃO DOCKER-COMPOSE")
        print("=" * 50)

        if not Path("docker-compose.yml").exists():
            return False

        try:
            with open("docker-compose.yml", "r") as f:
                content = f.read()

            # Verificar se todas as estratégias estão no docker-compose
            required_services = [
                "stratA",
                "stratB",
                "waveHyperNW",
                "mlStrategy",
                "multiTimeframe",
                "waveEnhanced",
                "telegram_bot",
                "health_monitor",
                "risk_manager",
                "telegram_commander",
            ]

            missing_services = []
            for service in required_services:
                if service not in content:
                    missing_services.append(service)

            if missing_services:
                error_msg = (
                    f"❌ Serviços ausentes no docker-compose: {missing_services}"
                )
                print(error_msg)
                self.errors.append(error_msg)
                return False
            else:
                print("✅ Docker-compose: Todos os serviços presentes")
                self.success_count += 1
                self.total_checks += 1
                return True

        except Exception as e:
            error_msg = f"❌ Erro ao verificar docker-compose: {e}"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def print_summary(self):
        """Imprimir resumo final"""
        print(f"\n📊 RESUMO DA VERIFICAÇÃO")
        print("=" * 60)
        print(
            f"✅ Verificações bem-sucedidas: {self.success_count}/{self.total_checks}"
        )
        print(f"❌ Erros encontrados: {len(self.errors)}")
        print(f"⚠️ Avisos: {len(self.warnings)}")

        if self.errors:
            print(f"\n🚨 ERROS CRÍTICOS:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️ AVISOS:")
            for warning in self.warnings:
                print(f"   • {warning}")

        success_rate = (
            (self.success_count / self.total_checks) * 100
            if self.total_checks > 0
            else 0
        )

        if success_rate >= 95:
            print(f"\n🎉 SISTEMA COMPLETO E PRONTO PARA USO! ({success_rate:.1f}%)")
            return True
        elif success_rate >= 80:
            print(
                f"\n⚠️ SISTEMA QUASE COMPLETO ({success_rate:.1f}%) - Corrija os erros críticos"
            )
            return False
        else:
            print(
                f"\n❌ SISTEMA INCOMPLETO ({success_rate:.1f}%) - Muitos arquivos ausentes"
            )
            return False


def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA DO SETUP - FREQTRADE MULTI-STRATEGY")
    print("=" * 70)

    verifier = SetupVerifier()

    # Executar todas as verificações
    results = []
    results.append(verifier.verify_strategies())
    results.append(verifier.verify_configs())
    results.append(verifier.verify_docker_files())
    results.append(verifier.verify_scripts())
    results.append(verifier.verify_env_setup())
    results.append(verifier.verify_documentation())
    results.append(verifier.verify_test_files())
    results.append(verifier.verify_docker_compose_config())

    # Resumo final
    system_ready = verifier.print_summary()

    if system_ready:
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Configure suas credenciais no arquivo .env")
        print("   2. Execute: docker-compose up -d")
        print("   3. Monitore: docker-compose logs -f")
        print("   4. Controle via Telegram ou PowerShell")

    return system_ready


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

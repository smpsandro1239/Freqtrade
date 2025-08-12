#!/usr/bin/env python3
"""
Syntax Validator - Validador de Sintaxe para Estratégias Freqtrade
Verifica sintaxe Python e estrutura básica sem dependências externas
"""
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class StrategyValidator:
    """Validador de sintaxe e estrutura para estratégias Freqtrade"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.required_methods = [
            "populate_indicators",
            "populate_entry_trend",
            "populate_exit_trend",
        ]
        self.required_attributes = ["INTERFACE_VERSION", "timeframe", "stoploss"]

    def validate_syntax(self, file_path: str) -> bool:
        """Valida sintaxe Python básica"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Compilar para verificar sintaxe
            ast.parse(content)
            print(f"✅ Sintaxe válida: {file_path}")
            return True

        except SyntaxError as e:
            error_msg = f"❌ Erro de sintaxe em {file_path}:{e.lineno}: {e.msg}"
            print(error_msg)
            self.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ Erro ao ler {file_path}: {str(e)}"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def validate_strategy_structure(self, file_path: str) -> bool:
        """Valida estrutura específica de estratégia Freqtrade via AST"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Encontrar classes que herdam de IStrategy
            strategy_classes = []
            class_methods = {}
            class_attributes = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar se herda de IStrategy
                    inherits_istrategy = any(
                        (isinstance(base, ast.Name) and base.id == "IStrategy")
                        or (
                            isinstance(base, ast.Attribute) and base.attr == "IStrategy"
                        )
                        for base in node.bases
                    )

                    if inherits_istrategy:
                        strategy_classes.append(node.name)

                        # Coletar métodos da classe
                        methods = []
                        attributes = []

                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                methods.append(item.name)
                            elif isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        attributes.append(target.id)

                        class_methods[node.name] = methods
                        class_attributes[node.name] = attributes

            if not strategy_classes:
                error_msg = f"❌ Nenhuma classe de estratégia encontrada em {file_path}"
                print(error_msg)
                self.errors.append(error_msg)
                return False

            # Validar cada classe de estratégia encontrada
            for class_name in strategy_classes:
                methods = class_methods[class_name]
                attributes = class_attributes[class_name]

                # Verificar métodos obrigatórios
                missing_methods = [m for m in self.required_methods if m not in methods]
                if missing_methods:
                    warning_msg = f"⚠️ Métodos recomendados ausentes em {class_name}: {missing_methods}"
                    print(warning_msg)
                    self.warnings.append(warning_msg)

                # Verificar atributos obrigatórios
                missing_attrs = [
                    a for a in self.required_attributes if a not in attributes
                ]
                if missing_attrs:
                    warning_msg = f"⚠️ Atributos recomendados ausentes em {class_name}: {missing_attrs}"
                    print(warning_msg)
                    self.warnings.append(warning_msg)

            print(
                f"✅ Estrutura válida: {file_path} (classes: {', '.join(strategy_classes)})"
            )
            return True

        except Exception as e:
            error_msg = f"❌ Erro ao validar estrutura de {file_path}: {str(e)}"
            print(error_msg)
            self.errors.append(error_msg)
            return False

    def validate_file(self, file_path: str) -> bool:
        """Valida um arquivo completamente"""
        print(f"\n🔍 Validando: {file_path}")

        syntax_ok = self.validate_syntax(file_path)
        if not syntax_ok:
            return False

        structure_ok = self.validate_strategy_structure(file_path)
        return structure_ok

    def validate_directory(self, directory: str) -> Dict[str, bool]:
        """Valida todas as estratégias em um diretório"""
        results = {}
        strategy_dir = Path(directory)

        if not strategy_dir.exists():
            print(f"❌ Diretório não encontrado: {directory}")
            return results

        python_files = list(strategy_dir.glob("*.py"))
        if not python_files:
            print(f"⚠️ Nenhum arquivo .py encontrado em {directory}")
            return results

        print(f"\n📁 Validando diretório: {directory}")
        print(f"📄 Arquivos encontrados: {len(python_files)}")

        for file_path in python_files:
            # Pular arquivos especiais
            if file_path.name.startswith("__"):
                continue

            results[str(file_path)] = self.validate_file(str(file_path))

        return results

    def print_summary(self, results: Dict[str, bool]):
        """Imprime resumo da validação"""
        total = len(results)
        valid = sum(1 for v in results.values() if v)
        invalid = total - valid

        print(f"\n📊 RESUMO DA VALIDAÇÃO")
        print(f"{'='*50}")
        print(f"📄 Total de arquivos: {total}")
        print(f"✅ Válidos: {valid}")
        print(f"❌ Inválidos: {invalid}")

        if invalid > 0:
            print(f"\n❌ ARQUIVOS COM PROBLEMAS:")
            for file_path, is_valid in results.items():
                if not is_valid:
                    print(f"   • {Path(file_path).name}")

        if self.errors:
            print(f"\n🚨 ERROS ENCONTRADOS:")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️ AVISOS:")
            for warning in self.warnings:
                print(f"   • {warning}")

        return invalid == 0


def main():
    """Função principal"""
    validator = StrategyValidator()

    # Diretório padrão de estratégias
    strategies_dir = "user_data/strategies"

    # Permitir especificar diretório via argumento
    if len(sys.argv) > 1:
        strategies_dir = sys.argv[1]

    print("VALIDADOR DE SINTAXE - FREQTRADE STRATEGIES")
    print("=" * 60)

    # Validar todas as estratégias
    results = validator.validate_directory(strategies_dir)

    # Imprimir resumo
    all_valid = validator.print_summary(results)

    # Exit code baseado no resultado (apenas erros críticos)
    has_critical_errors = len(validator.errors) > 0
    sys.exit(0 if not has_critical_errors else 1)


if __name__ == "__main__":
    main()

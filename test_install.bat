@echo off
chcp 65001 >nul

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🧪 TESTE DE INSTALAÇÃO                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 Verificando pré-requisitos instalados...
echo.

:: Testar Docker
echo 🐳 Docker:
docker --version 2>nul
if %errorLevel% equ 0 (
    echo ✅ Docker instalado
    
    :: Testar se está rodando
    docker ps >nul 2>&1
    if %errorLevel% equ 0 (
        echo ✅ Docker está rodando
    ) else (
        echo ⚠️  Docker instalado mas não está rodando
    )
) else (
    echo ❌ Docker não encontrado
)

echo.

:: Testar Git
echo 📦 Git:
git --version 2>nul
if %errorLevel% equ 0 (
    echo ✅ Git instalado
) else (
    echo ❌ Git não encontrado
)

echo.

:: Testar Python (opcional)
echo 🐍 Python:
python --version 2>nul
if %errorLevel% equ 0 (
    echo ✅ Python instalado
) else (
    echo ⚠️  Python não encontrado (opcional)
)

echo.

:: Testar Chocolatey
echo 📦 Chocolatey:
choco --version 2>nul
if %errorLevel% equ 0 (
    echo ✅ Chocolatey instalado
) else (
    echo ⚠️  Chocolatey não encontrado
)

echo.

:: Verificar arquivos do projeto
echo 📁 Arquivos do projeto:
if exist "docker-compose.yml" (
    echo ✅ docker-compose.yml encontrado
) else (
    echo ❌ docker-compose.yml não encontrado
)

if exist ".env" (
    echo ✅ .env configurado
) else if exist ".env.example" (
    echo ⚠️  .env.example encontrado (precisa configurar)
) else (
    echo ❌ Arquivos de configuração não encontrados
)

if exist "user_data\strategies" (
    echo ✅ Estratégias encontradas
) else (
    echo ❌ Pasta de estratégias não encontrada
)

echo.

:: Testar containers se Docker estiver rodando
docker ps >nul 2>&1
if %errorLevel% equ 0 (
    echo 🐳 Status dos containers:
    docker-compose ps 2>nul
    if %errorLevel% neq 0 (
        echo ⚠️  Containers não iniciados (execute: docker-compose up -d)
    )
) else (
    echo ⚠️  Não é possível verificar containers (Docker não está rodando)
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            📋 RESUMO                                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

docker --version >nul 2>&1 && git --version >nul 2>&1 && exist "docker-compose.yml"
if %errorLevel% equ 0 (
    echo ✅ Sistema pronto para uso!
    echo.
    echo 💡 Próximos passos:
    echo 1. Configure o .env se ainda não fez
    echo 2. Execute: docker-compose up -d
    echo 3. Use start.bat para controlar o sistema
) else (
    echo ❌ Sistema não está completamente configurado
    echo.
    echo 💡 Execute a instalação:
    echo 1. Use start.bat opção 1 (Instalação Completa)
    echo 2. Ou execute install_auto.bat diretamente
)

echo.
pause
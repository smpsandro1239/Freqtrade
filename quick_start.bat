@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE QUICK START
:: Para usuários que já têm Docker e Git instalados
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        ⚡ FREQTRADE QUICK START                              ║
echo ║                                                                              ║
echo ║  Para usuários que já possuem Docker e Git                                  ║
echo ║  Setup rápido em menos de 2 minutos                                         ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar pré-requisitos
echo 🔍 Verificando pré-requisitos...

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker não encontrado
    echo 💡 Execute setup_freqtrade.bat para instalação completa
    pause
    exit /b 1
)

git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Git não encontrado
    echo 💡 Execute setup_freqtrade.bat para instalação completa
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker não está rodando
    echo 💡 Inicie o Docker Desktop e tente novamente
    pause
    exit /b 1
)

echo ✅ Pré-requisitos OK

:: Clonar ou atualizar
if exist "Freqtrade-MultiStrategy" (
    echo 📁 Atualizando projeto...
    cd Freqtrade-MultiStrategy
    git pull origin main
) else (
    echo 📥 Clonando projeto...
    git clone https://github.com/smpsandro1239/Freqtrade.git Freqtrade-MultiStrategy
    cd Freqtrade-MultiStrategy
)

:: Configurar rapidamente
if not exist ".env" (
    echo ⚙️ Configuração rápida...
    copy ".env.example" ".env"
    
    echo.
    echo 🤖 CONFIGURAÇÃO TELEGRAM:
    set /p "token=Token do bot: "
    set /p "chat=Chat ID: "
    
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_TOKEN=.*', 'TELEGRAM_TOKEN=!token!' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', 'TELEGRAM_CHAT_ID=!chat!' | Set-Content .env"
    
    echo ✅ Configurado
)

:: Iniciar
echo 🚀 Iniciando sistema...
docker-compose up -d --build

echo.
echo ✅ Sistema iniciado!
echo.
echo 💡 Comandos úteis:
echo • Ver status: docker-compose ps
echo • Ver logs: docker-compose logs -f
echo • Parar: docker-compose down
echo.

pause
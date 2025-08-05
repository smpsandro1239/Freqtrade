@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE VPS SETUP SCRIPT
:: Setup automatizado para VPS/Servidor Windows
:: Configuração silenciosa com parâmetros via linha de comando
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                      🖥️  FREQTRADE VPS SETUP                                ║
echo ║                                                                              ║
echo ║  Setup automatizado para VPS/Servidor Windows                               ║
echo ║  Uso: setup_vps.bat [TELEGRAM_TOKEN] [CHAT_ID] [EXCHANGE_KEY] [SECRET]      ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar parâmetros
if "%~1"=="" (
    echo ❌ ERRO: Parâmetros obrigatórios não fornecidos
    echo.
    echo 💡 Uso correto:
    echo setup_vps.bat [TELEGRAM_TOKEN] [CHAT_ID] [EXCHANGE_KEY] [SECRET]
    echo.
    echo Exemplo:
    echo setup_vps.bat "123456:ABC-DEF" "-1001234567890" "api_key" "api_secret"
    echo.
    echo Para dry-run apenas (sem exchange):
    echo setup_vps.bat "123456:ABC-DEF" "-1001234567890" "" ""
    echo.
    pause
    exit /b 1
)

set "TELEGRAM_TOKEN=%~1"
set "TELEGRAM_CHAT_ID=%~2"
set "EXCHANGE_KEY=%~3"
set "EXCHANGE_SECRET=%~4"

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Este script precisa ser executado como Administrador
    echo.
    echo 💡 Execute: "Executar como administrador"
    exit /b 1
)

set "REPO_URL=https://github.com/smpsandro1239/Freqtrade.git"
set "PROJECT_DIR=Freqtrade-MultiStrategy"
set "LOG_FILE=vps_setup.log"

echo 📝 Iniciando VPS setup... > %LOG_FILE%
echo %date% %time% >> %LOG_FILE%

echo 🔍 Verificando ambiente VPS...

:: ============================================================================
:: INSTALAR CHOCOLATEY (GERENCIADOR DE PACOTES)
:: ============================================================================
choco --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📦 Instalando Chocolatey...
    powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    
    :: Atualizar PATH
    call refreshenv
    
    echo ✅ Chocolatey instalado
) else (
    echo ✅ Chocolatey encontrado
)

:: ============================================================================
:: INSTALAR DEPENDÊNCIAS VIA CHOCOLATEY
:: ============================================================================
echo 🔧 Instalando dependências...

:: Docker Desktop
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 🐳 Instalando Docker Desktop...
    choco install docker-desktop -y --ignore-checksums
    echo ✅ Docker Desktop instalado
) else (
    echo ✅ Docker já instalado
)

:: Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📦 Instalando Git...
    choco install git -y
    echo ✅ Git instalado
) else (
    echo ✅ Git já instalado
)

:: Python (para scripts auxiliares)
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 🐍 Instalando Python...
    choco install python -y
    echo ✅ Python instalado
) else (
    echo ✅ Python já instalado
)

:: Atualizar PATH
call refreshenv

:: ============================================================================
:: CONFIGURAR FIREWALL (VPS)
:: ============================================================================
echo 🔥 Configurando firewall...

:: Permitir Docker
netsh advfirewall firewall add rule name="Docker Desktop" dir=in action=allow program="C:\Program Files\Docker\Docker\Docker Desktop.exe" enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="Docker Engine" dir=in action=allow program="C:\Program Files\Docker\Docker\resources\bin\docker.exe" enable=yes >nul 2>&1

:: Permitir porta do Telegram bot (8080)
netsh advfirewall firewall add rule name="Freqtrade Telegram Bot" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1

echo ✅ Firewall configurado

:: ============================================================================
:: INICIAR DOCKER (se não estiver rodando)
:: ============================================================================
echo 🐳 Verificando Docker...

docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo 🔄 Iniciando Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo ⏳ Aguardando Docker inicializar...
    :wait_docker_vps
    timeout /t 10 /nobreak >nul
    docker ps >nul 2>&1
    if %errorLevel% neq 0 (
        echo    Ainda aguardando Docker...
        goto wait_docker_vps
    )
    
    echo ✅ Docker iniciado
)

:: ============================================================================
:: CLONAR E CONFIGURAR PROJETO
:: ============================================================================
echo 📂 Configurando projeto...

if exist "%PROJECT_DIR%" (
    echo 📁 Atualizando projeto existente...
    cd "%PROJECT_DIR%"
    git pull origin main
) else (
    echo 📥 Clonando repositório...
    git clone %REPO_URL% %PROJECT_DIR%
    cd "%PROJECT_DIR%"
)

:: ============================================================================
:: CONFIGURAR VARIÁVEIS DE AMBIENTE AUTOMATICAMENTE
:: ============================================================================
echo ⚙️ Configurando variáveis de ambiente...

copy ".env.example" ".env" >nul 2>&1

:: Configurar automaticamente via PowerShell
powershell -Command "(Get-Content .env) -replace 'TELEGRAM_TOKEN=.*', 'TELEGRAM_TOKEN=%TELEGRAM_TOKEN%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', 'TELEGRAM_CHAT_ID=%TELEGRAM_CHAT_ID%' | Set-Content .env"

if not "%EXCHANGE_KEY%"=="" (
    powershell -Command "(Get-Content .env) -replace 'EXCHANGE_KEY=.*', 'EXCHANGE_KEY=%EXCHANGE_KEY%' | Set-Content .env"
)
if not "%EXCHANGE_SECRET%"=="" (
    powershell -Command "(Get-Content .env) -replace 'EXCHANGE_SECRET=.*', 'EXCHANGE_SECRET=%EXCHANGE_SECRET%' | Set-Content .env"
)

echo ✅ Variáveis configuradas automaticamente

:: ============================================================================
:: CONFIGURAR SERVIÇO WINDOWS (OPCIONAL)
:: ============================================================================
echo 🔧 Configurando para inicialização automática...

:: Criar script de inicialização
echo @echo off > start_freqtrade.bat
echo cd /d "%CD%" >> start_freqtrade.bat
echo docker-compose up -d >> start_freqtrade.bat

:: Criar tarefa agendada para iniciar com o Windows
schtasks /create /tn "Freqtrade MultiStrategy" /tr "%CD%\start_freqtrade.bat" /sc onstart /ru SYSTEM /f >nul 2>&1

echo ✅ Configurado para iniciar automaticamente com o Windows

:: ============================================================================
:: INICIAR SISTEMA
:: ============================================================================
echo 🚀 Iniciando sistema...

docker-compose up -d --build

if %errorLevel% neq 0 (
    echo ❌ ERRO: Falha ao iniciar containers
    echo 💡 Verifique os logs: docker-compose logs
    exit /b 1
)

:: Aguardar inicialização
echo ⏳ Aguardando inicialização completa...
timeout /t 15 /nobreak >nul

:: Verificar status
echo 🔍 Verificando status final...
docker-compose ps

:: ============================================================================
:: CRIAR SCRIPTS DE MONITORAMENTO
:: ============================================================================
echo 📝 Criando scripts de monitoramento...

:: Script de status
echo @echo off > status.bat
echo cd /d "%~dp0" >> status.bat
echo echo ╔══════════════════════════════════════════════════════════════════════════════╗ >> status.bat
echo echo ║                           📊 STATUS DO SISTEMA                              ║ >> status.bat
echo echo ╚══════════════════════════════════════════════════════════════════════════════╝ >> status.bat
echo docker-compose ps >> status.bat
echo echo. >> status.bat
echo echo 💾 Uso de disco: >> status.bat
echo dir /s /-c ^| find "bytes" >> status.bat
echo echo. >> status.bat
echo echo 🕐 Última atualização: %%date%% %%time%% >> status.bat

:: Script de logs
echo @echo off > logs.bat
echo cd /d "%~dp0" >> logs.bat
echo docker-compose logs -f >> logs.bat

:: Script de restart
echo @echo off > restart.bat
echo cd /d "%~dp0" >> restart.bat
echo echo 🔄 Reiniciando sistema... >> restart.bat
echo docker-compose restart >> restart.bat
echo echo ✅ Sistema reiniciado >> restart.bat

:: Script de backup
echo @echo off > backup.bat
echo cd /d "%~dp0" >> backup.bat
echo set backup_dir=backups\vps_%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%% >> backup.bat
echo mkdir %%backup_dir%% >> backup.bat
echo xcopy user_data\configs %%backup_dir%%\configs\ /E /I >> backup.bat
echo xcopy .env %%backup_dir%%\ >> backup.bat
echo echo ✅ Backup criado em %%backup_dir%% >> backup.bat

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        ✅ VPS SETUP CONCLUÍDO!                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Sistema Freqtrade Multi-Strategy configurado com sucesso no VPS!
echo.
echo 📊 CONFIGURAÇÃO:
echo • Telegram Token: %TELEGRAM_TOKEN%
echo • Chat ID: %TELEGRAM_CHAT_ID%
echo • Exchange: %EXCHANGE_KEY%
echo • Modo: %if "%EXCHANGE_KEY%"=="" (DRY-RUN) else (LIVE TRADING)%
echo.
echo 🤖 SERVIÇOS ATIVOS:
echo • 3 Estratégias de Trading
echo • Telegram Bot (alertas)
echo • Health Monitor (24/7)
echo • Risk Manager (automático)
echo.
echo 🔧 SCRIPTS CRIADOS:
echo • status.bat - Ver status do sistema
echo • logs.bat - Ver logs em tempo real
echo • restart.bat - Reiniciar sistema
echo • backup.bat - Criar backup manual
echo.
echo 🔄 INICIALIZAÇÃO AUTOMÁTICA:
echo • Sistema configurado para iniciar com o Windows
echo • Tarefa agendada criada: "Freqtrade MultiStrategy"
echo.
echo 📱 Em alguns minutos você deve receber confirmação no Telegram!
echo.

echo %date% %time% - VPS Setup concluído com sucesso >> %LOG_FILE%

exit /b 0
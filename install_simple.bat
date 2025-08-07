@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE SIMPLE INSTALLER
:: Instalação simplificada e robusta
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 FREQTRADE SIMPLE INSTALLER                            ║
echo ║                                                                              ║
echo ║  Instalação automática simplificada                                         ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  PRIVILÉGIOS DE ADMINISTRADOR NECESSÁRIOS
    echo.
    echo Este script precisa instalar Docker e Git.
    echo.
    echo 💡 Clique com botão direito neste arquivo e selecione:
    echo    "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Executando com privilégios de administrador
echo.

:: ============================================================================
:: VERIFICAR E INSTALAR CHOCOLATEY
:: ============================================================================
echo 📦 Verificando Chocolatey...

choco --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📥 Instalando Chocolatey...
    echo Isso pode levar alguns minutos...
    echo.
    
    powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    
    if %errorLevel% neq 0 (
        echo ❌ Falha ao instalar Chocolatey
        echo.
        echo 💡 Instalação manual necessária:
        echo 1. Docker: https://www.docker.com/products/docker-desktop
        echo 2. Git: https://git-scm.com/download/win
        pause
        exit /b 1
    )
    
    echo ✅ Chocolatey instalado
    
    :: Atualizar PATH
    call refreshenv
) else (
    echo ✅ Chocolatey já instalado
)

echo.

:: ============================================================================
:: VERIFICAR E INSTALAR DOCKER
:: ============================================================================
echo 🐳 Verificando Docker...

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📥 Instalando Docker Desktop...
    echo Isso pode levar 5-10 minutos...
    echo.
    
    choco install docker-desktop -y --ignore-checksums
    
    if %errorLevel% neq 0 (
        echo ❌ Falha ao instalar Docker via Chocolatey
        echo.
        echo 💡 Instale manualmente:
        echo https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    )
    
    echo ✅ Docker Desktop instalado
) else (
    echo ✅ Docker já instalado
)

echo.

:: ============================================================================
:: VERIFICAR E INSTALAR GIT
:: ============================================================================
echo 📦 Verificando Git...

git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📥 Instalando Git...
    echo.
    
    choco install git -y
    
    if %errorLevel% neq 0 (
        echo ❌ Falha ao instalar Git
        echo.
        echo 💡 Instale manualmente:
        echo https://git-scm.com/download/win
        pause
        exit /b 1
    )
    
    echo ✅ Git instalado
) else (
    echo ✅ Git já instalado
)

echo.

:: Atualizar PATH
call refreshenv

:: ============================================================================
:: VERIFICAR SE DOCKER ESTÁ RODANDO
:: ============================================================================
echo 🐳 Verificando se Docker está rodando...

docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo 🔄 Iniciando Docker Desktop...
    echo.
    
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo ⏳ Aguardando Docker inicializar...
    echo Isso pode levar 1-2 minutos...
    echo.
    
    :: Aguardar Docker inicializar
    set /a counter=0
    :wait_docker
    timeout /t 10 /nobreak >nul
    docker ps >nul 2>&1
    if %errorLevel% neq 0 (
        set /a counter+=1
        if !counter! lss 12 (
            echo    Ainda aguardando... (!counter!/12)
            goto wait_docker
        ) else (
            echo ❌ Docker não iniciou após 2 minutos
            echo.
            echo 💡 Tente:
            echo 1. Abrir Docker Desktop manualmente
            echo 2. Aguardar ele inicializar completamente
            echo 3. Executar este script novamente
            pause
            exit /b 1
        )
    )
    
    echo ✅ Docker iniciado
) else (
    echo ✅ Docker já está rodando
)

echo.

:: ============================================================================
:: CLONAR REPOSITÓRIO (se não existir)
:: ============================================================================
echo 📂 Verificando projeto...

if exist "docker-compose.yml" (
    echo ✅ Projeto já existe neste diretório
) else (
    echo 📥 Clonando repositório...
    
    git clone https://github.com/smpsandro1239/Freqtrade.git temp_clone
    
    if %errorLevel% neq 0 (
        echo ❌ Falha ao clonar repositório
        echo.
        echo 💡 Verifique sua conexão com a internet
        pause
        exit /b 1
    )
    
    :: Mover arquivos para diretório atual
    echo 📁 Movendo arquivos...
    xcopy temp_clone\* . /E /I /Y >nul
    rmdir /s /q temp_clone
    
    echo ✅ Projeto configurado
)

echo.

:: ============================================================================
:: CONFIGURAR TELEGRAM
:: ============================================================================
echo ⚙️ Configurando Telegram...

if not exist ".env" (
    copy ".env.example" ".env" >nul
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                        🤖 CONFIGURAÇÃO DO TELEGRAM                          ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo Para o sistema funcionar, você precisa de um bot do Telegram:
    echo.
    echo 📱 COMO CRIAR BOT:
    echo 1. Abra Telegram e procure @BotFather
    echo 2. Digite /newbot
    echo 3. Siga instruções e copie o TOKEN
    echo.
    echo 💬 COMO OBTER CHAT ID:
    echo 1. Adicione o bot a um chat/grupo
    echo 2. Envie uma mensagem
    echo 3. Acesse: https://api.telegram.org/bot[TOKEN]/getUpdates
    echo 4. Copie o número do "chat":{"id":
    echo.
    
    :get_token
    set /p "token=📱 Cole seu TELEGRAM_TOKEN: "
    if "%token%"=="" (
        echo ❌ Token não pode estar vazio
        goto get_token
    )
    
    :get_chat
    set /p "chat=💬 Cole seu TELEGRAM_CHAT_ID: "
    if "%chat%"=="" (
        echo ❌ Chat ID não pode estar vazio
        goto get_chat
    )
    
    :: Atualizar .env
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_TOKEN=.*', 'TELEGRAM_TOKEN=%token%' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', 'TELEGRAM_CHAT_ID=%chat%' | Set-Content .env"
    
    echo ✅ Telegram configurado
) else (
    echo ✅ Configuração já existe
)

echo.

:: ============================================================================
:: INICIAR SISTEMA
:: ============================================================================
echo 🚀 Iniciando sistema...

echo 📦 Baixando e iniciando containers...
echo Isso pode levar 5-10 minutos na primeira vez...
echo.

docker-compose up -d --build

if %errorLevel% neq 0 (
    echo ❌ Falha ao iniciar containers
    echo.
    echo 💡 Verifique:
    echo 1. Se Docker Desktop está rodando
    echo 2. Execute: docker-compose logs
    pause
    exit /b 1
)

echo.
echo ⏳ Aguardando serviços iniciarem...
timeout /t 15 /nobreak >nul

echo.
echo 📊 Status dos containers:
docker-compose ps

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ INSTALAÇÃO CONCLUÍDA!                         ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Sistema Freqtrade Multi-Strategy instalado com sucesso!
echo.
echo 📊 ESTRATÉGIAS ATIVAS:
echo • SampleStrategyA (RSI - 15m)
echo • SampleStrategyB (RSI - 15m)
echo • WaveHyperNW (WaveTrend + Nadaraya-Watson - 5m)
echo.
echo 🤖 SERVIÇOS:
echo • Telegram Bot (alertas em tempo real)
echo • Health Monitor (monitoramento 24/7)
echo • Risk Manager (ajuste automático)
echo • Redis (cache)
echo.
echo 💡 COMANDOS ÚTEIS:
echo • Ver logs: docker-compose logs -f
echo • Controlar: start.bat
echo • Status: docker-compose ps
echo.
echo 📱 Você deve receber uma mensagem no Telegram em alguns minutos!
echo.

pause
exit /b 0
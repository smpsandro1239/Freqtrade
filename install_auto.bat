@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE AUTO INSTALLER
:: Instalação automática com elevação de privilégios
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 FREQTRADE AUTO INSTALLER                              ║
echo ║                                                                              ║
echo ║  Instalação automática com detecção de privilégios                          ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  PRIVILÉGIOS DE ADMINISTRADOR NECESSÁRIOS
    echo.
    echo Este script precisa instalar Docker e Git, que requerem privilégios de administrador.
    echo.
    echo 🔄 Tentando executar como administrador automaticamente...
    echo.
    
    :: Tentar executar como administrador
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

echo ✅ Executando com privilégios de administrador
echo.

:: Definir variáveis
set "REPO_URL=https://github.com/smpsandro1239/Freqtrade.git"
set "PROJECT_DIR=Freqtrade-MultiStrategy"
set "LOG_FILE=install_auto.log"

echo 📝 Iniciando instalação automática... > %LOG_FILE%
echo %date% %time% >> %LOG_FILE%

:: Função para log
:log
echo %~1
echo %date% %time% - %~1 >> %LOG_FILE%
goto :eof

call :log "🔍 Verificando e instalando pré-requisitos..."

:: ============================================================================
:: INSTALAR CHOCOLATEY (GERENCIADOR DE PACOTES)
:: ============================================================================
call :log "📦 Verificando Chocolatey..."

choco --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "📥 Instalando Chocolatey..."
    echo.
    echo 📦 Instalando Chocolatey (gerenciador de pacotes)...
    echo Isso pode levar alguns minutos...
    echo.
    
    powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    
    if %errorLevel% neq 0 (
        call :log "❌ Falha ao instalar Chocolatey"
        echo.
        echo ❌ ERRO: Não foi possível instalar o Chocolatey
        echo.
        echo 💡 Solução alternativa:
        echo 1. Instale manualmente o Docker Desktop: https://www.docker.com/products/docker-desktop
        echo 2. Instale manualmente o Git: https://git-scm.com/download/win
        echo 3. Execute o quick_start.bat
        pause
        exit /b 1
    )
    
    :: Atualizar PATH
    call refreshenv
    call :log "✅ Chocolatey instalado"
) else (
    call :log "✅ Chocolatey já instalado"
)

:: ============================================================================
:: INSTALAR DOCKER DESKTOP
:: ============================================================================
call :log "🐳 Verificando Docker Desktop..."

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "📥 Instalando Docker Desktop..."
    echo.
    echo 🐳 Instalando Docker Desktop...
    echo Isso pode levar 5-10 minutos...
    echo.
    
    choco install docker-desktop -y --ignore-checksums
    
    if %errorLevel% neq 0 (
        call :log "❌ Falha ao instalar Docker Desktop via Chocolatey"
        echo.
        echo ⚠️  Tentando instalação manual do Docker...
        
        :: Tentar download direto
        call :log "📥 Baixando Docker Desktop diretamente..."
        powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe' -OutFile 'DockerInstaller.exe'"
        
        if exist "DockerInstaller.exe" (
            call :log "🔧 Instalando Docker Desktop..."
            start /wait DockerInstaller.exe install --quiet
            del DockerInstaller.exe
            call :log "✅ Docker Desktop instalado"
        ) else (
            call :log "❌ Falha ao baixar Docker Desktop"
            echo ❌ ERRO: Não foi possível instalar o Docker Desktop
            echo.
            echo 💡 Solução manual:
            echo 1. Acesse: https://www.docker.com/products/docker-desktop
            echo 2. Baixe e instale manualmente
            echo 3. Execute este script novamente
            pause
            exit /b 1
        )
    ) else (
        call :log "✅ Docker Desktop instalado via Chocolatey"
    )
) else (
    call :log "✅ Docker Desktop já instalado"
)

:: ============================================================================
:: INSTALAR GIT
:: ============================================================================
call :log "📦 Verificando Git..."

git --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "📥 Instalando Git..."
    echo.
    echo 📦 Instalando Git...
    echo.
    
    choco install git -y
    
    if %errorLevel% neq 0 (
        call :log "❌ Falha ao instalar Git via Chocolatey"
        echo.
        echo ⚠️  Tentando instalação manual do Git...
        
        :: Tentar download direto
        call :log "📥 Baixando Git diretamente..."
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'GitInstaller.exe'"
        
        if exist "GitInstaller.exe" (
            call :log "🔧 Instalando Git..."
            start /wait GitInstaller.exe /VERYSILENT /NORESTART
            del GitInstaller.exe
            call :log "✅ Git instalado"
        ) else (
            call :log "❌ Falha ao baixar Git"
            echo ❌ ERRO: Não foi possível instalar o Git
            echo.
            echo 💡 Solução manual:
            echo 1. Acesse: https://git-scm.com/download/win
            echo 2. Baixe e instale manualmente
            echo 3. Execute este script novamente
            pause
            exit /b 1
        )
    ) else (
        call :log "✅ Git instalado via Chocolatey"
    )
) else (
    call :log "✅ Git já instalado"
)

:: Atualizar PATH
call refreshenv

:: ============================================================================
:: VERIFICAR SE DOCKER ESTÁ RODANDO
:: ============================================================================
call :log "🐳 Verificando se Docker está rodando..."

docker ps >nul 2>&1
if %errorLevel% neq 0 (
    call :log "🔄 Iniciando Docker Desktop..."
    echo.
    echo 🔄 Docker Desktop não está rodando. Iniciando...
    echo.
    
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo ⏳ Aguardando Docker Desktop inicializar...
    echo Isso pode levar 1-2 minutos...
    echo.
    
    :wait_docker
    timeout /t 10 /nobreak >nul
    docker ps >nul 2>&1
    if %errorLevel% neq 0 (
        echo    Ainda aguardando Docker inicializar...
        goto wait_docker
    )
    
    call :log "✅ Docker Desktop iniciado"
) else (
    call :log "✅ Docker já está rodando"
)

:: ============================================================================
:: CLONAR OU ATUALIZAR REPOSITÓRIO
:: ============================================================================
call :log "📂 Configurando projeto..."

if exist "%PROJECT_DIR%" (
    call :log "📁 Diretório do projeto já existe. Atualizando..."
    cd "%PROJECT_DIR%"
    git pull origin main
    call :log "✅ Projeto atualizado"
) else (
    call :log "📥 Clonando repositório..."
    git clone %REPO_URL% %PROJECT_DIR%
    if %errorLevel% neq 0 (
        call :log "❌ Falha ao clonar repositório"
        echo ❌ ERRO: Não foi possível clonar o repositório
        echo.
        echo 💡 Verifique sua conexão com a internet e tente novamente
        pause
        exit /b 1
    )
    cd "%PROJECT_DIR%"
    call :log "✅ Repositório clonado com sucesso"
)

:: ============================================================================
:: CONFIGURAR VARIÁVEIS DE AMBIENTE
:: ============================================================================
call :log "⚙️ Configurando variáveis de ambiente..."

if not exist ".env" (
    copy ".env.example" ".env"
    call :log "📄 Arquivo .env criado"
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════════╗
    echo ║                        🔧 CONFIGURAÇÃO DO TELEGRAM                          ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo Para o sistema funcionar, você precisa configurar o bot do Telegram:
    echo.
    echo 🤖 COMO CRIAR BOT DO TELEGRAM:
    echo 1. Abra o Telegram e procure por @BotFather
    echo 2. Digite /newbot e siga as instruções
    echo 3. Copie o TOKEN que será fornecido
    echo.
    echo 💬 COMO OBTER CHAT ID:
    echo 1. Adicione seu bot a um grupo ou chat privado
    echo 2. Envie uma mensagem qualquer para o bot
    echo 3. Acesse: https://api.telegram.org/bot[SEU_TOKEN]/getUpdates
    echo 4. Procure por "chat":{"id": e copie o número
    echo.
    
    :config_telegram
    echo.
    set /p "TELEGRAM_TOKEN=📱 Cole seu TELEGRAM_TOKEN: "
    if "!TELEGRAM_TOKEN!"=="" (
        echo ❌ Token não pode estar vazio
        goto config_telegram
    )
    
    :config_chat
    set /p "TELEGRAM_CHAT_ID=💬 Cole seu TELEGRAM_CHAT_ID: "
    if "!TELEGRAM_CHAT_ID!"=="" (
        echo ❌ Chat ID não pode estar vazio
        goto config_chat
    )
    
    echo.
    echo 🏦 Configuração da Exchange (OPCIONAL - pressione Enter para pular):
    echo Para trading real, configure suas chaves da exchange.
    echo Para apenas testar, deixe em branco (usará modo dry-run).
    echo.
    set /p "EXCHANGE_KEY=🔑 EXCHANGE_KEY (opcional): "
    set /p "EXCHANGE_SECRET=🔐 EXCHANGE_SECRET (opcional): "
    
    :: Atualizar arquivo .env
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_TOKEN=.*', 'TELEGRAM_TOKEN=!TELEGRAM_TOKEN!' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', 'TELEGRAM_CHAT_ID=!TELEGRAM_CHAT_ID!' | Set-Content .env"
    
    if not "!EXCHANGE_KEY!"=="" (
        powershell -Command "(Get-Content .env) -replace 'EXCHANGE_KEY=.*', 'EXCHANGE_KEY=!EXCHANGE_KEY!' | Set-Content .env"
    )
    if not "!EXCHANGE_SECRET!"=="" (
        powershell -Command "(Get-Content .env) -replace 'EXCHANGE_SECRET=.*', 'EXCHANGE_SECRET=!EXCHANGE_SECRET!' | Set-Content .env"
    )
    
    call :log "✅ Variáveis de ambiente configuradas"
) else (
    call :log "✅ Arquivo .env já existe"
)

:: ============================================================================
:: INICIAR SISTEMA
:: ============================================================================
call :log "🚀 Iniciando sistema Freqtrade..."

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                           🚀 INICIANDO SISTEMA                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

call :log "📦 Baixando e construindo containers Docker..."
echo 📦 Baixando imagens Docker e construindo containers...
echo Isso pode levar 5-10 minutos na primeira vez...
echo.

docker-compose up -d --build

if %errorLevel% neq 0 (
    call :log "❌ Falha ao iniciar containers"
    echo ❌ ERRO: Falha ao iniciar os containers
    echo.
    echo 💡 Possíveis soluções:
    echo 1. Verifique se o Docker Desktop está rodando
    echo 2. Reinicie o Docker Desktop
    echo 3. Execute: docker-compose logs para ver detalhes do erro
    pause
    exit /b 1
)

:: Aguardar containers iniciarem
call :log "⏳ Aguardando containers iniciarem..."
echo ⏳ Aguardando todos os serviços iniciarem...
timeout /t 15 /nobreak >nul

:: Verificar status
call :log "🔍 Verificando status dos containers..."
echo.
echo 📊 Status dos containers:
docker-compose ps

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ INSTALAÇÃO CONCLUÍDA!                         ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Sistema Freqtrade Multi-Strategy instalado e iniciado com sucesso!
echo.
echo 📊 ESTRATÉGIAS ATIVAS:
echo • SampleStrategyA (RSI - 15m)
echo • SampleStrategyB (RSI - 15m)  
echo • WaveHyperNW (WaveTrend + Nadaraya-Watson - 5m)
echo.
echo 🤖 SERVIÇOS RODANDO:
echo • Telegram Bot (alertas em tempo real)
echo • Health Monitor (monitoramento 24/7)
echo • Risk Manager (ajuste automático de stakes)
echo • Redis (cache de dados)
echo.
echo 💡 COMANDOS ÚTEIS:
echo • Ver status: docker-compose ps
echo • Ver logs: docker-compose logs -f
echo • Controle: execute start.bat
echo.
echo 📱 Em alguns minutos você deve receber uma mensagem no Telegram
echo    confirmando que o sistema está funcionando!
echo.
echo 🔗 Documentação: https://github.com/smpsandro1239/Freqtrade
echo.

call :log "✅ Instalação concluída com sucesso"

echo 💾 Log completo salvo em: %LOG_FILE%
echo.
pause
exit /b 0
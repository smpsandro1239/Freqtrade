@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE MULTI-STRATEGY SETUP SCRIPT
:: Instala e configura o sistema completo automaticamente
:: Compatível com Windows Local e VPS
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 FREQTRADE MULTI-STRATEGY SETUP                        ║
echo ║                                                                              ║
echo ║  Este script vai instalar e configurar automaticamente:                     ║
echo ║  • Docker Desktop (se necessário)                                           ║
echo ║  • Git (se necessário)                                                      ║
echo ║  • Clonar o repositório                                                     ║
echo ║  • Configurar variáveis de ambiente                                         ║
echo ║  • Iniciar o sistema completo                                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Este script precisa ser executado como Administrador
    echo.
    echo 💡 Clique com botão direito no arquivo e selecione "Executar como administrador"
    pause
    exit /b 1
)

:: Definir variáveis
set "REPO_URL=https://github.com/smpsandro1239/Freqtrade.git"
set "PROJECT_DIR=Freqtrade-MultiStrategy"
set "LOG_FILE=setup.log"

echo 📝 Iniciando setup... > %LOG_FILE%
echo %date% %time% >> %LOG_FILE%

:: Função para log
:log
echo %~1
echo %date% %time% - %~1 >> %LOG_FILE%
goto :eof

call :log "🔍 Verificando pré-requisitos..."

:: ============================================================================
:: VERIFICAR E INSTALAR DOCKER
:: ============================================================================
call :log "🐳 Verificando Docker..."

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "❌ Docker não encontrado. Instalando Docker Desktop..."
    
    echo.
    echo ⚠️  DOCKER NÃO ENCONTRADO
    echo.
    echo O Docker Desktop será baixado e instalado automaticamente.
    echo Isso pode levar alguns minutos...
    echo.
    
    :: Baixar Docker Desktop
    call :log "📥 Baixando Docker Desktop..."
    powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe' -OutFile 'DockerInstaller.exe'"
    
    if not exist "DockerInstaller.exe" (
        call :log "❌ Falha ao baixar Docker Desktop"
        echo.
        echo ❌ ERRO: Não foi possível baixar o Docker Desktop
        echo.
        echo 💡 Solução manual:
        echo 1. Acesse: https://www.docker.com/products/docker-desktop
        echo 2. Baixe e instale o Docker Desktop
        echo 3. Execute este script novamente
        pause
        exit /b 1
    )
    
    :: Instalar Docker Desktop
    call :log "🔧 Instalando Docker Desktop..."
    start /wait DockerInstaller.exe install --quiet
    
    :: Limpar arquivo de instalação
    del DockerInstaller.exe
    
    echo.
    echo ✅ Docker Desktop instalado com sucesso!
    echo.
    echo ⚠️  REINICIALIZAÇÃO NECESSÁRIA
    echo.
    echo O Docker Desktop foi instalado, mas é necessário:
    echo 1. Reiniciar o computador
    echo 2. Iniciar o Docker Desktop
    echo 3. Executar este script novamente
    echo.
    pause
    exit /b 0
) else (
    call :log "✅ Docker encontrado"
)

:: Verificar se Docker está rodando
docker ps >nul 2>&1
if %errorLevel% neq 0 (
    call :log "🔄 Iniciando Docker Desktop..."
    echo.
    echo 🔄 Docker Desktop não está rodando. Iniciando...
    
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo ⏳ Aguardando Docker Desktop inicializar...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker ps >nul 2>&1
    if %errorLevel% neq 0 (
        echo    Ainda aguardando...
        goto wait_docker
    )
    
    call :log "✅ Docker Desktop iniciado"
)

:: ============================================================================
:: VERIFICAR E INSTALAR GIT
:: ============================================================================
call :log "📦 Verificando Git..."

git --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log "❌ Git não encontrado. Instalando..."
    
    echo.
    echo ⚠️  GIT NÃO ENCONTRADO
    echo.
    echo O Git será baixado e instalado automaticamente.
    echo.
    
    :: Baixar Git
    call :log "📥 Baixando Git..."
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'GitInstaller.exe'"
    
    if not exist "GitInstaller.exe" (
        call :log "❌ Falha ao baixar Git"
        echo ❌ ERRO: Não foi possível baixar o Git
        echo.
        echo 💡 Solução manual:
        echo 1. Acesse: https://git-scm.com/download/win
        echo 2. Baixe e instale o Git
        echo 3. Execute este script novamente
        pause
        exit /b 1
    )
    
    :: Instalar Git
    call :log "🔧 Instalando Git..."
    start /wait GitInstaller.exe /VERYSILENT /NORESTART
    
    :: Limpar arquivo de instalação
    del GitInstaller.exe
    
    :: Atualizar PATH
    call refreshenv
    
    call :log "✅ Git instalado com sucesso"
) else (
    call :log "✅ Git encontrado"
)

:: ============================================================================
:: CLONAR REPOSITÓRIO
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
    echo ║                        🔧 CONFIGURAÇÃO NECESSÁRIA                           ║
    echo ╚══════════════════════════════════════════════════════════════════════════════╝
    echo.
    echo Para o sistema funcionar, você precisa configurar:
    echo.
    echo 🤖 TELEGRAM BOT:
    echo 1. Abra o Telegram e procure por @BotFather
    echo 2. Digite /newbot e siga as instruções
    echo 3. Copie o TOKEN que será fornecido
    echo.
    echo 💬 CHAT ID:
    echo 1. Adicione seu bot a um grupo ou chat
    echo 2. Envie uma mensagem qualquer
    echo 3. Acesse: https://api.telegram.org/bot[SEU_TOKEN]/getUpdates
    echo 4. Procure por "chat":{"id": e copie o número
    echo.
    echo 🏦 EXCHANGE (OPCIONAL para dry-run):
    echo 1. Crie conta na Binance (ou outra exchange)
    echo 2. Gere API Key e Secret nas configurações
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
    echo 🏦 Configuração da Exchange (pressione Enter para pular - usará dry-run):
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
call :log "🚀 Iniciando sistema..."

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                           🚀 INICIANDO SISTEMA                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

call :log "📦 Baixando e construindo containers..."
docker-compose up -d --build

if %errorLevel% neq 0 (
    call :log "❌ Falha ao iniciar containers"
    echo ❌ ERRO: Falha ao iniciar os containers
    echo.
    echo 💡 Verifique os logs para mais detalhes:
    echo docker-compose logs
    pause
    exit /b 1
)

:: Aguardar containers iniciarem
call :log "⏳ Aguardando containers iniciarem..."
timeout /t 10 /nobreak >nul

:: Verificar status
call :log "🔍 Verificando status dos containers..."
docker-compose ps

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ SETUP CONCLUÍDO!                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Sistema Freqtrade Multi-Strategy iniciado com sucesso!
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
echo • Parar sistema: docker-compose down
echo • Reiniciar: docker-compose restart
echo.
echo 📱 Em alguns minutos você deve receber uma mensagem no Telegram
echo    confirmando que o sistema está funcionando!
echo.
echo 🔗 Documentação completa: https://github.com/smpsandro1239/Freqtrade
echo.

call :log "✅ Setup concluído com sucesso"

:: Criar script de controle
call :log "📝 Criando scripts de controle..."

echo @echo off > controle.bat
echo cd /d "%~dp0" >> controle.bat
echo echo. >> controle.bat
echo echo ╔══════════════════════════════════════════════════════════════════════════════╗ >> controle.bat
echo echo ║                    🎛️  FREQTRADE CONTROLE RÁPIDO                           ║ >> controle.bat
echo echo ╚══════════════════════════════════════════════════════════════════════════════╝ >> controle.bat
echo echo. >> controle.bat
echo echo 1. Ver Status >> controle.bat
echo echo 2. Ver Logs >> controle.bat
echo echo 3. Reiniciar Sistema >> controle.bat
echo echo 4. Parar Sistema >> controle.bat
echo echo 5. Alternar para LIVE Trading ^(CUIDADO!^) >> controle.bat
echo echo 6. Voltar para DRY-RUN >> controle.bat
echo echo 7. Backup Manual >> controle.bat
echo echo 8. Sair >> controle.bat
echo echo. >> controle.bat
echo set /p choice="Escolha uma opção (1-8): " >> controle.bat
echo. >> controle.bat
echo if "%%choice%%"=="1" docker-compose ps ^&^& pause >> controle.bat
echo if "%%choice%%"=="2" docker-compose logs -f >> controle.bat
echo if "%%choice%%"=="3" docker-compose restart ^&^& echo ✅ Sistema reiniciado ^&^& pause >> controle.bat
echo if "%%choice%%"=="4" docker-compose down ^&^& echo ✅ Sistema parado ^&^& pause >> controle.bat
echo if "%%choice%%"=="5" python scripts/toggle_mode.py live ^&^& docker-compose restart >> controle.bat
echo if "%%choice%%"=="6" python scripts/toggle_mode.py dry ^&^& docker-compose restart >> controle.bat
echo if "%%choice%%"=="7" mkdir backups\manual_%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%% ^&^& xcopy user_data\configs backups\manual_%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%%\ /E /I ^&^& echo ✅ Backup criado ^&^& pause >> controle.bat
echo if "%%choice%%"=="8" exit >> controle.bat
echo goto :eof >> controle.bat

echo.
echo 📝 Script de controle criado: controle.bat
echo    Execute este arquivo para controlar o sistema facilmente!
echo.

pause
exit /b 0
@echo off
echo.
echo ========================================
echo   FREQTRADE DEPLOY AUTOMATICO
echo   Sistema Completo com IA Preditiva
echo ========================================
echo.

REM Verificar se Docker esta instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker nao encontrado! Instale o Docker Desktop primeiro.
    echo    Download: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker encontrado!
echo.

REM Verificar se arquivo .env existe
if not exist .env (
    echo ⚠️  Arquivo .env nao encontrado!
    echo    Copiando template...
    copy .env.example .env
    echo.
    echo ❌ CONFIGURE O ARQUIVO .env ANTES DE CONTINUAR!
    echo.
    echo    Edite o arquivo .env com:
    echo    - TELEGRAM_TOKEN (do @BotFather)
    echo    - TELEGRAM_CHAT_ID (seu chat ID)
    echo    - TELEGRAM_ADMIN_USERS (seu user ID)
    echo    - Exchange API keys
    echo.
    echo    Pressione qualquer tecla apos configurar...
    pause
)

echo ✅ Arquivo .env encontrado!
echo.

REM Verificar configuracoes criticas
findstr /C:"TELEGRAM_TOKEN=1234567890" .env >nul
if not errorlevel 1 (
    echo ❌ TELEGRAM_TOKEN ainda esta com valor padrao!
    echo    Configure o token real do seu bot.
    pause
    exit /b 1
)

findstr /C:"TELEGRAM_CHAT_ID=123456789" .env >nul
if not errorlevel 1 (
    echo ❌ TELEGRAM_CHAT_ID ainda esta com valor padrao!
    echo    Configure seu chat ID real.
    pause
    exit /b 1
)

echo ✅ Configuracoes basicas verificadas!
echo.

REM Menu de opcoes
:menu
echo ========================================
echo   OPCOES DE DEPLOY
echo ========================================
echo.
echo 1. Deploy em DRY-RUN (Recomendado para testes)
echo 2. Deploy em LIVE TRADING (Apenas apos testes!)
echo 3. Verificar Status do Sistema
echo 4. Ver Logs em Tempo Real
echo 5. Parar Sistema
echo 6. Backup das Configuracoes
echo 7. Sair
echo.
set /p choice="Escolha uma opcao (1-7): "

if "%choice%"=="1" goto deploy_dryrun
if "%choice%"=="2" goto deploy_live
if "%choice%"=="3" goto status
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto stop
if "%choice%"=="6" goto backup
if "%choice%"=="7" goto exit
goto menu

:deploy_dryrun
echo.
echo 🧪 INICIANDO DEPLOY EM DRY-RUN...
echo.

REM Garantir que esta em dry-run
powershell -Command "(Get-Content .env) -replace 'DRY_RUN=false', 'DRY_RUN=true' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'EXCHANGE_SANDBOX=false', 'EXCHANGE_SANDBOX=true' | Set-Content .env"

echo ✅ Configurado para DRY-RUN (modo de teste)
echo.

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker compose down

echo.
echo 🚀 Iniciando sistema...
docker compose up -d

echo.
echo ⏳ Aguardando inicializacao (30 segundos)...
timeout /t 30 /nobreak

echo.
echo 📊 Status dos containers:
docker compose ps

echo.
echo ========================================
echo   SISTEMA INICIADO EM DRY-RUN!
echo ========================================
echo.
echo 📱 TESTE NO TELEGRAM:
echo    /start          - Menu principal
echo    /status         - Status das estrategias
echo    /predict        - Previsoes de IA
echo    /stats          - Estatisticas horarias
echo    /forcebuy stratA BTC/USDT - Teste de compra
echo.
echo ⚠️  IMPORTANTE: Teste todas as funcionalidades
echo    antes de fazer deploy em LIVE!
echo.
pause
goto menu

:deploy_live
echo.
echo ⚠️  DEPLOY EM LIVE TRADING
echo ========================================
echo.
echo    ATENCAO: Isso ira usar dinheiro real!
echo.
echo    Certifique-se de que:
echo    ✅ Testou em dry-run por pelo menos 24h
echo    ✅ Todas as funcionalidades funcionam
echo    ✅ Configurou stake amount adequado
echo    ✅ Tem API keys de producao
echo.
set /p confirm="Tem certeza? Digite 'SIM' para continuar: "

if not "%confirm%"=="SIM" (
    echo ❌ Deploy cancelado.
    goto menu
)

echo.
echo 💰 CONFIGURANDO PARA LIVE TRADING...

REM Fazer backup antes
call :backup_silent

REM Configurar para live
powershell -Command "(Get-Content .env) -replace 'DRY_RUN=true', 'DRY_RUN=false' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'EXCHANGE_SANDBOX=true', 'EXCHANGE_SANDBOX=false' | Set-Content .env"

echo ✅ Configurado para LIVE TRADING
echo.

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker compose down

echo.
echo 🚀 Iniciando sistema LIVE...
docker compose up -d

echo.
echo ⏳ Aguardando inicializacao (30 segundos)...
timeout /t 30 /nobreak

echo.
echo 📊 Status dos containers:
docker compose ps

echo.
echo ========================================
echo   SISTEMA LIVE INICIADO!
echo ========================================
echo.
echo 🚨 MONITORAMENTO CRITICO:
echo    - Verifique /status a cada 15 min
echo    - Monitore posicoes abertas
echo    - Use /emergency se necessario
echo.
echo 📱 COMANDOS DE EMERGENCIA:
echo    /emergency              - Parar tudo
echo    /forcesell stratA all   - Vender tudo
echo    /adjust stratA conservative - Modo cauteloso
echo.
pause
goto menu

:status
echo.
echo 📊 STATUS DO SISTEMA
echo ========================================
echo.
docker compose ps
echo.
echo 💾 Uso de espaco:
docker system df
echo.
echo 📈 Uso de recursos:
docker stats --no-stream
echo.
pause
goto menu

:logs
echo.
echo 📋 LOGS EM TEMPO REAL
echo ========================================
echo.
echo Pressione Ctrl+C para sair dos logs
echo.
docker compose logs -f
goto menu

:stop
echo.
echo 🛑 PARANDO SISTEMA...
echo.
docker compose down
echo.
echo ✅ Sistema parado!
echo.
pause
goto menu

:backup
call :backup_silent
echo.
echo ✅ Backup concluido!
echo.
pause
goto menu

:backup_silent
echo 💾 Fazendo backup das configuracoes...
set backup_dir=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_dir=%backup_dir: =0%
mkdir %backup_dir% 2>nul
copy .env %backup_dir%\ >nul
xcopy user_data %backup_dir%\user_data\ /E /I /Q >nul
echo ✅ Backup salvo em: %backup_dir%
goto :eof

:exit
echo.
echo 👋 Obrigado por usar o Freqtrade Commander!
echo.
echo 📚 Documentacao completa:
echo    - DEPLOY_PRODUCAO.md
echo    - SISTEMA_COMPLETO_FINAL.md
echo    - README.md
echo.
echo 🌐 GitHub: https://github.com/smpsandro1239/Freqtrade
echo.
pause
exit /b 0
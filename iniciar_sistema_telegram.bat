@echo off
echo.
echo ========================================
echo   INICIAR SISTEMA COMPLETO COM TELEGRAM
echo   Freqtrade Commander + IA + Trading Manual
echo ========================================
echo.

REM Verificar se Docker esta disponivel
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
    echo ❌ Arquivo .env nao encontrado!
    echo    Copie .env.example para .env e configure suas credenciais.
    pause
    exit /b 1
)

echo ✅ Arquivo .env encontrado!
echo.

REM Testar comunicacao com Telegram primeiro
echo 📱 TESTANDO COMUNICACAO COM TELEGRAM...
echo.
python test_telegram_completo.py

echo.
set /p continue="Comunicacao Telegram OK? Continuar com inicializacao? (S/N): "
if /i not "%continue%"=="S" (
    echo ❌ Inicializacao cancelada.
    echo    Configure o Telegram primeiro.
    pause
    exit /b 0
)

echo.
echo 🚀 INICIANDO SISTEMA COMPLETO...
echo.

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker compose down >nul 2>&1

echo.
echo 🔨 Fazendo build dos containers...
docker compose build >nul 2>&1

if errorlevel 1 (
    echo ❌ Erro no build dos containers!
    echo    Verificando logs...
    docker compose build
    pause
    exit /b 1
)

echo ✅ Build concluido!
echo.

echo 🚀 Iniciando todos os servicos...
docker compose up -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar servicos!
    echo    Verificando logs...
    docker compose logs
    pause
    exit /b 1
)

echo ✅ Servicos iniciados!
echo.

echo ⏳ Aguardando inicializacao completa (45 segundos)...
timeout /t 45 /nobreak >nul

echo.
echo 📊 STATUS DOS CONTAINERS:
docker compose ps

echo.
echo 📋 VERIFICANDO LOGS DO TELEGRAM COMMANDER...
docker compose logs --tail=10 telegram_commander

echo.
echo ========================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.

echo 🎉 SERVICOS ATIVOS:
echo    ✅ Telegram Commander (IA + Trading Manual)
echo    ✅ Strategy A
echo    ✅ Strategy B  
echo    ✅ WaveHyperNW Strategy
echo.

echo 📱 TESTE NO TELEGRAM AGORA:
echo.
echo    /start          - Menu principal completo
echo    /status         - Status de todas as estrategias
echo    /predict        - Previsoes de IA (NOVO!)
echo    /stats          - Estatisticas horarias
echo    /forcebuy stratA BTC/USDT - Trading manual (NOVO!)
echo    /adjust stratA aggressive - Ajuste dinamico (NOVO!)
echo    /help           - Lista completa de comandos
echo.

echo 🔮 FUNCIONALIDADES ATIVAS:
echo    ✅ IA Preditiva - Previsao de subidas
echo    ✅ Trading Manual - Compra/venda forcada
echo    ✅ Ajuste Dinamico - Estrategias adaptaveis
echo    ✅ Notificacoes 24/7 - Alertas automaticos
echo    ✅ Dashboard Horario - Dados em tempo real
echo.

echo 📊 MONITORAMENTO:
echo    Execute: .\monitor_producao.bat
echo    Para monitoramento em tempo real
echo.

echo 🏥 VERIFICACAO DE SAUDE:
echo    Execute: python scripts/health_check.py
echo    Para verificar saude do sistema
echo.

set /p test_now="Deseja enviar mensagem de teste agora? (S/N): "
if /i "%test_now%"=="S" (
    echo.
    echo 📱 Enviando mensagem de confirmacao...
    
    REM Obter configuracoes do .env
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_CHAT_ID" .env 2^>nul') do set chat_id=%%i
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_TOKEN" .env 2^>nul') do set bot_token=%%i
    
    if not "%chat_id%"=="" if not "%bot_token%"=="" (
        curl -s -X POST "https://api.telegram.org/bot%bot_token%/sendMessage" -d "chat_id=%chat_id%" -d "text=🎉 SISTEMA FREQTRADE COMMANDER INICIADO!%0A%0A✅ Todos os servicos ativos:%0A🔮 IA Preditiva%0A💰 Trading Manual%0A⚙️ Ajuste Dinamico%0A📊 Dashboard Horario%0A🔔 Notificacoes 24/7%0A%0ATestem: /start" >nul 2>&1
        echo ✅ Mensagem enviada!
    ) else (
        echo ⚠️  Erro ao obter configuracoes do Telegram
    )
)

echo.
echo 🎯 PROXIMOS PASSOS:
echo    1. Abra o Telegram
echo    2. Digite /start
echo    3. Explore o menu completo
echo    4. Teste as novas funcionalidades
echo    5. Configure notificacoes se desejar
echo.

echo 📚 DOCUMENTACAO:
echo    - DEPLOY_FINAL_PRODUCAO.md - Guia completo
echo    - SISTEMA_COMPLETO_FINAL.md - Funcionalidades
echo    - TRADING_MANUAL_COMMANDS.md - Comandos de trading
echo.

echo 🌐 GitHub: https://github.com/smpsandro1239/Freqtrade
echo.

echo 🎉 SISTEMA REVOLUCIONARIO ATIVO!
echo    IA + Trading Manual + Notificacoes + Dashboard
echo.
pause
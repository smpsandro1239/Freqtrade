@echo off
title Freqtrade Production Monitor
color 0A

:main_loop
cls
echo.
echo ========================================
echo   FREQTRADE PRODUCTION MONITOR
echo   %date% %time%
echo ========================================
echo.

REM Verificar se sistema esta rodando
docker compose ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose nao encontrado ou sistema parado!
    echo.
    echo Pressione qualquer tecla para tentar novamente...
    pause >nul
    goto main_loop
)

REM Status dos containers
echo 🐳 STATUS DOS CONTAINERS:
echo ----------------------------------------
docker compose ps
echo.

REM Verificar saude do sistema
echo 🏥 VERIFICACAO DE SAUDE:
echo ----------------------------------------
python scripts/health_check.py
echo.

REM Estatisticas rapidas
echo 📊 ESTATISTICAS RAPIDAS:
echo ----------------------------------------

REM Verificar se ha trades recentes
for /f "tokens=*" %%i in ('docker compose exec ft-stratA freqtrade show_trades --config user_data/configs/stratA.json --trade-ids --open-only 2^>nul ^| find /c "BTC"') do set trades_a=%%i
for /f "tokens=*" %%i in ('docker compose exec ft-stratB freqtrade show_trades --config user_data/configs/stratB.json --trade-ids --open-only 2^>nul ^| find /c "BTC"') do set trades_b=%%i
for /f "tokens=*" %%i in ('docker compose exec ft-waveHyperNW freqtrade show_trades --config user_data/configs/waveHyperNW.json --trade-ids --open-only 2^>nul ^| find /c "BTC"') do set trades_w=%%i

echo    Strategy A: %trades_a% posicoes abertas
echo    Strategy B: %trades_b% posicoes abertas  
echo    WaveHyperNW: %trades_w% posicoes abertas
echo.

REM Uso de recursos
echo 💾 USO DE RECURSOS:
echo ----------------------------------------
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo.

REM Logs recentes (ultimas 5 linhas)
echo 📋 LOGS RECENTES:
echo ----------------------------------------
echo [Telegram Commander]
docker compose logs --tail=3 telegram_commander 2>nul | findstr /v "INFO"
echo.
echo [Strategy A]  
docker compose logs --tail=2 ft-stratA 2>nul | findstr /v "INFO"
echo.

REM Menu de opcoes
echo ========================================
echo   OPCOES DE MONITORAMENTO
echo ========================================
echo.
echo 1. Continuar monitoramento (auto-refresh 30s)
echo 2. Ver logs completos
echo 3. Executar health check detalhado
echo 4. Enviar comando Telegram de teste
echo 5. Ver posicoes abertas detalhadas
echo 6. Parar monitoramento
echo.

REM Auto-refresh ou aguardar input
choice /c 123456 /t 30 /d 1 /m "Escolha uma opcao (auto-refresh em 30s): "

if errorlevel 6 goto exit
if errorlevel 5 goto show_positions
if errorlevel 4 goto test_telegram
if errorlevel 3 goto detailed_health
if errorlevel 2 goto show_logs
if errorlevel 1 goto main_loop

:show_logs
cls
echo 📋 LOGS COMPLETOS - Pressione Ctrl+C para voltar
echo ========================================
docker compose logs -f
goto main_loop

:detailed_health
cls
echo 🏥 VERIFICACAO DETALHADA DE SAUDE
echo ========================================
python scripts/health_check.py
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
goto main_loop

:test_telegram
cls
echo 📱 TESTE DO TELEGRAM BOT
echo ========================================
echo.
echo Enviando comando de teste...
echo.

REM Obter chat ID do .env
for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_CHAT_ID" .env') do set chat_id=%%i
for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_TOKEN" .env') do set bot_token=%%i

if "%chat_id%"=="" (
    echo ❌ TELEGRAM_CHAT_ID nao encontrado no .env
) else if "%bot_token%"=="" (
    echo ❌ TELEGRAM_TOKEN nao encontrado no .env
) else (
    echo ✅ Enviando mensagem de teste...
    curl -s -X POST "https://api.telegram.org/bot%bot_token%/sendMessage" -d "chat_id=%chat_id%" -d "text=🤖 Sistema funcionando! Monitor ativo em %date% %time%"
    echo.
    echo ✅ Mensagem enviada! Verifique seu Telegram.
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul
goto main_loop

:show_positions
cls
echo 💰 POSICOES ABERTAS DETALHADAS
echo ========================================
echo.

echo [Strategy A]
echo ----------------------------------------
docker compose exec ft-stratA freqtrade show_trades --config user_data/configs/stratA.json --trade-ids --open-only 2>nul
echo.

echo [Strategy B]
echo ----------------------------------------
docker compose exec ft-stratB freqtrade show_trades --config user_data/configs/stratB.json --trade-ids --open-only 2>nul
echo.

echo [WaveHyperNW]
echo ----------------------------------------
docker compose exec ft-waveHyperNW freqtrade show_trades --config user_data/configs/waveHyperNW.json --trade-ids --open-only 2>nul
echo.

echo Pressione qualquer tecla para continuar...
pause >nul
goto main_loop

:exit
echo.
echo 👋 Monitor finalizado!
echo.
echo 📊 Para monitoramento via Telegram use:
echo    /status - Status geral
echo    /stats  - Estatisticas detalhadas
echo    /predict - Previsoes de IA
echo.
pause
exit /b 0
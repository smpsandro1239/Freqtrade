@echo off
echo.
echo ========================================
echo 🚀 INICIANDO SISTEMA FREQTRADE COMPLETO
echo ========================================
echo.

:: Verificar se Docker está rodando
echo 🔍 Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não encontrado! Instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando! Inicie o Docker Desktop primeiro.
    pause
    exit /b 1
)

echo ✅ Docker está funcionando

:: Parar containers existentes
echo.
echo 🛑 Parando containers existentes...
docker-compose -f docker-compose-simples.yml down

:: Construir e iniciar containers
echo.
echo 🏗️ Construindo e iniciando containers...
docker-compose -f docker-compose-simples.yml up -d

:: Aguardar inicialização
echo.
echo ⏳ Aguardando inicialização dos containers...
timeout /t 30 /nobreak >nul

:: Verificar status dos containers
echo.
echo 📊 Verificando status dos containers...
docker-compose -f docker-compose-simples.yml ps

:: Testar APIs
echo.
echo 🔧 Testando APIs (aguarde...)
timeout /t 10 /nobreak >nul

echo.
echo 🧪 Executando teste completo do sistema...
python test_sistema_completo.py

:: Verificar se o teste passou
if errorlevel 1 (
    echo.
    echo ❌ Alguns testes falharam. Verifique os logs acima.
    echo.
    echo 💡 Comandos úteis para diagnóstico:
    echo   docker-compose -f docker-compose-simples.yml logs
    echo   docker-compose -f docker-compose-simples.yml ps
    echo   docker-compose -f docker-compose-simples.yml restart
    echo.
) else (
    echo.
    echo 🎉 SISTEMA INICIADO COM SUCESSO!
    echo.
    echo 📱 TELEGRAM BOT: @smpsandrobot
    echo 🔗 APIs disponíveis em:
    echo   • Strategy A: http://127.0.0.1:8081
    echo   • Strategy B: http://127.0.0.1:8082  
    echo   • WaveHyperNW: http://127.0.0.1:8083
    echo   • ML Strategy: http://127.0.0.1:8084
    echo   • ML Simple: http://127.0.0.1:8085
    echo   • Multi Timeframe: http://127.0.0.1:8086
    echo   • Wave Enhanced: http://127.0.0.1:8087
    echo.
    echo 💡 COMANDOS TELEGRAM DISPONÍVEIS:
    echo   /start - Menu principal
    echo   /status - Status das estratégias
    echo   /predict - IA preditiva avançada
    echo   /charts - Gráficos visuais
    echo   /stats - Estatísticas detalhadas
    echo   /forcebuy - Trading manual
    echo   /forcesell - Trading manual
    echo.
    echo 🔍 MONITORAMENTO:
    echo   docker-compose -f docker-compose-simples.yml logs -f
    echo.
)

echo.
echo 📋 LOGS EM TEMPO REAL (Ctrl+C para sair):
echo.
docker-compose -f docker-compose-simples.yml logs -f

pause
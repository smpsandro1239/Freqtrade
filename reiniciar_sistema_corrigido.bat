@echo off
echo.
echo ========================================
echo 🔧 REINICIANDO SISTEMA COM CORREÇÕES
echo ========================================
echo.

:: Parar todos os containers
echo 🛑 Parando todos os containers...
docker-compose -f docker-compose-simples.yml down

:: Remover containers antigos para forçar recriação
echo 🗑️ Removendo containers antigos...
docker container prune -f

:: Aguardar um pouco
echo ⏳ Aguardando limpeza...
timeout /t 5 /nobreak >nul

:: Recriar e iniciar containers
echo 🏗️ Recriando containers com configurações corrigidas...
docker-compose -f docker-compose-simples.yml up -d --force-recreate

:: Aguardar inicialização
echo ⏳ Aguardando inicialização completa...
timeout /t 45 /nobreak >nul

:: Verificar status
echo 📊 Verificando status dos containers...
docker-compose -f docker-compose-simples.yml ps

:: Verificar portas
echo 🔍 Verificando portas mapeadas...
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

:: Testar APIs uma por uma
echo.
echo 🧪 Testando APIs individuais...

echo Testando Strategy A (8081)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8081/api/v1/ping
echo.

echo Testando Strategy B (8082)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8082/api/v1/ping
echo.

echo Testando WaveHyperNW (8083)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8083/api/v1/ping
echo.

echo Testando ML Strategy (8084)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8084/api/v1/ping
echo.

echo Testando ML Simple (8085)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8085/api/v1/ping
echo.

echo Testando Multi Timeframe (8086)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8086/api/v1/ping
echo.

echo Testando Wave Enhanced (8087)...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8087/api/v1/ping
echo.

echo.
echo 📋 Verificando logs de erros...
echo.
echo === LOGS STRATEGY A ===
docker logs ft-stratA --tail 10
echo.
echo === LOGS STRATEGY B ===
docker logs ft-stratB --tail 10
echo.

echo ✅ Reinicialização concluída!
echo.
echo 🌐 URLs para testar:
echo   • Strategy A: http://127.0.0.1:8081
echo   • Strategy B: http://127.0.0.1:8082
echo   • WaveHyperNW: http://127.0.0.1:8083
echo   • ML Strategy: http://127.0.0.1:8084
echo   • ML Simple: http://127.0.0.1:8085
echo   • Multi Timeframe: http://127.0.0.1:8086
echo   • Wave Enhanced: http://127.0.0.1:8087
echo.
echo 💡 Se alguma API não responder, verifique os logs:
echo   docker logs ft-[nome-da-estrategia]
echo.

pause
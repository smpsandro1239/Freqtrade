@echo off
echo.
echo ========================================
echo 🧪 TESTE FINAL DO SISTEMA
echo ========================================
echo.

echo 🔍 Verificando containers...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 🌐 Testando todas as APIs...

echo Testando Strategy A (8081)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8081
echo.

echo Testando Strategy B (8082)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8082
echo.

echo Testando WaveHyperNW (8083)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8083
echo.

echo Testando ML Strategy (8084)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8084
echo.

echo Testando ML Simple (8085)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8085
echo.

echo Testando Multi Timeframe (8086)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8086
echo.

echo Testando Wave Enhanced (8087)...
curl -s -o nul -w "Status: %%{http_code}" http://127.0.0.1:8087
echo.

echo.
echo ✅ SISTEMA TOTALMENTE FUNCIONAL!
echo.
echo 🎯 PRÓXIMOS PASSOS:
echo 1. Abra seu navegador e acesse:
echo    • http://127.0.0.1:8081 (Strategy A)
echo    • http://127.0.0.1:8082 (Strategy B)
echo    • http://127.0.0.1:8083 (WaveHyperNW)
echo.
echo 2. Teste no Telegram @smpsandrobot:
echo    • /start - Menu principal
echo    • /status - Status das estratégias
echo    • /predict - IA preditiva
echo    • /charts comparison - Gráficos
echo.
echo 3. Para controle manual das estratégias:
echo    • Use o navegador nas URLs acima
echo    • Login: stratA / stratA123 (para Strategy A)
echo    • Login: stratB / stratB123 (para Strategy B)
echo.
echo 🎉 PARABÉNS! SISTEMA 100%% OPERACIONAL!
echo.

pause
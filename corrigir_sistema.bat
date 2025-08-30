@echo off
echo 🔧 SCRIPT DE CORREÇÃO AUTOMÁTICA
echo.

echo 1. Parando containers...
docker-compose -f docker-compose-simples.yml down

echo 2. Removendo containers antigos...
docker container prune -f

echo 3. Recriando containers...
docker-compose -f docker-compose-simples.yml up -d --force-recreate

echo 4. Aguardando inicialização...
timeout /t 60 /nobreak >nul

echo 5. Verificando status...
docker-compose -f docker-compose-simples.yml ps

echo ✅ Correção concluída!
pause

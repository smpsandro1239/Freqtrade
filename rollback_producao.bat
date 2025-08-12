@echo off
echo.
echo ========================================
echo   ROLLBACK DE PRODUCAO
echo   Voltar para versao anterior
echo ========================================
echo.

REM Verificar se ha backups disponiveis
echo 🔍 Procurando backups disponiveis...
echo.

set backup_found=0
for /d %%i in (backup_pre_update_*) do (
    echo 📦 Backup encontrado: %%i
    set backup_found=1
    set latest_backup=%%i
)

if %backup_found%==0 (
    echo ❌ Nenhum backup encontrado!
    echo    Nao e possivel fazer rollback sem backup.
    echo.
    echo 💡 Para criar backup manual:
    echo    1. Pare o sistema: docker compose down
    echo    2. Copie: .env, user_data/, docker-compose.yml
    echo    3. Reinicie: docker compose up -d
    echo.
    pause
    exit /b 1
)

echo.
echo ⚠️  ATENCAO: ROLLBACK IRA:
echo    - Parar o sistema atual
echo    - Restaurar configuracoes anteriores
echo    - Perder funcionalidades novas (IA, Trading Manual, etc)
echo    - Voltar para versao anterior do codigo
echo.

set /p confirm="Tem certeza que deseja fazer rollback? Digite 'ROLLBACK' para confirmar: "
if not "%confirm%"=="ROLLBACK" (
    echo ❌ Rollback cancelado.
    pause
    exit /b 0
)

echo.
echo 🔄 INICIANDO PROCESSO DE ROLLBACK...
echo.

REM Passo 1: Parar sistema atual
echo 🛑 PASSO 1/5: Parando sistema atual...
docker compose down >nul 2>&1
echo ✅ Sistema parado!
echo.

REM Passo 2: Fazer backup do estado atual (caso precise voltar)
echo 📦 PASSO 2/5: Fazendo backup do estado atual...
set current_backup=backup_before_rollback_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set current_backup=%current_backup: =0%

mkdir %current_backup% 2>nul
if exist .env copy .env %current_backup%\ >nul
if exist user_data xcopy user_data %current_backup%\user_data\ /E /I /Q >nul
if exist docker-compose.yml copy docker-compose.yml %current_backup%\ >nul

echo ✅ Estado atual salvo em: %current_backup%
echo.

REM Passo 3: Restaurar arquivos do backup
echo 📥 PASSO 3/5: Restaurando arquivos do backup...
echo    Usando backup: %latest_backup%

if exist %latest_backup%\.env (
    copy %latest_backup%\.env . >nul
    echo ✅ .env restaurado
) else (
    echo ⚠️  .env nao encontrado no backup
)

if exist %latest_backup%\user_data (
    rmdir /s /q user_data 2>nul
    xcopy %latest_backup%\user_data user_data\ /E /I /Q >nul
    echo ✅ user_data restaurado
) else (
    echo ⚠️  user_data nao encontrado no backup
)

if exist %latest_backup%\docker-compose.yml (
    copy %latest_backup%\docker-compose.yml . >nul
    echo ✅ docker-compose.yml restaurado
) else (
    echo ⚠️  docker-compose.yml nao encontrado no backup
)

echo.

REM Passo 4: Voltar codigo para versao anterior
echo 📤 PASSO 4/5: Voltando codigo para versao anterior...

REM Tentar identificar commit anterior
for /f "tokens=1" %%i in ('git log --oneline -2 ^| tail -1') do set previous_commit=%%i

if not "%previous_commit%"=="" (
    echo    Voltando para commit: %previous_commit%
    git reset --hard %previous_commit% >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Erro ao voltar commit. Continuando...
    ) else (
        echo ✅ Codigo revertido com sucesso!
    )
) else (
    echo ⚠️  Nao foi possivel identificar commit anterior
)

echo.

REM Passo 5: Rebuild e iniciar sistema
echo 🔨 PASSO 5/5: Rebuilding e iniciando sistema...
echo    Rebuilding containers...
docker compose build --no-cache >nul 2>&1

echo    Iniciando sistema...
docker compose up -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar sistema!
    echo    Verificando logs...
    docker compose logs
    pause
    exit /b 1
)

echo ✅ Sistema iniciado!
echo.

REM Verificar status
echo 📊 Verificando status do sistema...
timeout /t 15 /nobreak >nul
docker compose ps

echo.
echo ========================================
echo   ROLLBACK CONCLUIDO!
echo ========================================
echo.

echo ✅ SISTEMA RESTAURADO PARA VERSAO ANTERIOR
echo.
echo ❌ FUNCIONALIDADES PERDIDAS:
echo    - IA Preditiva (/predict)
echo    - Trading Manual (/forcebuy, /forcesell)
echo    - Ajuste Dinamico (/adjust)
echo    - Dashboard Horario melhorado
echo    - Notificacoes automaticas
echo.

echo 📦 BACKUPS DISPONIVEIS:
echo    - Estado anterior: %latest_backup%
echo    - Estado antes do rollback: %current_backup%
echo.

echo 💡 PARA VOLTAR PARA VERSAO NOVA:
echo    1. Execute: .\update_producao.bat
echo    2. Ou restaure manualmente do backup: %current_backup%
echo.

echo 🧪 TESTE O SISTEMA:
echo    /start - Verificar se menu voltou ao normal
echo    /status - Verificar se estrategias funcionam
echo.

set /p test_system="Deseja testar o sistema agora? (S/N): "
if /i "%test_system%"=="S" (
    echo.
    echo 📱 Enviando mensagem de teste...
    
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_CHAT_ID" .env 2^>nul') do set chat_id=%%i
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_TOKEN" .env 2^>nul') do set bot_token=%%i
    
    if not "%chat_id%"=="" if not "%bot_token%"=="" (
        curl -s -X POST "https://api.telegram.org/bot%bot_token%/sendMessage" -d "chat_id=%chat_id%" -d "text=🔄 ROLLBACK CONCLUIDO!%0A%0A✅ Sistema restaurado para versao anterior%0A❌ Funcionalidades novas removidas%0A%0ATestem: /start e /status" >nul 2>&1
        echo ✅ Mensagem enviada para Telegram!
    )
    
    echo.
    echo 🎯 TESTE MANUAL:
    echo    Abra o Telegram e execute: /start
    echo    Verifique se o menu NAO tem [💰 Trading Manual]
    echo.
)

echo.
echo 🔄 ROLLBACK COMPLETO!
echo.
pause
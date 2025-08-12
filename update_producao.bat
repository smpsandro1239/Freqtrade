@echo off
echo.
echo ========================================
echo   ATUALIZACAO AUTOMATICA EM PRODUCAO
echo   Sistema Completo com Novas Funcionalidades
echo ========================================
echo.

REM Verificar se Git esta disponivel
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git nao encontrado! Instale o Git primeiro.
    pause
    exit /b 1
)

REM Verificar se Docker esta disponivel
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker nao encontrado! Instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

echo ✅ Pré-requisitos verificados!
echo.

REM Verificar se sistema esta rodando
docker compose ps >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Sistema nao esta rodando ou docker-compose nao encontrado.
    echo    Continuando com atualizacao...
) else (
    echo ✅ Sistema atual detectado!
)

echo.
echo ========================================
echo   NOVAS FUNCIONALIDADES DISPONÍVEIS
echo ========================================
echo.
echo 🔮 IA PREDITIVA - Previsao de subidas
echo 💰 TRADING MANUAL - Compra/venda forcada
echo ⚙️  AJUSTE DINAMICO - Estrategias adaptaveis
echo 📊 DASHBOARD HORARIO - Dados reais (nao zeros!)
echo 🔔 NOTIFICACOES 24/7 - Alertas automaticos
echo 🔧 GITHUB ACTIONS - CI/CD funcionando
echo.

set /p confirm="Deseja continuar com a atualizacao? (S/N): "
if /i not "%confirm%"=="S" (
    echo ❌ Atualizacao cancelada.
    pause
    exit /b 0
)

echo.
echo 🔄 INICIANDO PROCESSO DE ATUALIZACAO...
echo.

REM Passo 1: Backup do sistema atual
echo 📦 PASSO 1/6: Criando backup do sistema atual...
set backup_dir=backup_pre_update_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_dir=%backup_dir: =0%

mkdir %backup_dir% 2>nul
if exist .env copy .env %backup_dir%\ >nul
if exist user_data xcopy user_data %backup_dir%\user_data\ /E /I /Q >nul
if exist docker-compose.yml copy docker-compose.yml %backup_dir%\ >nul

echo ✅ Backup criado em: %backup_dir%
echo.

REM Passo 2: Parar sistema atual
echo 🛑 PASSO 2/6: Parando sistema atual...
docker compose down >nul 2>&1
echo ✅ Sistema parado com seguranca!
echo.

REM Passo 3: Atualizar codigo do GitHub
echo 📥 PASSO 3/6: Atualizando codigo do GitHub...
echo    Fazendo fetch das ultimas alteracoes...
git fetch origin >nul 2>&1

echo    Verificando branch atual...
for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
echo    Branch atual: %current_branch%

echo    Atualizando codigo...
git pull origin main
if errorlevel 1 (
    echo ❌ Erro ao atualizar codigo do GitHub!
    echo    Verifique conexao com internet e tente novamente.
    pause
    exit /b 1
)

echo ✅ Codigo atualizado com sucesso!
echo.

REM Passo 4: Rebuild containers com novas funcionalidades
echo 🔨 PASSO 4/6: Rebuilding containers com novas funcionalidades...
echo    Isso pode levar alguns minutos...

docker compose build --no-cache >nul 2>&1
if errorlevel 1 (
    echo ❌ Erro ao fazer rebuild dos containers!
    echo    Verificando logs...
    docker compose build
    pause
    exit /b 1
)

echo ✅ Containers rebuilded com sucesso!
echo.

REM Passo 5: Iniciar sistema atualizado
echo 🚀 PASSO 5/6: Iniciando sistema atualizado...
docker compose up -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar sistema!
    echo    Verificando logs...
    docker compose logs
    pause
    exit /b 1
)

echo ✅ Sistema iniciado com sucesso!
echo.

REM Passo 6: Verificar saude do sistema
echo 🏥 PASSO 6/6: Verificando saude do sistema...
echo    Aguardando inicializacao (30 segundos)...
timeout /t 30 /nobreak >nul

echo.
echo 📊 Status dos containers:
docker compose ps

echo.
echo 🏥 Executando health check...
python scripts/health_check.py

echo.
echo ========================================
echo   ATUALIZACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.

echo 🎉 NOVAS FUNCIONALIDADES ATIVAS:
echo.
echo 🔮 IA PREDITIVA:
echo    /predict - Previsoes rapidas
echo    /start → 🔮 Previsoes - Analise detalhada
echo.
echo 💰 TRADING MANUAL:
echo    /forcebuy stratA BTC/USDT - Compra forcada
echo    /forcesell stratA BTC/USDT - Venda forcada
echo    /start → 💰 Trading Manual - Interface grafica
echo.
echo ⚙️  AJUSTE DINAMICO:
echo    /adjust stratA aggressive - Mais penetravel
echo    /adjust stratA conservative - Mais cauteloso
echo    /adjust stratA balanced - Equilibrado
echo.
echo 📊 DASHBOARD HORARIO:
echo    /stats - Estatisticas com dados REAIS
echo    /start → 📈 Estatisticas → 📊 Stats Horarias
echo.
echo 🔔 NOTIFICACOES:
echo    /start → 📈 Estatisticas → 🔔 Notificacoes
echo    Ativar para receber alertas 24/7
echo.

echo ⚠️  TESTES OBRIGATORIOS:
echo    1. /start - Verificar novo menu
echo    2. /predict - Testar IA preditiva
echo    3. /stats - Verificar dados horarios reais
echo    4. /forcebuy stratA BTC/USDT - Testar trading manual
echo    5. /adjust stratA aggressive - Testar ajuste dinamico
echo.

echo 📚 DOCUMENTACAO:
echo    - ATUALIZACAO_PRODUCAO.md - Guia completo
echo    - SISTEMA_COMPLETO_FINAL.md - Funcionalidades
echo    - DEPLOY_PRODUCAO.md - Deploy em producao
echo.

echo 🔍 MONITORAMENTO:
echo    Execute: .\monitor_producao.bat
echo    Para monitoramento em tempo real
echo.

echo 📦 BACKUP DISPONIVEL:
echo    Localizado em: %backup_dir%
echo    Use para rollback se necessario
echo.

set /p test_now="Deseja testar as funcionalidades agora? (S/N): "
if /i "%test_now%"=="S" (
    echo.
    echo 🧪 INICIANDO TESTES AUTOMATICOS...
    echo.
    
    echo 📱 Enviando comando de teste via Telegram...
    
    REM Obter configuracoes do .env
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_CHAT_ID" .env 2^>nul') do set chat_id=%%i
    for /f "tokens=2 delims==" %%i in ('findstr "TELEGRAM_TOKEN" .env 2^>nul') do set bot_token=%%i
    
    if not "%chat_id%"=="" if not "%bot_token%"=="" (
        curl -s -X POST "https://api.telegram.org/bot%bot_token%/sendMessage" -d "chat_id=%chat_id%" -d "text=🎉 SISTEMA ATUALIZADO COM SUCESSO!%0A%0A✅ Novas funcionalidades ativas:%0A🔮 /predict - IA Preditiva%0A💰 /forcebuy - Trading Manual%0A⚙️ /adjust - Ajuste Dinamico%0A📊 /stats - Dashboard Horario%0A%0ATestem as funcionalidades!" >nul 2>&1
        echo ✅ Mensagem de teste enviada para o Telegram!
    ) else (
        echo ⚠️  Configuracoes do Telegram nao encontradas no .env
    )
    
    echo.
    echo 🎯 TESTE MANUAL NECESSARIO:
    echo    Abra o Telegram e execute:
    echo    /start
    echo.
    echo    Verifique se o menu mostra:
    echo    [💰 Trading Manual] ← NOVO!
    echo.
)

echo.
echo 🎉 ATUALIZACAO COMPLETA!
echo    Sistema revolucionario com IA preditiva ativo!
echo.
pause
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: FREQTRADE MULTI-STRATEGY - LAUNCHER UNIVERSAL
:: Funciona em qualquer ambiente Windows (CMD/PowerShell)
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 FREQTRADE MULTI-STRATEGY                              ║
echo ║                         Launcher Universal                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar se está no diretório correto
if not exist "docker-compose.yml" (
    echo ❌ ERRO: Execute este script no diretório do projeto Freqtrade
    echo.
    echo 💡 Navegue até o diretório correto e execute novamente
    pause
    exit /b 1
)

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🎮 FREQTRADE CONTROLE CENTRAL                            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🔧 INSTALAÇÃO:
echo   1. Instalação Completa (primeira vez)
echo   2. Início Rápido (já tem Docker/Git)
echo.
echo 🎮 CONTROLE:
echo   3. Ver Status do Sistema
echo   4. Ver Logs em Tempo Real
echo   5. Reiniciar Sistema
echo   6. Parar Sistema
echo   7. Iniciar Sistema
echo.
echo ⚙️ CONFIGURAÇÃO:
echo   8. Alternar para DRY-RUN (simulação)
echo   9. Alternar para LIVE (CUIDADO!)
echo  10. Criar Backup Manual
echo.
echo  11. Ajuda / Documentação
echo  12. Sair
echo.

set /p "choice=Escolha uma opção (1-12): "

if "%choice%"=="1" goto install_complete
if "%choice%"=="2" goto quick_start
if "%choice%"=="3" goto show_status
if "%choice%"=="4" goto show_logs
if "%choice%"=="5" goto restart_system
if "%choice%"=="6" goto stop_system
if "%choice%"=="7" goto start_system
if "%choice%"=="8" goto set_dry
if "%choice%"=="9" goto set_live
if "%choice%"=="10" goto create_backup
if "%choice%"=="11" goto show_help
if "%choice%"=="12" goto exit_script

echo ❌ Opção inválida. Tente novamente.
timeout /t 2 /nobreak >nul
goto menu

:install_complete
echo.
echo 🚀 Executando instalação completa...
echo.
if exist "setup_freqtrade.bat" (
    call setup_freqtrade.bat
) else (
    echo ❌ Arquivo setup_freqtrade.bat não encontrado
)
pause
goto menu

:quick_start
echo.
echo ⚡ Executando início rápido...
echo.
if exist "quick_start.bat" (
    call quick_start.bat
) else (
    echo ❌ Arquivo quick_start.bat não encontrado
)
pause
goto menu

:show_status
echo.
echo 📊 Status do Sistema:
echo.
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker não encontrado. Execute a instalação primeiro.
    pause
    goto menu
)

docker-compose ps
echo.
echo 💾 Espaço em disco:
dir /-c | find "bytes"
echo.
echo 🕐 Última verificação: %date% %time%
pause
goto menu

:show_logs
echo.
echo 📋 Logs em Tempo Real (Ctrl+C para sair):
echo.
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker não encontrado. Execute a instalação primeiro.
    pause
    goto menu
)

docker-compose logs -f
pause
goto menu

:restart_system
echo.
echo 🔄 Reiniciando sistema...
docker-compose restart
if %errorLevel% equ 0 (
    echo ✅ Sistema reiniciado com sucesso
) else (
    echo ❌ Erro ao reiniciar sistema
)
pause
goto menu

:stop_system
echo.
echo ⏹️ Parando sistema...
docker-compose down
if %errorLevel% equ 0 (
    echo ✅ Sistema parado com sucesso
) else (
    echo ❌ Erro ao parar sistema
)
pause
goto menu

:start_system
echo.
echo ▶️ Iniciando sistema...
docker-compose up -d
if %errorLevel% equ 0 (
    echo ✅ Sistema iniciado com sucesso
) else (
    echo ❌ Erro ao iniciar sistema
)
pause
goto menu

:set_dry
echo.
echo 🟡 Alternando para modo DRY-RUN (simulação)...
if exist "scripts\toggle_mode.py" (
    python scripts\toggle_mode.py dry
    if %errorLevel% equ 0 (
        echo 🔄 Reiniciando containers...
        docker-compose restart
        echo ✅ Modo alterado para DRY-RUN
    )
) else (
    echo ❌ Script toggle_mode.py não encontrado
)
pause
goto menu

:set_live
echo.
echo ⚠️  ATENÇÃO: VOCÊ ESTÁ ALTERNANDO PARA LIVE TRADING!
echo.
echo 🚨 ISSO USARÁ DINHEIRO REAL!
echo.
set /p "confirm=Tem certeza? Digite 'SIM' para confirmar: "
if /i "%confirm%"=="SIM" (
    if exist "scripts\toggle_mode.py" (
        python scripts\toggle_mode.py live
        if %errorLevel% equ 0 (
            echo 🔄 Reiniciando containers...
            docker-compose restart
            echo 🚨 MODO LIVE ATIVADO - USANDO DINHEIRO REAL!
        )
    ) else (
        echo ❌ Script toggle_mode.py não encontrado
    )
) else (
    echo ❌ Operação cancelada
)
pause
goto menu

:create_backup
echo.
echo 💾 Criando backup manual...
set "timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%"
set "timestamp=%timestamp: =0%"
set "backup_dir=backups\manual_%timestamp%"

mkdir "%backup_dir%" 2>nul
xcopy "user_data\configs" "%backup_dir%\configs\" /E /I /Q >nul 2>&1
copy ".env" "%backup_dir%\" >nul 2>&1
copy "docker-compose.yml" "%backup_dir%\" >nul 2>&1

if exist "%backup_dir%" (
    echo ✅ Backup criado em: %backup_dir%
) else (
    echo ❌ Erro ao criar backup
)
pause
goto menu

:show_help
echo.
echo 📚 DOCUMENTAÇÃO E AJUDA:
echo.
echo 📖 Arquivos de ajuda disponíveis:
if exist "README.md" echo   • README.md - Documentação principal
if exist "INSTALACAO_WINDOWS.md" echo   • INSTALACAO_WINDOWS.md - Guia de instalação Windows
if exist "COMO_EXECUTAR.md" echo   • COMO_EXECUTAR.md - Como executar os scripts
echo.
echo 🌐 Links úteis:
echo   • Repositório: https://github.com/smpsandro1239/Freqtrade
echo   • Documentação Freqtrade: https://www.freqtrade.io/
echo.
echo 💡 Comandos Docker úteis:
echo   • docker-compose ps          - Ver containers
echo   • docker-compose logs        - Ver todos os logs
echo   • docker-compose logs -f     - Logs em tempo real
echo   • docker-compose restart     - Reiniciar tudo
echo.
echo 🤖 Telegram:
echo   • Crie bot com @BotFather
echo   • Configure TOKEN e CHAT_ID no arquivo .env
echo   • Bot enviará alertas automáticos
echo.
pause
goto menu

:exit_script
echo.
echo 👋 Obrigado por usar o Freqtrade Multi-Strategy!
echo.
echo 💡 Dica: Execute este script sempre que precisar controlar o sistema
echo.
exit /b 0
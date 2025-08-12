@echo off
echo.
echo ========================================
echo   TESTE SIMPLES DE COMUNICACAO TELEGRAM
echo ========================================
echo.

REM Configuracoes
set TELEGRAM_TOKEN=7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs
set TELEGRAM_CHAT_ID=1555333079

echo 🔧 Configuracoes:
echo    Token: %TELEGRAM_TOKEN:~0,15%...
echo    Chat ID: %TELEGRAM_CHAT_ID%
echo.

REM Teste 1: Informacoes do Bot
echo 🤖 Testando informacoes do bot...
curl -s "https://api.telegram.org/bot%TELEGRAM_TOKEN%/getMe" > bot_info.json

findstr "ok.*true" bot_info.json >nul
if errorlevel 1 (
    echo ❌ Bot nao encontrado ou token invalido!
    type bot_info.json
    del bot_info.json
    pause
    exit /b 1
) else (
    echo ✅ Bot encontrado e ativo!
    for /f "tokens=2 delims=:" %%i in ('findstr "username" bot_info.json') do (
        set username=%%i
        set username=!username:"=!
        set username=!username:,=!
        echo    Username: @!username!
    )
)

del bot_info.json
echo.

REM Teste 2: Envio de mensagem simples
echo 📱 Enviando mensagem de teste...

set message=🎉 TESTE DE COMUNICACAO TELEGRAM^

✅ Bot funcionando corretamente!^
🕐 Horario: %time%^
📅 Data: %date%^

🚀 Sistema Freqtrade Commander ativo!^

Comandos disponiveis:^
/start - Menu principal^
/status - Status das estrategias^
/predict - Previsoes de IA^
/stats - Estatisticas^
/help - Ajuda

curl -s -X POST "https://api.telegram.org/bot%TELEGRAM_TOKEN%/sendMessage" -d "chat_id=%TELEGRAM_CHAT_ID%" -d "text=%message%" > send_result.json

findstr "ok.*true" send_result.json >nul
if errorlevel 1 (
    echo ❌ Erro ao enviar mensagem!
    type send_result.json
    del send_result.json
    pause
    exit /b 1
) else (
    echo ✅ Mensagem enviada com sucesso!
    for /f "tokens=2 delims=:" %%i in ('findstr "message_id" send_result.json') do (
        set msg_id=%%i
        set msg_id=!msg_id:,=!
        echo    Message ID: !msg_id!
    )
)

del send_result.json
echo.

REM Teste 3: Status do sistema
echo 🏥 Enviando status do sistema...

set status_msg=🏥 STATUS DO SISTEMA FREQTRADE^

🕐 Verificacao: %time% - %date%^

🤖 Telegram Bot: ✅ Funcionando^
📡 Comunicacao: ✅ Estabelecida^
⚙️ Sistema: 🔄 Inicializando^

📋 Proximos passos:^
1. Iniciar containers Docker^
2. Configurar estrategias^
3. Ativar monitoramento^

💡 Para iniciar o sistema completo:^
   Execute: docker compose up -d^

🎯 Comandos disponiveis apos inicializacao:^
/start - Menu principal^
/status - Status das estrategias^
/predict - Previsoes de IA^
/stats - Estatisticas detalhadas^
/help - Lista completa de comandos

curl -s -X POST "https://api.telegram.org/bot%TELEGRAM_TOKEN%/sendMessage" -d "chat_id=%TELEGRAM_CHAT_ID%" -d "text=%status_msg%" > status_result.json

findstr "ok.*true" status_result.json >nul
if errorlevel 1 (
    echo ❌ Erro ao enviar status!
    type status_result.json
) else (
    echo ✅ Status do sistema enviado!
)

del status_result.json
echo.

REM Teste 4: Menu com botoes
echo ⌨️ Enviando menu interativo...

set menu_msg=🎮 TESTE DO MENU INTERATIVO^

Escolha uma opcao:

set keyboard={"inline_keyboard":[[{"text":"📊 Status","callback_data":"status"},{"text":"📈 Stats","callback_data":"stats"}],[{"text":"🔮 Previsoes","callback_data":"predict"},{"text":"💰 Trading","callback_data":"trading"}],[{"text":"✅ Teste OK","callback_data":"test_ok"}]]}

curl -s -X POST "https://api.telegram.org/bot%TELEGRAM_TOKEN%/sendMessage" -d "chat_id=%TELEGRAM_CHAT_ID%" -d "text=%menu_msg%" -d "reply_markup=%keyboard%" > menu_result.json

findstr "ok.*true" menu_result.json >nul
if errorlevel 1 (
    echo ❌ Erro ao enviar menu!
    type menu_result.json
) else (
    echo ✅ Menu interativo enviado!
    echo    Clique nos botoes para testar
)

del menu_result.json
echo.

echo ========================================
echo   TESTE CONCLUIDO!
echo ========================================
echo.

echo 🎉 COMUNICACAO TELEGRAM ESTABELECIDA!
echo.
echo 📱 VERIFIQUE SEU TELEGRAM:
echo    - Voce deve ter recebido mensagens de teste
echo    - Deve haver um menu interativo
echo    - Status do sistema foi enviado
echo.

echo 🚀 PROXIMO PASSO:
echo    Execute: .\iniciar_sistema_telegram.bat
echo    Ou: docker compose up -d
echo    Depois teste: /start no Telegram
echo.

echo 💡 COMANDOS PARA TESTAR NO TELEGRAM:
echo    /start - Menu principal
echo    /status - Status das estrategias
echo    /predict - Previsoes de IA
echo    /help - Ajuda completa
echo.

set /p iniciar="Deseja iniciar o sistema completo agora? (S/N): "
if /i "%iniciar%"=="S" (
    echo.
    echo 🚀 Iniciando sistema completo...
    call iniciar_sistema_telegram.bat
) else (
    echo.
    echo 👋 Para iniciar depois, execute:
    echo    .\iniciar_sistema_telegram.bat
    echo.
    pause
)
# Teste de Comunicação Telegram - PowerShell
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   TESTE DE COMUNICAÇÃO TELEGRAM" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$TELEGRAM_TOKEN = "7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs"
$TELEGRAM_CHAT_ID = "1555333079"

Write-Host "🔧 CONFIGURAÇÕES:" -ForegroundColor Yellow
Write-Host "   Token: $($TELEGRAM_TOKEN.Substring(0,15))..." -ForegroundColor Gray
Write-Host "   Chat ID: $TELEGRAM_CHAT_ID" -ForegroundColor Gray
Write-Host ""

# Teste 1: Informações do Bot
Write-Host "🤖 TESTANDO INFORMAÇÕES DO BOT..." -ForegroundColor Yellow

try {
    $url = "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe"
    $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
    
    if ($response.ok) {
        Write-Host "✅ Bot ativo: @$($response.result.username)" -ForegroundColor Green
        Write-Host "   Nome: $($response.result.first_name)" -ForegroundColor Gray
        Write-Host "   ID: $($response.result.id)" -ForegroundColor Gray
        $botTest = $true
    } else {
        Write-Host "❌ Erro na API: $($response.description)" -ForegroundColor Red
        $botTest = $false
    }
} catch {
    Write-Host "❌ Erro de conexão: $($_.Exception.Message)" -ForegroundColor Red
    $botTest = $false
}

Write-Host ""

# Teste 2: Envio de Mensagem
Write-Host "📱 TESTANDO ENVIO DE MENSAGEM..." -ForegroundColor Yellow

$message = @"
🎉 TESTE DE COMUNICAÇÃO TELEGRAM

✅ Bot funcionando corretamente!
🕐 Horário: $(Get-Date -Format 'HH:mm:ss')
📅 Data: $(Get-Date -Format 'dd/MM/yyyy')

🚀 Sistema Freqtrade Commander ativo!

Comandos disponíveis:
/start - Menu principal
/status - Status das estratégias
/predict - Previsões de IA
/stats - Estatísticas
/help - Ajuda
"@

try {
    $url = "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage"
    $body = @{
        chat_id = $TELEGRAM_CHAT_ID
        text = $message
        parse_mode = "HTML"
    }
    
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -TimeoutSec 10
    
    if ($response.ok) {
        Write-Host "✅ Mensagem enviada com sucesso!" -ForegroundColor Green
        Write-Host "   Message ID: $($response.result.message_id)" -ForegroundColor Gray
        $messageTest = $true
    } else {
        Write-Host "❌ Erro ao enviar: $($response.description)" -ForegroundColor Red
        $messageTest = $false
    }
} catch {
    Write-Host "❌ Erro ao enviar mensagem: $($_.Exception.Message)" -ForegroundColor Red
    $messageTest = $false
}

Write-Host ""

# Teste 3: Menu Interativo
Write-Host "⌨️ TESTANDO MENU INTERATIVO..." -ForegroundColor Yellow

$menuMessage = "🎮 TESTE DO MENU INTERATIVO`n`nEscolha uma opção:"

$keyboard = @{
    inline_keyboard = @(
        @(
            @{ text = "📊 Status"; callback_data = "status" },
            @{ text = "📈 Stats"; callback_data = "stats" }
        ),
        @(
            @{ text = "🔮 Previsões"; callback_data = "predict" },
            @{ text = "💰 Trading"; callback_data = "trading" }
        ),
        @(
            @{ text = "✅ Teste OK"; callback_data = "test_ok" }
        )
    )
}

try {
    $url = "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage"
    $body = @{
        chat_id = $TELEGRAM_CHAT_ID
        text = $menuMessage
        reply_markup = ($keyboard | ConvertTo-Json -Depth 10)
    }
    
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -TimeoutSec 10
    
    if ($response.ok) {
        Write-Host "✅ Menu interativo enviado!" -ForegroundColor Green
        Write-Host "   Clique nos botões para testar" -ForegroundColor Gray
        $menuTest = $true
    } else {
        Write-Host "❌ Erro ao enviar menu: $($response.description)" -ForegroundColor Red
        $menuTest = $false
    }
} catch {
    Write-Host "❌ Erro ao enviar menu: $($_.Exception.Message)" -ForegroundColor Red
    $menuTest = $false
}

Write-Host ""

# Teste 4: Status do Sistema
Write-Host "🏥 ENVIANDO STATUS DO SISTEMA..." -ForegroundColor Yellow

$statusMessage = @"
🏥 STATUS DO SISTEMA FREQTRADE

🕐 Verificação: $(Get-Date -Format 'HH:mm:ss - dd/MM/yyyy')

🤖 Telegram Bot: ✅ Funcionando
📡 Comunicação: ✅ Estabelecida
⚙️ Sistema: 🔄 Inicializando

📋 Próximos passos:
1. Iniciar containers Docker
2. Configurar estratégias
3. Ativar monitoramento

💡 Para iniciar o sistema completo:
   Execute: docker compose up -d

🎯 Comandos disponíveis após inicialização:
/start - Menu principal
/status - Status das estratégias  
/predict - Previsões de IA
/stats - Estatísticas detalhadas
/help - Lista completa de comandos
"@

try {
    $url = "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage"
    $body = @{
        chat_id = $TELEGRAM_CHAT_ID
        text = $statusMessage
    }
    
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -TimeoutSec 10
    
    if ($response.ok) {
        Write-Host "✅ Status do sistema enviado!" -ForegroundColor Green
        $statusTest = $true
    } else {
        Write-Host "❌ Erro ao enviar status: $($response.description)" -ForegroundColor Red
        $statusTest = $false
    }
} catch {
    Write-Host "❌ Erro ao enviar status: $($_.Exception.Message)" -ForegroundColor Red
    $statusTest = $false
}

Write-Host ""

# Resultado Final
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📋 RESULTADO DOS TESTES:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$testsTotal = 4
$testsPassed = 0

if ($botTest) { $testsPassed++ }
if ($messageTest) { $testsPassed++ }
if ($menuTest) { $testsPassed++ }
if ($statusTest) { $testsPassed++ }

Write-Host ""
Write-Host "✅ Testes passaram: $testsPassed/$testsTotal" -ForegroundColor $(if ($testsPassed -eq $testsTotal) { "Green" } else { "Yellow" })

if ($testsPassed -eq $testsTotal) {
    Write-Host ""
    Write-Host "🎉 COMUNICAÇÃO TELEGRAM 100% FUNCIONAL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 VERIFIQUE SEU TELEGRAM:" -ForegroundColor Yellow
    Write-Host "   - Você deve ter recebido mensagens de teste" -ForegroundColor Gray
    Write-Host "   - Deve haver um menu interativo" -ForegroundColor Gray
    Write-Host "   - Status do sistema foi enviado" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🚀 PRÓXIMO PASSO:" -ForegroundColor Yellow
    Write-Host "   Execute: .\iniciar_sistema_telegram.bat" -ForegroundColor Gray
    Write-Host "   Ou: docker compose up -d" -ForegroundColor Gray
    Write-Host "   Depois teste: /start no Telegram" -ForegroundColor Gray
} elseif ($testsPassed -ge 2) {
    Write-Host ""
    Write-Host "⚠️  COMUNICAÇÃO PARCIALMENTE FUNCIONAL" -ForegroundColor Yellow
    Write-Host "   Alguns testes falharam, mas o básico funciona" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ PROBLEMAS NA COMUNICAÇÃO" -ForegroundColor Red
    Write-Host "   Verifique TOKEN e CHAT_ID no arquivo .env" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 COMANDOS PARA TESTAR NO TELEGRAM:" -ForegroundColor Yellow
Write-Host "   /start - Menu principal" -ForegroundColor Gray
Write-Host "   /status - Status das estratégias" -ForegroundColor Gray
Write-Host "   /predict - Previsões de IA" -ForegroundColor Gray
Write-Host "   /help - Ajuda completa" -ForegroundColor Gray
Write-Host ""

# Perguntar se quer iniciar o sistema
$iniciar = Read-Host "Deseja iniciar o sistema completo agora? (S/N)"
if ($iniciar -eq "S" -or $iniciar -eq "s") {
    Write-Host ""
    Write-Host "🚀 Iniciando sistema completo..." -ForegroundColor Green
    & ".\iniciar_sistema_telegram.bat"
} else {
    Write-Host ""
    Write-Host "👋 Para iniciar depois, execute:" -ForegroundColor Yellow
    Write-Host "   .\iniciar_sistema_telegram.bat" -ForegroundColor Gray
    Write-Host ""
}
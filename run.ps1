# PowerShell Script para executar Freqtrade Multi-Strategy
# Resolve o problema de execução de .bat no PowerShell

param(
    [Parameter(Position=0)]
    [string]$Action = "menu"
)

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    🚀 FREQTRADE MULTI-STRATEGY                              ║" -ForegroundColor Cyan
Write-Host "║                         PowerShell Launcher                                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ ERRO: Execute este script no diretório do projeto Freqtrade" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Navegue até o diretório correto:" -ForegroundColor Yellow
    Write-Host "cd C:\caminho\para\Freqtrade-MultiStrategy" -ForegroundColor Gray
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

function Show-Menu {
    Write-Host "📋 OPÇÕES DISPONÍVEIS:" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 INSTALAÇÃO:" -ForegroundColor Yellow
    Write-Host "  1. setup     - Instalação completa (primeira vez)" -ForegroundColor White
    Write-Host "  2. quick     - Início rápido (já tem Docker/Git)" -ForegroundColor White
    Write-Host "  3. vps       - Setup para VPS (com parâmetros)" -ForegroundColor White
    Write-Host ""
    Write-Host "🎮 CONTROLE:" -ForegroundColor Yellow
    Write-Host "  4. status    - Ver status do sistema" -ForegroundColor White
    Write-Host "  5. logs      - Ver logs em tempo real" -ForegroundColor White
    Write-Host "  6. restart   - Reiniciar sistema" -ForegroundColor White
    Write-Host "  7. stop      - Parar sistema" -ForegroundColor White
    Write-Host "  8. start     - Iniciar sistema" -ForegroundColor White
    Write-Host ""
    Write-Host "⚙️ CONFIGURAÇÃO:" -ForegroundColor Yellow
    Write-Host "  9. dry       - Alternar para DRY-RUN" -ForegroundColor White
    Write-Host " 10. live      - Alternar para LIVE (CUIDADO!)" -ForegroundColor White
    Write-Host " 11. backup    - Criar backup manual" -ForegroundColor White
    Write-Host ""
    Write-Host " 12. exit      - Sair" -ForegroundColor White
    Write-Host ""
}

function Execute-Setup {
    Write-Host "🚀 Executando instalação completa..." -ForegroundColor Green
    if (Test-Path "setup_freqtrade.bat") {
        Start-Process -FilePath "setup_freqtrade.bat" -Verb RunAs -Wait
    } else {
        Write-Host "❌ Arquivo setup_freqtrade.bat não encontrado" -ForegroundColor Red
    }
}

function Execute-Quick {
    Write-Host "⚡ Executando início rápido..." -ForegroundColor Green
    if (Test-Path "quick_start.bat") {
        & ".\quick_start.bat"
    } else {
        Write-Host "❌ Arquivo quick_start.bat não encontrado" -ForegroundColor Red
    }
}

function Show-VpsHelp {
    Write-Host "🖥️ SETUP VPS - Como usar:" -ForegroundColor Green
    Write-Host ""
    Write-Host "Sintaxe:" -ForegroundColor Yellow
    Write-Host ".\setup_vps.bat [TELEGRAM_TOKEN] [CHAT_ID] [EXCHANGE_KEY] [SECRET]" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Exemplo com exchange:" -ForegroundColor Yellow
    Write-Host '.\setup_vps.bat "123456:ABC-DEF" "-1001234567890" "api_key" "api_secret"' -ForegroundColor Gray
    Write-Host ""
    Write-Host "Exemplo só dry-run:" -ForegroundColor Yellow
    Write-Host '.\setup_vps.bat "123456:ABC-DEF" "-1001234567890" "" ""' -ForegroundColor Gray
    Write-Host ""
}

function Execute-DockerCommand {
    param([string]$Command)
    
    # Verificar se Docker está disponível
    try {
        docker --version | Out-Null
    } catch {
        Write-Host "❌ Docker não encontrado. Execute a instalação primeiro." -ForegroundColor Red
        return
    }
    
    switch ($Command) {
        "status" {
            Write-Host "📊 Status do sistema:" -ForegroundColor Green
            docker-compose ps
        }
        "logs" {
            Write-Host "📋 Logs em tempo real (Ctrl+C para sair):" -ForegroundColor Green
            docker-compose logs -f
        }
        "restart" {
            Write-Host "🔄 Reiniciando sistema..." -ForegroundColor Green
            docker-compose restart
            Write-Host "✅ Sistema reiniciado" -ForegroundColor Green
        }
        "stop" {
            Write-Host "⏹️ Parando sistema..." -ForegroundColor Green
            docker-compose down
            Write-Host "✅ Sistema parado" -ForegroundColor Green
        }
        "start" {
            Write-Host "▶️ Iniciando sistema..." -ForegroundColor Green
            docker-compose up -d
            Write-Host "✅ Sistema iniciado" -ForegroundColor Green
        }
    }
}

function Execute-Toggle {
    param([string]$Mode)
    
    if (Test-Path "scripts/toggle_mode.py") {
        Write-Host "⚖️ Alternando para modo $Mode..." -ForegroundColor Green
        python scripts/toggle_mode.py $Mode
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "🔄 Reiniciando containers..." -ForegroundColor Green
            docker-compose restart
            Write-Host "✅ Modo alterado para $Mode" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ Script toggle_mode.py não encontrado" -ForegroundColor Red
    }
}

function Create-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups/manual_$timestamp"
    
    Write-Host "💾 Criando backup..." -ForegroundColor Green
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Copy-Item -Path "user_data/configs" -Destination "$backupDir/configs" -Recurse -Force
    Copy-Item -Path ".env" -Destination "$backupDir/" -Force -ErrorAction SilentlyContinue
    Copy-Item -Path "docker-compose.yml" -Destination "$backupDir/" -Force
    
    Write-Host "✅ Backup criado em: $backupDir" -ForegroundColor Green
}

# Processar ação
switch ($Action.ToLower()) {
    "menu" {
        do {
            Show-Menu
            $choice = Read-Host "Escolha uma opção (1-12)"
            
            switch ($choice) {
                "1" { Execute-Setup }
                "2" { Execute-Quick }
                "3" { Show-VpsHelp }
                "4" { Execute-DockerCommand "status" }
                "5" { Execute-DockerCommand "logs" }
                "6" { Execute-DockerCommand "restart" }
                "7" { Execute-DockerCommand "stop" }
                "8" { Execute-DockerCommand "start" }
                "9" { Execute-Toggle "dry" }
                "10" { Execute-Toggle "live" }
                "11" { Create-Backup }
                "12" { Write-Host "👋 Até logo!" -ForegroundColor Green; exit }
                default { Write-Host "❌ Opção inválida" -ForegroundColor Red }
            }
            
            if ($choice -ne "12") {
                Write-Host ""
                Read-Host "Pressione Enter para continuar"
                Clear-Host
            }
        } while ($choice -ne "12")
    }
    "setup" { Execute-Setup }
    "quick" { Execute-Quick }
    "vps" { Show-VpsHelp }
    "status" { Execute-DockerCommand "status" }
    "logs" { Execute-DockerCommand "logs" }
    "restart" { Execute-DockerCommand "restart" }
    "stop" { Execute-DockerCommand "stop" }
    "start" { Execute-DockerCommand "start" }
    "dry" { Execute-Toggle "dry" }
    "live" { Execute-Toggle "live" }
    "backup" { Create-Backup }
    default {
        Write-Host "❌ Ação desconhecida: $Action" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Ações disponíveis:" -ForegroundColor Yellow
        Write-Host ".\run.ps1 setup    - Instalação completa" -ForegroundColor Gray
        Write-Host ".\run.ps1 quick    - Início rápido" -ForegroundColor Gray
        Write-Host ".\run.ps1 status   - Ver status" -ForegroundColor Gray
        Write-Host ".\run.ps1 logs     - Ver logs" -ForegroundColor Gray
        Write-Host ".\run.ps1          - Menu interativo" -ForegroundColor Gray
    }
}
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: LIMPEZA DE ARQUIVOS SENSÍVEIS
:: Remove arquivos que não devem estar no repositório
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🧹 LIMPEZA DE ARQUIVOS SENSÍVEIS                     ║
echo ║                                                                              ║
echo ║  Remove arquivos que podem conter informações sensíveis                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo ⚠️  ATENÇÃO: Este script vai remover arquivos sensíveis
echo.
echo Arquivos que serão removidos:
echo • *.log (logs podem conter informações de debug)
echo • backups/ (backups podem conter credenciais)
echo • *.tmp, *.temp (arquivos temporários)
echo • __pycache__/ (cache Python)
echo • .DS_Store (arquivos de sistema Mac)
echo.

set /p "confirm=Continuar? (s/N): "
if /i not "%confirm%"=="s" (
    echo ❌ Operação cancelada
    pause
    exit /b 0
)

echo.
echo 🧹 Iniciando limpeza...

:: Remover logs
echo 📋 Removendo arquivos de log...
if exist "*.log" (
    del /q *.log 2>nul
    echo ✅ Logs removidos
) else (
    echo ℹ️  Nenhum log encontrado
)

:: Remover backups
echo 💾 Removendo backups...
if exist "backups" (
    rmdir /s /q backups 2>nul
    echo ✅ Pasta backups removida
) else (
    echo ℹ️  Pasta backups não encontrada
)

:: Remover arquivos temporários
echo 🗑️ Removendo arquivos temporários...
if exist "*.tmp" del /q *.tmp 2>nul
if exist "*.temp" del /q *.temp 2>nul
if exist "Thumbs.db" del /q Thumbs.db 2>nul
if exist ".DS_Store" del /q .DS_Store 2>nul
echo ✅ Arquivos temporários removidos

:: Remover cache Python
echo 🐍 Removendo cache Python...
if exist "__pycache__" (
    rmdir /s /q __pycache__ 2>nul
    echo ✅ Cache Python removido
) else (
    echo ℹ️  Cache Python não encontrado
)

:: Remover arquivos de instalação baixados
echo 📦 Removendo instaladores baixados...
if exist "DockerInstaller.exe" del /q DockerInstaller.exe 2>nul
if exist "GitInstaller.exe" del /q GitInstaller.exe 2>nul
echo ✅ Instaladores removidos

:: Verificar se .env está sendo rastreado
echo 🔍 Verificando .env...
git ls-files | findstr ".env" >nul 2>&1
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: .env está sendo rastreado pelo Git!
    echo 🔧 Removendo do Git...
    git rm --cached .env 2>nul
    echo ✅ .env removido do Git
) else (
    echo ✅ .env não está sendo rastreado
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            ✅ LIMPEZA CONCLUÍDA                             ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🎉 Arquivos sensíveis removidos com sucesso!
echo.
echo 💡 Próximos passos:
echo 1. Execute: check_security.bat para verificar
echo 2. Faça commit das mudanças se necessário
echo 3. Mantenha o .gitignore atualizado
echo.

pause
exit /b 0
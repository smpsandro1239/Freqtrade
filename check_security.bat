@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: VERIFICADOR DE SEGURANÇA - FREQTRADE
:: Verifica se há arquivos sensíveis no repositório
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🔒 VERIFICADOR DE SEGURANÇA                          ║
echo ║                                                                              ║
echo ║  Verifica se há arquivos sensíveis que podem vazar credenciais              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

set "ISSUES_FOUND=0"

echo 🔍 Verificando arquivos sensíveis...
echo.

:: ============================================================================
:: VERIFICAR ARQUIVOS DE CREDENCIAIS
:: ============================================================================
echo 🔐 Verificando arquivos de credenciais:

if exist ".env" (
    echo ⚠️  ENCONTRADO: .env ^(arquivo de credenciais^)
    echo    💡 Verifique se está no .gitignore
    set /a ISSUES_FOUND+=1
)

if exist "config.json" (
    echo ⚠️  ENCONTRADO: config.json ^(pode conter credenciais^)
    set /a ISSUES_FOUND+=1
)

for %%f in (user_data\configs\*.json) do (
    echo ⚠️  ENCONTRADO: %%f ^(configuração de estratégia^)
    echo    💡 Pode conter chaves de API
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR BANCOS DE DADOS
:: ============================================================================
echo.
echo 💾 Verificando bancos de dados:

for %%f in (*.sqlite *.db) do (
    echo ⚠️  ENCONTRADO: %%f ^(banco de dados de trades^)
    echo    💡 Contém histórico financeiro sensível
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR LOGS
:: ============================================================================
echo.
echo 📋 Verificando logs:

for %%f in (*.log) do (
    echo ⚠️  ENCONTRADO: %%f ^(arquivo de log^)
    echo    💡 Pode conter informações de debug sensíveis
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR BACKUPS
:: ============================================================================
echo.
echo 💾 Verificando backups:

if exist "backups" (
    echo ⚠️  ENCONTRADO: pasta backups/ ^(backups podem conter dados sensíveis^)
    set /a ISSUES_FOUND+=1
)

for %%f in (*.backup *.bak) do (
    echo ⚠️  ENCONTRADO: %%f ^(arquivo de backup^)
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR CHAVES E CERTIFICADOS
:: ============================================================================
echo.
echo 🔑 Verificando chaves e certificados:

for %%f in (*.key *.pem *.crt) do (
    echo 🚨 CRÍTICO: %%f ^(chave/certificado^)
    echo    💡 NUNCA deve estar no repositório!
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR STATUS DO GIT
:: ============================================================================
echo.
echo 📦 Verificando status do Git:

git status --porcelain 2>nul | findstr /C:".env" >nul
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: .env está sendo rastreado pelo Git!
    echo    💡 Execute: git rm --cached .env
    set /a ISSUES_FOUND+=1
)

git status --porcelain 2>nul | findstr /C:".sqlite" >nul
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: Arquivos .sqlite estão sendo rastreados!
    echo    💡 Execute: git rm --cached *.sqlite
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR HISTÓRICO DO GIT
:: ============================================================================
echo.
echo 📚 Verificando histórico do Git:

git ls-files | findstr /E ".env" >nul 2>&1
if !errorLevel! equ 0 (
    echo 🚨 CRÍTICO: .env está sendo rastreado pelo Git!
    echo    💡 Execute: git rm --cached .env
    set /a ISSUES_FOUND+=1
)

:: ============================================================================
:: VERIFICAR CONTEÚDO DE ARQUIVOS
:: ============================================================================
echo.
echo 🔍 Verificando conteúdo suspeito:

for %%f in (*.py *.js *.json *.yml *.yaml) do (
    if exist "%%f" (
        findstr /i "password\|secret\|token\|api_key\|private_key" "%%f" >nul 2>&1
        if !errorLevel! equ 0 (
            echo ⚠️  SUSPEITO: %%f contém palavras sensíveis
            echo    💡 Verifique se não há credenciais hardcoded
            set /a ISSUES_FOUND+=1
        )
    )
)

:: ============================================================================
:: RELATÓRIO FINAL
:: ============================================================================
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            📊 RELATÓRIO FINAL                               ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

if !ISSUES_FOUND! equ 0 (
    echo ✅ SEGURANÇA OK: Nenhum problema crítico encontrado
    echo.
    echo 💡 Recomendações:
    echo • Mantenha o .gitignore atualizado
    echo • Nunca commite arquivos .env
    echo • Faça backups locais dos dados sensíveis
    echo • Use variáveis de ambiente para credenciais
) else (
    echo 🚨 ATENÇÃO: !ISSUES_FOUND! problemas de segurança encontrados!
    echo.
    echo 🔧 AÇÕES RECOMENDADAS:
    echo.
    echo 1. REMOVER ARQUIVOS SENSÍVEIS DO GIT:
    echo    git rm --cached .env
    echo    git rm --cached *.sqlite
    echo    git rm --cached *.log
    echo.
    echo 2. VERIFICAR .gitignore:
    echo    Certifique-se que todos os arquivos sensíveis estão listados
    echo.
    echo 3. LIMPAR HISTÓRICO ^(se necessário^):
    echo    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all
    echo.
    echo 4. FORÇAR PUSH ^(CUIDADO!^):
    echo    git push origin --force --all
    echo.
    echo ⚠️  IMPORTANTE: Faça backup antes de executar comandos de limpeza!
)

echo.
echo 🔒 LEMBRE-SE:
echo • Credenciais vazadas podem causar perdas financeiras
echo • Sempre use .env para dados sensíveis
echo • Mantenha backups locais seguros
echo • Monitore regularmente a segurança
echo.

pause
exit /b %ISSUES_FOUND%
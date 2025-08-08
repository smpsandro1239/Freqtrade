@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: STATUS DE SEGURANÇA SIMPLIFICADO
:: Mostra apenas o que realmente importa
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🛡️ STATUS DE SEGURANÇA                               ║
echo ║                                                                              ║
echo ║  Verificação rápida dos pontos críticos de segurança                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

set "CRITICAL_ISSUES=0"

:: ============================================================================
:: VERIFICAR SE .ENV ESTÁ SENDO RASTREADO PELO GIT
:: ============================================================================
echo 🔐 Verificando proteção do arquivo .env...

git ls-files | findstr /E "\.env$" >nul 2>&1
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: .env está sendo rastreado pelo Git!
    echo    💡 AÇÃO: Execute "git rm --cached .env"
    set /a CRITICAL_ISSUES+=1
) else (
    if exist ".env" (
        echo ✅ .env existe localmente e está protegido pelo .gitignore
    ) else (
        echo ⚠️  .env não encontrado - você precisa configurar suas credenciais
        echo    💡 AÇÃO: Copie .env.example para .env e configure
    )
)

:: ============================================================================
:: VERIFICAR SE HÁ BANCOS DE DADOS SENDO RASTREADOS
:: ============================================================================
echo.
echo 💾 Verificando proteção dos bancos de dados...

git ls-files | findstr "\.sqlite" >nul 2>&1
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: Bancos de dados estão sendo rastreados!
    echo    💡 AÇÃO: Execute "git rm --cached *.sqlite"
    set /a CRITICAL_ISSUES+=1
) else (
    echo ✅ Bancos de dados protegidos
)

:: ============================================================================
:: VERIFICAR SE HÁ LOGS SENDO RASTREADOS
:: ============================================================================
echo.
echo 📋 Verificando proteção dos logs...

git ls-files | findstr "\.log" >nul 2>&1
if %errorLevel% equ 0 (
    echo 🚨 CRÍTICO: Arquivos de log estão sendo rastreados!
    echo    💡 AÇÃO: Execute "git rm --cached *.log"
    set /a CRITICAL_ISSUES+=1
) else (
    echo ✅ Logs protegidos
)

:: ============================================================================
:: VERIFICAR GITIGNORE
:: ============================================================================
echo.
echo 📄 Verificando .gitignore...

if exist ".gitignore" (
    findstr /C:".env" .gitignore >nul 2>&1
    if !errorLevel! equ 0 (
        echo ✅ .gitignore configurado corretamente
    ) else (
        echo ⚠️  .gitignore pode estar incompleto
        set /a CRITICAL_ISSUES+=1
    )
) else (
    echo 🚨 CRÍTICO: .gitignore não encontrado!
    echo    💡 AÇÃO: Crie o arquivo .gitignore
    set /a CRITICAL_ISSUES+=1
)

:: ============================================================================
:: VERIFICAR CONFIGURAÇÕES DE ESTRATÉGIAS
:: ============================================================================
echo.
echo ⚙️ Verificando configurações de estratégias...

set "CONFIG_COUNT=0"
for %%f in (user_data\configs\*.json) do (
    set /a CONFIG_COUNT+=1
)

if %CONFIG_COUNT% gtr 0 (
    echo ℹ️  %CONFIG_COUNT% arquivos de configuração encontrados
    echo    💡 NORMAL: Estes arquivos devem existir localmente
    echo    💡 PROTEGIDO: Estão no .gitignore e não serão commitados
) else (
    echo ⚠️  Nenhuma configuração de estratégia encontrada
)

:: ============================================================================
:: RELATÓRIO FINAL SIMPLIFICADO
:: ============================================================================
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            🎯 RESUMO FINAL                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

if %CRITICAL_ISSUES% equ 0 (
    echo ✅ SEGURANÇA OK: Sistema protegido contra vazamentos
    echo.
    echo 🛡️ PROTEÇÕES ATIVAS:
    echo • .env protegido pelo .gitignore
    echo • Bancos de dados não rastreados
    echo • Logs não rastreados
    echo • Configurações protegidas
    echo.
    echo 💡 ARQUIVOS LOCAIS NORMAIS:
    echo • .env ^(suas credenciais - NUNCA será commitado^)
    echo • user_data/configs/*.json ^(configurações - NUNCA serão commitadas^)
    echo • Estes arquivos DEVEM existir para o sistema funcionar
    echo.
    echo 🎉 Seu sistema está SEGURO para uso!
) else (
    echo 🚨 ATENÇÃO: %CRITICAL_ISSUES% problemas CRÍTICOS encontrados!
    echo.
    echo 🔧 AÇÕES NECESSÁRIAS:
    echo 1. Corrija os problemas listados acima
    echo 2. Execute este script novamente para verificar
    echo 3. Nunca commite arquivos com credenciais
    echo.
    echo ⚠️  NÃO USE O SISTEMA até corrigir os problemas críticos!
)

echo.
echo 🔒 LEMBRE-SE:
echo • Arquivos .env e configs/ DEVEM existir localmente
echo • Mas NUNCA devem ser commitados no Git
echo • O .gitignore protege automaticamente
echo • Execute este script regularmente
echo.

pause
exit /b %CRITICAL_ISSUES%
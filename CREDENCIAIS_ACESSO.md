# 🔐 CREDENCIAIS DE ACESSO - SISTEMA FREQTRADE

## 🌐 **ACESSO VIA NAVEGADOR - TODAS AS ESTRATÉGIAS**

### ✅ **Strategy A**
- **URL:** http://127.0.0.1:8081
- **Username:** `stratA`
- **Password:** `stratA123`
- **Status:** 🟢 Ativo
- **Porta:** 8081

### ✅ **Strategy B**
- **URL:** http://127.0.0.1:8082
- **Username:** `stratB`
- **Password:** `stratB123`
- **Status:** 🟢 Ativo
- **Porta:** 8082

### ✅ **WaveHyperNW Strategy**
- **URL:** http://127.0.0.1:8083
- **Username:** `waveHyperNW`
- **Password:** `waveHyperNW123`
- **Status:** 🟢 Ativo
- **Porta:** 8083

### ✅ **ML Strategy**
- **URL:** http://127.0.0.1:8084
- **Username:** `mlStrategy`
- **Password:** `mlStrategy123`
- **Status:** 🟢 Ativo
- **Porta:** 8084

### ✅ **ML Strategy Simple**
- **URL:** http://127.0.0.1:8085
- **Username:** `mlStrategySimple`
- **Password:** `mlStrategySimple123`
- **Status:** 🟢 Ativo
- **Porta:** 8085

### ✅ **Multi Timeframe Strategy**
- **URL:** http://127.0.0.1:8086
- **Username:** `multiTimeframe`
- **Password:** `multiTimeframe123`
- **Status:** 🟢 Ativo
- **Porta:** 8086

### ✅ **WaveHyperNW Enhanced**
- **URL:** http://127.0.0.1:8087
- **Username:** `waveHyperNWEnhanced`
- **Password:** `waveHyperNWEnhanced123`
- **Status:** 🟢 Ativo
- **Porta:** 8087

---

## 📱 **ACESSO VIA TELEGRAM**

### 🤖 **Bot Telegram**
- **Bot:** `@smpsandrobot`
- **Token:** `7407762395:AAEldw2--6fTrLu16Qpvwcposy3eaUp2Qqs`
- **Chat ID:** `1555333079`
- **Status:** 🟢 Ativo

### 📋 **Comandos Principais:**
- `/start` - Menu principal interativo
- `/status` - Status de todas as estratégias
- `/predict` - IA preditiva avançada
- `/charts comparison` - Gráficos de comparação
- `/charts heatmap` - Mapa de calor
- `/forcebuy stratA BTC/USDT` - Compra forçada
- `/forcesell stratA all` - Venda de todas as posições
- `/adjust stratA reload` - Recarregar configuração

---

## 🔧 **INFORMAÇÕES TÉCNICAS**

### 🐳 **Containers Docker:**
- `ft-stratA` - Strategy A (Porta 8081)
- `ft-stratB` - Strategy B (Porta 8082)
- `ft-waveHyperNW` - WaveHyperNW (Porta 8083)
- `ft-mlStrategy` - ML Strategy (Porta 8084)
- `ft-mlStrategySimple` - ML Simple (Porta 8085)
- `ft-multiTimeframe` - Multi Timeframe (Porta 8086)
- `ft-waveHyperNWEnhanced` - Wave Enhanced (Porta 8087)
- `ft-telegram-commander` - Bot Telegram
- `ft-redis` - Banco de dados Redis

### 🔑 **JWT Tokens (para APIs):**
- **Strategy A:** `stratA_secret_key` / `stratA_ws_token`
- **Strategy B:** `stratB_secret_key` / `stratB_ws_token`
- **WaveHyperNW:** `waveHyperNW_secret_key` / `waveHyperNW_ws_token`
- **ML Strategy:** `mlStrategy_secret_key` / `mlStrategy_ws_token`
- **ML Simple:** `mlStrategySimple_secret_key` / `mlStrategySimple_ws_token`
- **Multi Timeframe:** `multiTimeframe_secret_key` / `multiTimeframe_ws_token`
- **Wave Enhanced:** `waveHyperNWEnhanced_secret_key` / `waveHyperNWEnhanced_ws_token`

---

## 🚀 **COMO USAR**

### 1. **Acesso Web (Recomendado):**
```
1. Abra o navegador
2. Acesse http://127.0.0.1:8081
3. Digite: stratA / stratA123
4. Clique em Login
5. Você verá o dashboard da Strategy A
```

### 2. **Acesso via Telegram:**
```
1. Abra o Telegram
2. Procure por @smpsandrobot
3. Digite /start
4. Use os menus interativos
```

### 3. **Controle via API:**
```bash
# Exemplo de requisição
curl -X POST http://127.0.0.1:8081/api/v1/token/login \
  -H "Content-Type: application/json" \
  -d '{"username":"stratA","password":"stratA123"}'
```

---

## ⚠️ **SEGURANÇA**

### 🔒 **Importante:**
- **Todas as estratégias estão em modo DRY-RUN** (simulação)
- **Não há risco financeiro real**
- **Para trading real, altere `dry_run: false` nas configurações**
- **Mantenha as credenciais seguras**

### 🛡️ **Recomendações:**
- Altere as senhas padrão em produção
- Use HTTPS em ambiente de produção
- Configure firewall para limitar acesso às portas
- Monitore logs regularmente

---

## 📊 **STATUS ATUAL**

**Data:** 14/08/2025  
**Status:** 🟢 SISTEMA 100% OPERACIONAL  
**Estratégias Ativas:** 7/7  
**APIs Funcionando:** 7/7  
**Bot Telegram:** ✅ Ativo  

---

*Documento gerado automaticamente pelo sistema Freqtrade Commander*
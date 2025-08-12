# 🚀 Deploy em Produção - Guia Completo

## 📋 Pré-requisitos

### 🔑 **1. Configurar Telegram Bot**
```bash
# 1. Criar bot no Telegram
# - Abra o Telegram e procure por @BotFather
# - Digite /newbot
# - Escolha um nome e username para o bot
# - Copie o TOKEN gerado

# 2. Obter Chat ID
# - Envie uma mensagem para o bot
# - Acesse: https://api.telegram.org/bot<TOKEN>/getUpdates
# - Copie o "chat_id" da resposta
```

### 🏦 **2. Configurar Exchange (Binance/Bybit/etc)**
```bash
# Obter API Keys da exchange:
# - API Key
# - API Secret
# - Sandbox/Testnet keys para testes
```

### 🐳 **3. Instalar Docker**
```bash
# Windows: Docker Desktop
# Linux: docker + docker-compose
```

---

## 🛠️ **Deploy Passo a Passo**

### **Passo 1: Clonar e Configurar**
```bash
# Clonar repositório
git clone https://github.com/smpsandro1239/Freqtrade.git
cd Freqtrade

# Criar arquivo de configuração
cp .env.example .env
```

### **Passo 2: Configurar Variáveis de Ambiente**
```bash
# Editar .env com suas credenciais
nano .env
```

**Conteúdo do .env:**
```env
# Telegram Configuration
TELEGRAM_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ADMIN_USERS=123456789,987654321

# Exchange Configuration (Binance exemplo)
EXCHANGE_NAME=binance
EXCHANGE_KEY=your_api_key_here
EXCHANGE_SECRET=your_api_secret_here
EXCHANGE_SANDBOX=true

# Trading Configuration
DRY_RUN=true
STAKE_CURRENCY=USDT
STAKE_AMOUNT=100

# Database
DB_URL=sqlite:///user_data/tradesv3.sqlite
```

### **Passo 3: Configurar Estratégias**
```bash
# Verificar configurações das estratégias
ls user_data/configs/

# Arquivos disponíveis:
# - stratA.json
# - stratB.json  
# - waveHyperNW.json
```

### **Passo 4: Deploy Inicial (Dry-Run)**
```bash
# Iniciar em modo de teste
docker compose up -d

# Verificar logs
docker compose logs -f telegram_commander
```

### **Passo 5: Testar Funcionalidades**
```bash
# No Telegram, envie:
/start                    # Menu principal
/status                   # Status das estratégias
/predict                  # Previsões de IA
/stats                    # Estatísticas
```

---

## 🧪 **Testes de Funcionalidades**

### **1. Teste do Menu Principal**
```bash
# No Telegram:
/start

# Deve aparecer:
🤖 FREQTRADE COMMANDER
[📊 Status Geral]
[🎮 Controlar Estratégias]
[📈 Estatísticas]
[💰 Trading Manual]
[⚙️ Configurações]
[🆘 Ajuda]
```

### **2. Teste de Previsões de IA**
```bash
# No Telegram:
/predict

# Deve mostrar:
🔮 PREVISÕES RÁPIDAS
📈 WaveHyperNW Strategy
   🟢 ALTA - 78.5%
   💡 Considerar posições de compra
```

### **3. Teste de Trading Manual**
```bash
# No Telegram:
/forcebuy stratA BTC/USDT

# Deve executar compra forçada (em dry-run)
```

### **4. Teste de Ajuste de Estratégia**
```bash
# No Telegram:
/adjust stratA aggressive

# Deve ajustar para modo agressivo
```

### **5. Teste de Estatísticas Horárias**
```bash
# No Telegram:
/start → 📈 Estatísticas → 📊 Stats Horárias

# Deve mostrar dados reais (não zeros)
```

---

## 🔄 **Migração para Live Trading**

### **⚠️ IMPORTANTE: Só após testes completos em dry-run!**

### **Passo 1: Configurar para Live**
```bash
# Parar sistema
docker compose down

# Editar .env
nano .env

# Alterar:
DRY_RUN=false
EXCHANGE_SANDBOX=false
STAKE_AMOUNT=50  # Começar com valor baixo
```

### **Passo 2: Backup de Segurança**
```bash
# Fazer backup das configurações
cp -r user_data user_data_backup_$(date +%Y%m%d_%H%M%S)
```

### **Passo 3: Iniciar Live Trading**
```bash
# Iniciar sistema live
docker compose up -d

# Monitorar logs atentamente
docker compose logs -f telegram_commander
docker compose logs -f ft-stratA
```

### **Passo 4: Monitoramento Intensivo**
```bash
# Verificar a cada 15 minutos nas primeiras 2 horas:
/status                   # Status geral
/stats                    # Estatísticas
/start → 💰 Trading Manual → stratA  # Posições abertas
```

---

## 📊 **Monitoramento em Produção**

### **1. Comandos de Monitoramento**
```bash
# Status geral
/status

# Estatísticas detalhadas
/stats

# Previsões de mercado
/predict

# Posições abertas
/start → 💰 Trading Manual → [Estratégia]
```

### **2. Logs do Sistema**
```bash
# Logs do Telegram Commander
docker compose logs -f telegram_commander

# Logs das estratégias
docker compose logs -f ft-stratA
docker compose logs -f ft-stratB
docker compose logs -f ft-waveHyperNW

# Logs de todos os containers
docker compose logs -f
```

### **3. Verificações de Saúde**
```bash
# Status dos containers
docker compose ps

# Uso de recursos
docker stats

# Espaço em disco
df -h
```

---

## 🚨 **Comandos de Emergência**

### **1. Parada de Emergência**
```bash
# Via Telegram
/emergency

# Via terminal
docker compose down
```

### **2. Venda Forçada de Tudo**
```bash
# Via Telegram
/forcesell stratA all
/forcesell stratB all
/forcesell waveHyperNW all
```

### **3. Modo Conservador Rápido**
```bash
# Via Telegram
/adjust stratA conservative
/adjust stratB conservative
/adjust waveHyperNW conservative
```

---

## 🔧 **Troubleshooting**

### **Problema: Bot não responde**
```bash
# Verificar logs
docker compose logs telegram_commander

# Verificar token
echo $TELEGRAM_TOKEN

# Reiniciar bot
docker compose restart telegram_commander
```

### **Problema: Estratégias não fazem trades**
```bash
# Verificar modo dry-run
grep DRY_RUN .env

# Verificar saldo
/start → 📊 Status Geral

# Verificar configuração
/start → ⚙️ Configurações
```

### **Problema: Estatísticas mostram zeros**
```bash
# Verificar banco de dados
ls -la user_data/*.sqlite

# Reiniciar sistema
docker compose restart
```

---

## 📈 **Otimização de Performance**

### **1. Ajuste de Estratégias por Mercado**
```bash
# Mercado em alta (bullish)
/adjust stratA aggressive
/adjust stratB aggressive

# Mercado volátil
/adjust stratA conservative
/adjust stratB conservative

# Mercado normal
/adjust stratA balanced
/adjust stratB balanced
```

### **2. Monitoramento de IA**
```bash
# Verificar previsões a cada hora
/predict

# Se confiança > 70% e tendência de alta:
# Considerar modo agressivo

# Se confiança > 70% e tendência de baixa:
# Considerar modo conservador
```

### **3. Gestão de Risco**
```bash
# Verificar drawdown máximo
/stats

# Se drawdown > 10%:
# Considerar modo conservador ou pausa

# Se win rate < 40%:
# Revisar estratégias
```

---

## 🎯 **Checklist de Deploy**

### **Pré-Deploy:**
- [ ] Token do Telegram configurado
- [ ] Chat ID configurado
- [ ] API Keys da exchange configuradas
- [ ] Modo dry-run ativado
- [ ] Stake amount baixo para testes

### **Deploy Inicial:**
- [ ] Sistema iniciado com `docker compose up -d`
- [ ] Logs verificados sem erros
- [ ] Bot responde a `/start`
- [ ] Todas as funcionalidades testadas

### **Testes Funcionais:**
- [ ] Menu principal funcionando
- [ ] Previsões de IA funcionando
- [ ] Trading manual funcionando
- [ ] Ajuste de estratégias funcionando
- [ ] Estatísticas horárias com dados reais
- [ ] Notificações funcionando

### **Go-Live:**
- [ ] Testes em dry-run por pelo menos 24h
- [ ] Backup das configurações feito
- [ ] DRY_RUN=false configurado
- [ ] EXCHANGE_SANDBOX=false configurado
- [ ] Stake amount adequado configurado
- [ ] Monitoramento intensivo nas primeiras 2h

---

## 🎉 **Sistema Pronto para Produção!**

**Após seguir este guia, você terá:**

✅ **Sistema completo** funcionando em produção
✅ **IA preditiva** identificando oportunidades
✅ **Trading manual** para controle total
✅ **Estratégias adaptáveis** ao mercado
✅ **Monitoramento 24/7** via Telegram
✅ **Notificações automáticas** de todos os trades

**🚀 SISTEMA REVOLUCIONÁRIO EM PRODUÇÃO!**
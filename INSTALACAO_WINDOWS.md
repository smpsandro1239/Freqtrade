# 🪟 Instalação Windows - Freqtrade Multi-Strategy

Este guia fornece **3 opções** de instalação para Windows, desde iniciantes até usuários avançados.

## 📋 **Opções de Instalação**

### 🟢 **Opção 1: Instalação Completa (Recomendada)**
**Para iniciantes ou primeira instalação**

```bash
# 1. Baixe o arquivo setup_freqtrade.bat
# 2. Clique com botão direito → "Executar como administrador"
# 3. Siga as instruções na tela
```

**O que faz:**
- ✅ Instala Docker Desktop automaticamente
- ✅ Instala Git automaticamente  
- ✅ Clona o repositório
- ✅ Configuração guiada passo-a-passo
- ✅ Cria scripts de controle
- ✅ Inicia o sistema completo

---

### 🟡 **Opção 2: Setup VPS/Servidor**
**Para VPS Windows ou instalação automatizada**

```bash
# Uso: setup_vps.bat [TELEGRAM_TOKEN] [CHAT_ID] [EXCHANGE_KEY] [SECRET]

# Exemplo com exchange:
setup_vps.bat "123456:ABC-DEF" "-1001234567890" "sua_api_key" "sua_secret_key"

# Exemplo só dry-run:
setup_vps.bat "123456:ABC-DEF" "-1001234567890" "" ""
```

**O que faz:**
- ✅ Instalação silenciosa via Chocolatey
- ✅ Configuração automática via parâmetros
- ✅ Configura firewall do Windows
- ✅ Cria tarefa agendada (inicia com Windows)
- ✅ Scripts de monitoramento
- ✅ Ideal para VPS/servidores

---

### 🔵 **Opção 3: Quick Start**
**Para usuários que já têm Docker e Git**

```bash
# 1. Execute quick_start.bat
# 2. Configure Telegram rapidamente
# 3. Sistema iniciado em 2 minutos
```

**Pré-requisitos:**
- ✅ Docker Desktop instalado e rodando
- ✅ Git instalado
- ✅ Conhecimento básico de Docker

---

## 🛠️ **Pré-requisitos por Opção**

| Opção | Docker | Git | Admin | Telegram Bot |
|-------|--------|-----|-------|--------------|
| **Completa** | ❌ (instala) | ❌ (instala) | ✅ | ✅ |
| **VPS** | ❌ (instala) | ❌ (instala) | ✅ | ✅ |
| **Quick** | ✅ (necessário) | ✅ (necessário) | ❌ | ✅ |

## 🤖 **Como Criar Bot do Telegram**

### 1. **Criar o Bot**
1. Abra o Telegram
2. Procure por `@BotFather`
3. Digite `/newbot`
4. Escolha um nome e username
5. **Copie o TOKEN** fornecido

### 2. **Obter Chat ID**
1. Adicione seu bot a um grupo/chat
2. Envie uma mensagem qualquer
3. Acesse: `https://api.telegram.org/bot[SEU_TOKEN]/getUpdates`
4. Procure por `"chat":{"id":` e **copie o número**

### 3. **Exemplo de Configuração**
```
TELEGRAM_TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=-1001234567890
```

---

## 🎮 **Scripts de Controle Criados**

Após a instalação, você terá estes scripts:

### 📊 **controle.bat** (Opção 1)
Menu interativo com opções:
- Ver Status
- Ver Logs  
- Reiniciar Sistema
- Parar Sistema
- Alternar DRY-RUN ↔ LIVE
- Backup Manual

### 🖥️ **Scripts VPS** (Opção 2)
- `status.bat` - Status do sistema
- `logs.bat` - Logs em tempo real
- `restart.bat` - Reiniciar
- `backup.bat` - Backup manual

---

## 🚀 **Após a Instalação**

### ✅ **Verificar se Funcionou**
1. **Telegram**: Deve receber mensagem de "Bot started"
2. **Docker**: `docker-compose ps` mostra containers rodando
3. **Logs**: `docker-compose logs -f` mostra atividade

### 📊 **Estratégias Ativas**
- **SampleStrategyA**: RSI básico (15m)
- **SampleStrategyB**: RSI básico (15m)
- **WaveHyperNW**: Estratégia avançada (5m)

### 🤖 **Serviços Rodando**
- **Telegram Bot**: Alertas em tempo real
- **Health Monitor**: Monitoramento 24/7
- **Risk Manager**: Ajuste automático de stakes
- **Redis**: Cache de dados

---

## 🔧 **Comandos Úteis**

### **Controle Básico**
```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar tudo
docker-compose down

# Iniciar
docker-compose up -d
```

### **Logs Específicos**
```bash
# Telegram bot
docker-compose logs -f telegram_bot

# Estratégias
docker-compose logs -f stratA stratB waveHyperNW

# Health monitor
docker-compose logs -f health_monitor
```

### **Alternar Modos**
```bash
# Ver modo atual
python scripts/toggle_mode.py status

# Dry-run (simulação)
python scripts/toggle_mode.py dry

# LIVE (dinheiro real - CUIDADO!)
python scripts/toggle_mode.py live
```

---

## ❌ **Solução de Problemas**

### **Docker não inicia**
```bash
# Reiniciar Docker Desktop
# Ou executar como administrador:
net stop com.docker.service
net start com.docker.service
```

### **Containers não sobem**
```bash
# Ver erro específico
docker-compose logs

# Rebuild forçado
docker-compose down
docker-compose up -d --build --force-recreate
```

### **Telegram não funciona**
1. Verificar TOKEN e CHAT_ID no `.env`
2. Testar bot manualmente: `https://api.telegram.org/bot[TOKEN]/getMe`
3. Verificar se bot foi adicionado ao grupo/chat

### **Porta 8080 ocupada**
```bash
# Ver o que está usando a porta
netstat -ano | findstr :8080

# Matar processo (substitua PID)
taskkill /PID [numero_do_pid] /F
```

---

## 🔒 **Segurança**

### **⚠️ Importante**
- **Nunca compartilhe** seu arquivo `.env`
- **Teste sempre** em dry-run antes de ir live
- **Monitore constantemente** via Telegram
- **Faça backups** regulares

### **🛡️ Proteções Ativas**
- StoplossGuard (limite de trades)
- CooldownPeriod (pausa após perdas)
- Health Monitor (alertas de problemas)
- Risk Manager (ajuste automático)

---

## 📞 **Suporte**

- **Documentação**: [README.md](README.md)
- **Repositório**: https://github.com/smpsandro1239/Freqtrade
- **Issues**: Use o GitHub Issues para reportar problemas

---

**🎉 Pronto! Seu sistema Freqtrade Multi-Strategy está funcionando!**
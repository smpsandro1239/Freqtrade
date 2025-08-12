# 📊 GUIA DO DASHBOARD WEB - FREQTRADE MULTI-STRATEGY

## 🎯 **VISÃO GERAL**

O Dashboard Web oferece uma interface visual completa para monitorar suas estratégias de trading com:

- 📈 **Gráficos multi-timeframe** (1m, 5m, 15m, 1h, 4h, 1d)
- 📊 **Indicadores técnicos** em tempo real
- 💰 **Estatísticas de performance**
- 🔔 **Notificações Telegram** melhoradas
- 🔐 **Acesso seguro** com login

---

## 🚀 **COMO INICIAR**

### **Opção 1: Via Docker (Recomendado)**
```bash
# Iniciar sistema completo com dashboard
docker-compose up -d

# Verificar se está rodando
docker-compose ps

# Acessar dashboard
# http://localhost:5000
```

### **Opção 2: Via Script Python**
```bash
# Instalar dependências
pip install -r scripts/requirements.dashboard.txt

# Iniciar dashboard
python start_dashboard.py
```

### **Opção 3: Via PowerShell**
```powershell
# Usar o menu interativo
.\run.ps1

# Ou diretamente
.\run.ps1 dashboard
```

---

## 🔐 **LOGIN E SEGURANÇA**

### **Credenciais Padrão**
- **Username**: `admin`
- **Password**: `admin123`

### **⚠️ IMPORTANTE - SEGURANÇA**
1. **Altere a senha padrão** imediatamente
2. **Configure HTTPS** em produção
3. **Use firewall** para restringir acesso
4. **Monitore logs** de acesso

### **Como Alterar Credenciais**
Edite o arquivo `scripts/dashboard_api.py`:
```python
self.users = {
    'admin': self.hash_password('SUA_NOVA_SENHA'),
    'trader': self.hash_password('OUTRA_SENHA')
}
```

---

## 📊 **FUNCIONALIDADES DO DASHBOARD**

### **1. Estatísticas Principais**
- 📊 **Total de Trades**: Número total de operações
- 🟢 **Trades Abertos**: Posições ativas
- 🎯 **Win Rate**: Taxa de acerto (%)
- 💰 **Profit Total**: Lucro/prejuízo acumulado

### **2. Gráficos Interativos**

#### **Gráfico Principal (TradingView)**
- 🕯️ **Candlesticks** coloridos
- 📈 **EMAs** (8, 21, 50 períodos)
- 🔍 **Zoom** e navegação
- 📱 **Responsivo** (mobile-friendly)

#### **Indicadores Técnicos**
- 📊 **RSI** (Relative Strength Index)
- 📈 **MACD** (Moving Average Convergence Divergence)
- 🎯 **Bollinger Bands**
- 📊 **Volume** com médias móveis

### **3. Multi-Timeframe**
Análise simultânea em diferentes períodos:
- **1m**: Entrada precisa
- **5m**: Momentum de curto prazo
- **15m**: Tendência de médio prazo
- **1h**: Tendência principal
- **4h**: Contexto amplo
- **1d**: Visão de longo prazo

### **4. Painel de Indicadores**
Valores em tempo real:
- 🎯 **RSI atual**
- 📊 **MACD atual**
- 📈 **EMAs atuais**
- 📊 **Volume atual**

---

## 🔔 **NOTIFICAÇÕES TELEGRAM MELHORADAS**

### **Notificações de Entrada**
```
🟢 ENTRADA EM TRADE 🤖

💰 Par: BTC/USDT
🎯 Estratégia: MLStrategySimple
💵 Preço de Entrada: 45000.0000 USDT
📊 Quantidade: 0.001000
💰 Stake: 45.0000 USDT
⏰ Horário: 14:30:25

📈 Sinais de Entrada:
ML_signal_confirmed

🎯 Targets:
• Take Profit: +2-5%
• Stop Loss: -8.0%
```

### **Notificações de Saída**
```
🟢 SAÍDA DE TRADE - LUCRO 🤖

💰 Par: BTC/USDT
🎯 Estratégia: MLStrategySimple

📊 Preços:
• Entrada: 45000.0000 USDT
• Saída: 46350.0000 USDT

💰 Resultado:
• P&L: 1.3500 USDT
• Percentual: 🟢 3.00%

⏱️ Duração: 2h 15m
📊 Quantidade: 0.001000

🏷️ Motivo da Saída:
take_profit
```

### **Resumo Diário**
```
📊 RESUMO DIÁRIO - 15/12/2024

📈 Estatísticas Gerais:
• Total de Trades: 12
• Trades Abertos: 3
• Trades Fechados: 9
• Win Rate: 66.7%
• Profit Total: 15.4500 USDT
• Profit Médio: 1.7167 USDT

🎯 Por Estratégia:
🤖 MLStrategySimple:
  • Trades: 5
  • P&L: 8.2500 USDT
  • Média: 1.6500 USDT

🌊 WaveHyperNWEnhanced:
  • Trades: 4
  • P&L: 7.2000 USDT
  • Média: 1.8000 USDT
```

---

## 🌐 **ACESSO REMOTO**

### **Configuração para Acesso Externo**

#### **1. Via Túnel SSH (Seguro)**
```bash
# No servidor
ssh -R 5000:localhost:5000 usuario@servidor-remoto

# Acessar via: http://servidor-remoto:5000
```

#### **2. Via Ngrok (Desenvolvimento)**
```bash
# Instalar ngrok
# Executar
ngrok http 5000

# Usar URL fornecida (ex: https://abc123.ngrok.io)
```

#### **3. Via VPS (Produção)**
```bash
# Configurar nginx como proxy reverso
# Configurar SSL com Let's Encrypt
# Configurar firewall
```

### **⚠️ Segurança para Acesso Remoto**
1. **Use HTTPS** sempre
2. **Configure firewall** adequadamente
3. **Use VPN** quando possível
4. **Monitore logs** de acesso
5. **Altere senhas** regularmente

---

## 🔧 **CONFIGURAÇÃO AVANÇADA**

### **Variáveis de Ambiente**
```bash
# Dashboard
DASHBOARD_SECRET_KEY=sua-chave-secreta-muito-forte
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=senha-muito-forte

# Redis (para cache)
REDIS_HOST=redis
REDIS_PORT=6379

# Telegram (para notificações)
TELEGRAM_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
```

### **Personalização de Cores**
Edite `scripts/templates/dashboard.html`:
```css
/* Cores principais */
--primary-color: #00d4ff;
--secondary-color: #5a67d8;
--success-color: #51cf66;
--error-color: #ff6b6b;
```

### **Adicionar Novos Indicadores**
Edite `scripts/dashboard_api.py` na função `calculate_indicators()`:
```python
# Exemplo: Adicionar Stochastic
k_percent = ((df['close'] - df['low'].rolling(14).min()) /
            (df['high'].rolling(14).max() - df['low'].rolling(14).min())) * 100
indicators['stoch_k'] = k_percent.tolist()
```

---

## 🐛 **SOLUÇÃO DE PROBLEMAS**

### **Dashboard não carrega**
```bash
# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs dashboard

# Reiniciar
docker-compose restart dashboard
```

### **Erro de login**
1. Verificar credenciais no código
2. Limpar cache do navegador
3. Verificar logs do container

### **Gráficos não aparecem**
1. Verificar conexão com internet (CDNs)
2. Verificar console do navegador (F12)
3. Verificar se dados estão sendo retornados pela API

### **Notificações Telegram não funcionam**
1. Verificar `TELEGRAM_TOKEN` e `CHAT_ID`
2. Testar bot manualmente
3. Verificar logs do enhanced_notifier

---

## 📱 **USO MOBILE**

O dashboard é **totalmente responsivo** e funciona perfeitamente em:
- 📱 **Smartphones** (iOS/Android)
- 📱 **Tablets**
- 💻 **Desktops**
- 🖥️ **Monitores grandes**

### **Recursos Mobile**
- 👆 **Touch gestures** nos gráficos
- 📱 **Layout adaptativo**
- 🔄 **Auto-refresh** configurável
- 📊 **Indicadores otimizados** para tela pequena

---

## 🚀 **PRÓXIMAS FUNCIONALIDADES**

### **Em Desenvolvimento**
- 🔔 **Push notifications** (PWA)
- 📊 **Mais indicadores** (Ichimoku, Fibonacci)
- 🎯 **Alertas personalizados**
- 📈 **Backtesting visual**
- 🤖 **Chat com IA** para análises

### **Roadmap**
1. **Fase 1**: Alertas customizáveis
2. **Fase 2**: Análise de sentimento
3. **Fase 3**: Trading social
4. **Fase 4**: IA avançada

---

## 📞 **SUPORTE**

- 📚 **Documentação**: Este arquivo
- 🐛 **Issues**: GitHub Issues
- 💬 **Telegram**: Grupo de suporte
- 📧 **Email**: suporte@freqtrade.com

---

**🎉 Aproveite seu novo Dashboard Web profissional!**

**Acesse: http://localhost:5000**
**Login: admin / admin123**
**🔒 Lembre-se de alterar a senha!**

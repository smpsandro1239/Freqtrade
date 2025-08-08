# 🤖 Comandos Telegram - Freqtrade Multi-Strategy

## 📋 **COMANDOS DISPONÍVEIS**

### **Comandos Básicos:**
- `/start` - Menu principal interativo
- `/status` - Status de todas as estratégias
- `/control` - Menu de controle de estratégias
- `/stats` - Estatísticas consolidadas
- `/help` - Lista de comandos e ajuda

---

## 🎮 **CONTROLE POR ESTRATÉGIA**

### **Estratégias Disponíveis:**
1. **Sample Strategy A** - RSI básico (15m)
2. **Sample Strategy B** - RSI básico (15m)
3. **WaveHyperNW Strategy** - WaveTrend + Nadaraya-Watson (5m)

### **Ações Disponíveis:**
- ▶️ **Iniciar** estratégia
- ⏹️ **Parar** estratégia
- 🔄 **Reiniciar** estratégia
- 📋 **Ver logs** em tempo real
- 📊 **Estatísticas** detalhadas
- ⚙️ **Configurações** e ajustes

---

## ⚙️ **CONFIGURAÇÕES AVANÇADAS**

### **Alterações Suportadas:**
- 🔄 **Toggle Dry-Run/Live** - Alternar entre simulação e dinheiro real
- 💰 **Stake Amount** - Valor por trade
- 📊 **Max Trades** - Máximo de trades simultâneos
- 📈 **Timeframe** - Intervalo de análise (fixo por estratégia)

### **Segurança:**
- ⚠️ **Confirmação obrigatória** para modo LIVE
- 🔒 **Acesso restrito** a usuários autorizados
- 📝 **Log de todas as ações**
- 🔄 **Reinicialização automática** após mudanças

---

## 📊 **INFORMAÇÕES DISPONÍVEIS**

### **Status da Estratégia:**
- 🟢 **Rodando** - Estratégia ativa
- 🔴 **Parada** - Estratégia inativa
- 🟡 **DRY-RUN** - Modo simulação
- 🔴 **LIVE** - Modo dinheiro real

### **Estatísticas (24h):**
- 📈 **Trades** - Número de operações
- 💰 **P&L Total** - Lucro/Prejuízo total
- 📊 **P&L Médio** - Lucro/Prejuízo por trade
- 🎯 **Win Rate** - Taxa de acerto
- 🏆 **Melhor Trade** - Maior lucro
- 📉 **Pior Trade** - Maior prejuízo

### **Sistema:**
- 🖥️ **CPU** - Uso do processador
- 💾 **RAM** - Uso de memória
- 📦 **Container** - Status do Docker
- 🔄 **Reinicializações** - Contador de restarts

---

## 🚨 **ALERTAS AUTOMÁTICOS**

### **Alertas de Trading:**
- 🟢 **Entrada** - Nova posição aberta
- 🔴 **Saída** - Posição fechada com P&L
- ⚠️ **Erro** - Problemas na estratégia
- 📊 **Relatório** - Resumo horário/diário

### **Alertas de Sistema:**
- 🚨 **Container Offline** - Estratégia parou
- 💾 **Recursos Críticos** - CPU/RAM alto
- 🔄 **Reinicialização** - Container reiniciado
- ⚖️ **Risk Management** - Ajustes automáticos

---

## 🎯 **EXEMPLOS DE USO**

### **Verificar Status:**
1. Digite `/status`
2. Veja o status de todas as estratégias
3. Identifique quais estão rodando

### **Controlar Estratégia:**
1. Digite `/control`
2. Selecione a estratégia desejada
3. Escolha a ação (iniciar/parar/reiniciar)
4. Confirme se necessário

### **Alterar Configuração:**
1. Digite `/control`
2. Selecione a estratégia
3. Clique em "⚙️ Config"
4. Escolha o que alterar
5. Confirme as mudanças
6. Reinicie se necessário

### **Ver Estatísticas:**
1. Digite `/stats` para resumo geral
2. Ou use `/control` → estratégia → "📊 Stats"
3. Veja dados detalhados de performance

---

## 🔒 **SEGURANÇA E PERMISSÕES**

### **Controle de Acesso:**
- ✅ Apenas usuários autorizados podem usar
- ✅ Chat ID configurado no `.env`
- ✅ Verificação em cada comando
- ❌ Usuários não autorizados são bloqueados

### **Confirmações de Segurança:**
- 🚨 **Modo LIVE** - Confirmação obrigatória
- ⚠️ **Reinicialização** - Aviso sobre interrupção
- 💰 **Alteração de Stake** - Confirmação de valor
- 🔄 **Mudanças críticas** - Dupla confirmação

### **Logs de Auditoria:**
- 📝 Todas as ações são logadas
- 🕐 Timestamp de cada comando
- 👤 Identificação do usuário
- 📊 Resultado da ação

---

## 🆘 **SOLUÇÃO DE PROBLEMAS**

### **Bot Não Responde:**
1. Verifique se o container está rodando
2. Confirme o TOKEN no `.env`
3. Verifique o CHAT_ID
4. Reinicie o container: `docker compose restart telegram_commander`

### **Acesso Negado:**
1. Verifique se seu CHAT_ID está correto no `.env`
2. Confirme que é o mesmo chat onde o bot está
3. Reinicie o bot após alterar configurações

### **Estratégia Não Responde:**
1. Verifique logs: `/control` → estratégia → "📋 Logs"
2. Tente reiniciar: `/control` → estratégia → "🔄 Reiniciar"
3. Verifique configuração: `/control` → estratégia → "⚙️ Config"

### **Comandos Não Funcionam:**
1. Use `/help` para ver comandos disponíveis
2. Certifique-se de usar os botões, não digitar
3. Aguarde resposta antes de enviar novo comando

---

## 💡 **DICAS DE USO**

### **Melhores Práticas:**
- ✅ **Teste sempre** em dry-run primeiro
- ✅ **Monitore regularmente** via `/status`
- ✅ **Verifique logs** se algo estranho acontecer
- ✅ **Faça backup** antes de mudanças importantes

### **Monitoramento:**
- 📱 **Deixe notificações ativas** no Telegram
- 🔔 **Configure alertas** para situações críticas
- 📊 **Revise estatísticas** diariamente
- 💰 **Acompanhe P&L** regularmente

### **Segurança:**
- 🔒 **Nunca compartilhe** o bot com terceiros
- 🔐 **Mantenha TOKEN** seguro
- ⚠️ **Cuidado com modo LIVE**
- 💾 **Faça backups** regulares

---

## 🔗 **Links Úteis**

- **Repositório**: https://github.com/smpsandro1239/Freqtrade
- **Documentação**: README.md
- **Segurança**: SEGURANCA.md
- **Instalação**: INSTALACAO_WINDOWS.md

---

**🤖 O Telegram Commander oferece controle total das suas estratégias de trading diretamente do seu celular!**
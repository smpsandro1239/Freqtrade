# 🔒 GUIA DE SEGURANÇA - FREQTRADE MULTI-STRATEGY

## ⚠️ **EXTREMAMENTE IMPORTANTE - LEIA ANTES DE USAR**

Este sistema lida com **dinheiro real** e **credenciais sensíveis**. Um vazamento pode resultar em **perdas financeiras graves**.

---

## 🚨 **REGRAS DE OURO - NUNCA QUEBRE**

### ❌ **NUNCA FAÇA:**
- ❌ **Commitar arquivo `.env`** no Git
- ❌ **Compartilhar credenciais** em chat/email
- ❌ **Fazer screenshot** de telas com credenciais
- ❌ **Usar credenciais reais** em ambiente de teste
- ❌ **Deixar arquivos sensíveis** em pastas públicas
- ❌ **Usar senhas fracas** para contas de exchange
- ❌ **Desabilitar 2FA** nas exchanges

### ✅ **SEMPRE FAÇA:**
- ✅ **Use arquivo `.env`** para todas as credenciais
- ✅ **Mantenha `.gitignore`** atualizado
- ✅ **Execute `check_security.bat`** regularmente
- ✅ **Use 2FA** em todas as contas
- ✅ **Faça backups seguros** dos dados
- ✅ **Monitore logs** de acesso
- ✅ **Teste em dry-run** antes de ir live

---

## 🔐 **ARQUIVOS PROTEGIDOS PELO .GITIGNORE**

### **Credenciais e Configurações:**
```
.env                          # Todas as credenciais
user_data/configs/*.json      # Configurações de estratégias
config*.json                  # Arquivos de configuração
*.key, *.pem, *.crt          # Chaves e certificados
```

### **Dados Financeiros:**
```
*.sqlite, *.db               # Bancos de dados de trades
backups/                     # Backups (podem conter dados sensíveis)
*.log                        # Logs (podem conter debug info)
user_data/data/              # Dados de mercado
```

### **Arquivos Temporários:**
```
*.tmp, *.temp                # Arquivos temporários
cache/, tmp/                 # Pastas de cache
__pycache__/                 # Cache Python
```

---

## 🛡️ **CONFIGURAÇÃO SEGURA**

### **1. Arquivo .env (NUNCA COMMITAR)**
```bash
# ✅ CORRETO - Use variáveis de ambiente
TELEGRAM_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-1001234567890
EXCHANGE_KEY=sua_chave_aqui
EXCHANGE_SECRET=sua_secret_aqui

# ❌ ERRADO - Nunca deixe valores vazios ou de exemplo
TELEGRAM_TOKEN=
EXCHANGE_KEY=your_key_here
```

### **2. Configurações de Exchange**
```json
{
  "exchange": {
    "name": "binance",
    "key": "${EXCHANGE_KEY}",      // ✅ Use variáveis
    "secret": "${EXCHANGE_SECRET}" // ✅ Não hardcode
  }
}
```

### **3. Permissões de API**
- ✅ **Apenas trading** (não withdrawal)
- ✅ **Restrição por IP** se possível
- ✅ **Limite de valor** por operação
- ❌ **Nunca permissão total**

---

## 🔍 **VERIFICAÇÃO DE SEGURANÇA**

### **Execute Regularmente:**
```bash
# Verificar arquivos sensíveis
.\check_security.bat

# Verificar status do Git
git status

# Verificar o que será commitado
git diff --cached
```

### **Antes de Cada Commit:**
```bash
# 1. Verificar segurança
.\check_security.bat

# 2. Verificar arquivos staged
git status

# 3. Se tudo OK, commitar
git commit -m "sua mensagem"
```

---

## 🚨 **SE CREDENCIAIS VAZARAM**

### **Ação Imediata:**
1. **🔴 PARE TUDO** - Pare o sistema imediatamente
2. **🔄 TROQUE CREDENCIAIS** - Gere novas chaves na exchange
3. **🗑️ REVOGUE ANTIGAS** - Desative chaves comprometidas
4. **🔍 INVESTIGUE** - Verifique se houve acesso não autorizado

### **Limpeza do Git:**
```bash
# Remover arquivo do Git (mas manter local)
git rm --cached .env

# Limpar histórico (CUIDADO!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Forçar push (apaga histórico remoto)
git push origin --force --all
```

---

## 💾 **BACKUP SEGURO**

### **O que Fazer Backup:**
- ✅ Arquivo `.env` (em local seguro)
- ✅ Configurações de estratégias
- ✅ Bancos de dados de trades
- ✅ Logs importantes

### **Como Fazer Backup:**
```bash
# Backup manual
.\start.bat (opção 10 - Criar Backup Manual)

# Ou criar pasta segura
mkdir C:\Backups\Freqtrade\%date%
copy .env C:\Backups\Freqtrade\%date%\
copy user_data\configs\*.json C:\Backups\Freqtrade\%date%\
```

### **Onde NÃO Fazer Backup:**
- ❌ Google Drive, Dropbox (não criptografados)
- ❌ Email
- ❌ Chat/WhatsApp
- ❌ Repositórios Git públicos

---

## 🔐 **BOAS PRÁTICAS DE SENHA**

### **Para Exchanges:**
- ✅ **12+ caracteres**
- ✅ **Letras, números, símbolos**
- ✅ **Única para cada exchange**
- ✅ **Gerenciador de senhas**
- ✅ **2FA sempre ativo**

### **Para Telegram Bot:**
- ✅ **Token único** por bot
- ✅ **Chat privado** ou grupo fechado
- ✅ **Não compartilhar** token

---

## 📱 **SEGURANÇA DO TELEGRAM**

### **Configuração Segura:**
- ✅ **Bot privado** (não público)
- ✅ **Chat/grupo fechado**
- ✅ **Verificação em duas etapas** no Telegram
- ✅ **Sessões ativas** monitoradas

### **Monitoramento:**
- ✅ **Alertas de login** estranho
- ✅ **Mensagens suspeitas**
- ✅ **Comandos não autorizados**

---

## 🚨 **SINAIS DE COMPROMETIMENTO**

### **Fique Alerta Para:**
- 🚨 **Trades não autorizados**
- 🚨 **Logins suspeitos** na exchange
- 🚨 **Mensagens estranhas** no Telegram
- 🚨 **Saldo alterado** sem explicação
- 🚨 **Configurações mudadas** automaticamente

### **Em Caso de Suspeita:**
1. **PARE o sistema** imediatamente
2. **TROQUE todas as credenciais**
3. **VERIFIQUE logs** de acesso
4. **CONTATE suporte** da exchange
5. **DOCUMENTE** o incidente

---

## 📞 **CONTATOS DE EMERGÊNCIA**

### **Exchanges:**
- **Binance**: https://www.binance.com/en/support
- **Coinbase**: https://help.coinbase.com/
- **Kraken**: https://support.kraken.com/

### **Telegram:**
- **Suporte**: @BotSupport
- **Segurança**: https://telegram.org/support

---

## ✅ **CHECKLIST DE SEGURANÇA**

### **Configuração Inicial:**
- [ ] Arquivo `.env` criado e não commitado
- [ ] `.gitignore` configurado corretamente
- [ ] 2FA ativo em todas as contas
- [ ] Permissões de API limitadas
- [ ] Backup seguro das credenciais

### **Uso Diário:**
- [ ] Verificar alertas de segurança
- [ ] Monitorar trades no Telegram
- [ ] Verificar saldo nas exchanges
- [ ] Executar `check_security.bat`

### **Manutenção:**
- [ ] Trocar credenciais periodicamente
- [ ] Atualizar sistema regularmente
- [ ] Revisar logs de acesso
- [ ] Fazer backup dos dados

---

## 🎯 **LEMBRE-SE**

> **"Em trading, a segurança não é opcional - é questão de sobrevivência financeira."**

- 🔒 **Segurança em primeiro lugar**, sempre
- 💰 **Dinheiro perdido** por falha de segurança não volta
- 🛡️ **Prevenção** é mais barata que recuperação
- 📚 **Educação contínua** em segurança é essencial

---

**🚨 SE TIVER DÚVIDAS SOBRE SEGURANÇA, PARE E PERGUNTE. NUNCA ASSUMA QUE ESTÁ SEGURO.**
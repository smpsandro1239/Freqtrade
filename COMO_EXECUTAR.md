# 🚀 Como Executar os Scripts

## ❌ **Problema Comum no PowerShell**

Se você está vendo este erro:
```
controle.bat : The term 'controle.bat' is not recognized...
```

**Isso acontece porque o PowerShell tem regras de segurança diferentes do CMD.**

---

## ✅ **3 Soluções Simples**

### 🟢 **Solução 1: Use o Script PowerShell (RECOMENDADO)**
```powershell
# Execute este comando:
.\run.ps1

# Ou para ações específicas:
.\run.ps1 setup     # Instalação completa
.\run.ps1 quick     # Início rápido  
.\run.ps1 status    # Ver status
.\run.ps1 logs      # Ver logs
```

### 🟡 **Solução 2: Use .\ antes do nome**
```powershell
# Em vez de:
setup_freqtrade.bat

# Use:
.\setup_freqtrade.bat
.\quick_start.bat
.\controle.bat
```

### 🔵 **Solução 3: Use o CMD (Prompt de Comando)**
```cmd
# Abra o CMD (não PowerShell) e execute:
setup_freqtrade.bat
quick_start.bat
controle.bat
```

---

## 🎯 **Qual Usar?**

| Situação | Comando Recomendado |
|----------|-------------------|
| **Primeira instalação** | `.\run.ps1 setup` |
| **Já tem Docker/Git** | `.\run.ps1 quick` |
| **Menu interativo** | `.\run.ps1` |
| **Ver status** | `.\run.ps1 status` |
| **Ver logs** | `.\run.ps1 logs` |

---

## 🔧 **Como Abrir Cada Terminal**

### **PowerShell (Recomendado)**
1. `Windows + R`
2. Digite: `powershell`
3. Navegue até a pasta: `cd C:\caminho\para\Freqtrade`
4. Execute: `.\run.ps1`

### **CMD (Alternativa)**
1. `Windows + R`
2. Digite: `cmd`
3. Navegue até a pasta: `cd C:\caminho\para\Freqtrade`
4. Execute: `setup_freqtrade.bat`

### **Windows Terminal (Moderno)**
1. Instale do Microsoft Store
2. Abra e navegue até a pasta
3. Execute: `.\run.ps1`

---

## 🚀 **Início Rápido**

### **Se é sua primeira vez:**
```powershell
# 1. Abra PowerShell como Administrador
# 2. Navegue até a pasta do projeto
cd C:\caminho\para\Freqtrade

# 3. Execute a instalação
.\run.ps1 setup
```

### **Se já tem tudo instalado:**
```powershell
# 1. Abra PowerShell normal
# 2. Navegue até a pasta
cd C:\caminho\para\Freqtrade

# 3. Use o menu
.\run.ps1
```

---

## 🛠️ **Comandos Úteis**

### **Controle do Sistema**
```powershell
.\run.ps1 status    # Ver se está rodando
.\run.ps1 logs      # Ver atividade em tempo real
.\run.ps1 restart   # Reiniciar tudo
.\run.ps1 stop      # Parar sistema
.\run.ps1 start     # Iniciar sistema
```

### **Configuração**
```powershell
.\run.ps1 dry       # Modo simulação
.\run.ps1 live      # Modo real (CUIDADO!)
.\run.ps1 backup    # Backup manual
```

---

## ❓ **Ainda com Problemas?**

### **Erro de Execução de Scripts**
Se aparecer erro sobre "execution policy":
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Docker não encontrado**
```powershell
# Execute a instalação completa:
.\run.ps1 setup
```

### **Arquivo não encontrado**
Certifique-se de estar na pasta correta:
```powershell
# Verificar se está no lugar certo:
ls *.bat

# Deve mostrar:
# setup_freqtrade.bat
# quick_start.bat
# setup_vps.bat
```

---

## 🎉 **Resumo**

**Para 99% dos casos, use:**
```powershell
.\run.ps1
```

**Isso abre um menu interativo com todas as opções!**

---

**💡 Dica**: Salve este arquivo para referência futura!
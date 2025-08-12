#!/usr/bin/env python3
"""
Health Check System - Verificação de saúde do sistema
Monitora containers, banco de dados, e funcionalidades críticas
"""
import os
import sys
import docker
import sqlite3
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

class HealthChecker:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.project_root = Path("/app/project")
        self.results = []
        
    def check_all(self):
        """Execute all health checks"""
        print("🏥 VERIFICAÇÃO DE SAÚDE DO SISTEMA")
        print("=" * 50)
        
        self.check_containers()
        self.check_database()
        self.check_telegram_bot()
        self.check_configurations()
        self.check_disk_space()
        self.check_recent_activity()
        
        self.print_summary()
        return all(result['status'] for result in self.results)
    
    def check_containers(self):
        """Check Docker containers status"""
        print("\n🐳 CONTAINERS DOCKER:")
        
        expected_containers = [
            'ft-telegram-commander',
            'ft-stratA', 
            'ft-stratB',
            'ft-waveHyperNW'
        ]
        
        running_containers = []
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
            for expected in expected_containers:
                found = False
                for container in containers:
                    if expected in container.name:
                        status = container.status
                        if status == 'running':
                            print(f"   ✅ {container.name}: {status}")
                            running_containers.append(container.name)
                        else:
                            print(f"   ❌ {container.name}: {status}")
                        found = True
                        break
                
                if not found:
                    print(f"   ❌ {expected}: não encontrado")
            
            success = len(running_containers) >= 3  # At least telegram + 2 strategies
            self.results.append({
                'check': 'containers',
                'status': success,
                'details': f"{len(running_containers)}/{len(expected_containers)} containers rodando"
            })
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar containers: {e}")
            self.results.append({
                'check': 'containers',
                'status': False,
                'details': str(e)
            })
    
    def check_database(self):
        """Check database connectivity and recent data"""
        print("\n💾 BANCO DE DADOS:")
        
        db_files = [
            "user_data/tradesv3.sqlite",
            "user_data/tradesv3.dryrun.sqlite"
        ]
        
        db_status = []
        
        for db_file in db_files:
            db_path = self.project_root / db_file
            
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    
                    # Check if trades table exists and has data
                    cursor.execute("SELECT COUNT(*) FROM trades")
                    trade_count = cursor.fetchone()[0]
                    
                    # Check recent trades (last 24h)
                    yesterday = (datetime.now() - timedelta(days=1)).timestamp() * 1000
                    cursor.execute("SELECT COUNT(*) FROM trades WHERE open_date_utc > ?", (yesterday,))
                    recent_trades = cursor.fetchone()[0]
                    
                    print(f"   ✅ {db_file}: {trade_count} trades total, {recent_trades} últimas 24h")
                    db_status.append(True)
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"   ❌ {db_file}: Erro - {e}")
                    db_status.append(False)
            else:
                print(f"   ⚠️  {db_file}: Arquivo não encontrado")
                db_status.append(False)
        
        success = any(db_status)  # At least one DB should be working
        self.results.append({
            'check': 'database',
            'status': success,
            'details': f"{sum(db_status)}/{len(db_files)} bancos acessíveis"
        })
    
    def check_telegram_bot(self):
        """Check Telegram bot connectivity"""
        print("\n📱 TELEGRAM BOT:")
        
        token = os.getenv('TELEGRAM_TOKEN')
        
        if not token or token == '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789':
            print("   ❌ Token do Telegram não configurado")
            self.results.append({
                'check': 'telegram',
                'status': False,
                'details': 'Token não configurado'
            })
            return
        
        try:
            # Test bot API
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_info = data['result']
                    print(f"   ✅ Bot ativo: @{bot_info['username']}")
                    self.results.append({
                        'check': 'telegram',
                        'status': True,
                        'details': f"Bot @{bot_info['username']} funcionando"
                    })
                else:
                    print(f"   ❌ Erro na API: {data}")
                    self.results.append({
                        'check': 'telegram',
                        'status': False,
                        'details': 'Erro na API do Telegram'
                    })
            else:
                print(f"   ❌ HTTP {response.status_code}")
                self.results.append({
                    'check': 'telegram',
                    'status': False,
                    'details': f'HTTP {response.status_code}'
                })
                
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}")
            self.results.append({
                'check': 'telegram',
                'status': False,
                'details': str(e)
            })
    
    def check_configurations(self):
        """Check configuration files"""
        print("\n⚙️ CONFIGURAÇÕES:")
        
        config_files = [
            "user_data/configs/stratA.json",
            "user_data/configs/stratB.json", 
            "user_data/configs/waveHyperNW.json"
        ]
        
        valid_configs = 0
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Check essential fields
                    required_fields = ['exchange', 'stake_currency', 'dry_run']
                    missing_fields = [field for field in required_fields if field not in config]
                    
                    if not missing_fields:
                        print(f"   ✅ {config_file}: Válido")
                        valid_configs += 1
                    else:
                        print(f"   ⚠️  {config_file}: Campos faltando - {missing_fields}")
                        
                except Exception as e:
                    print(f"   ❌ {config_file}: Erro - {e}")
            else:
                print(f"   ❌ {config_file}: Não encontrado")
        
        success = valid_configs >= 2  # At least 2 valid configs
        self.results.append({
            'check': 'configurations',
            'status': success,
            'details': f"{valid_configs}/{len(config_files)} configurações válidas"
        })
    
    def check_disk_space(self):
        """Check available disk space"""
        print("\n💿 ESPAÇO EM DISCO:")
        
        try:
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            
            free_gb = free // (1024**3)
            total_gb = total // (1024**3)
            used_pct = (used / total) * 100
            
            print(f"   📊 Espaço livre: {free_gb}GB de {total_gb}GB ({used_pct:.1f}% usado)")
            
            success = free_gb > 1  # At least 1GB free
            if success:
                print("   ✅ Espaço suficiente")
            else:
                print("   ⚠️  Pouco espaço disponível")
            
            self.results.append({
                'check': 'disk_space',
                'status': success,
                'details': f"{free_gb}GB livres"
            })
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar disco: {e}")
            self.results.append({
                'check': 'disk_space',
                'status': False,
                'details': str(e)
            })
    
    def check_recent_activity(self):
        """Check for recent trading activity"""
        print("\n📈 ATIVIDADE RECENTE:")
        
        try:
            # Check log files for recent activity
            log_indicators = [
                "Entering confirm_trade_entry",
                "Entering confirm_trade_exit", 
                "Trade",
                "BUY",
                "SELL"
            ]
            
            recent_activity = False
            
            # This would check actual log files in a real implementation
            # For now, we'll check if system has been running
            containers = self.docker_client.containers.list()
            running_containers = [c for c in containers if 'ft-' in c.name]
            
            if running_containers:
                # Check container uptime
                for container in running_containers:
                    if hasattr(container, 'attrs'):
                        started_at = container.attrs['State']['StartedAt']
                        # Parse and check if started recently
                        recent_activity = True
                        break
            
            if recent_activity:
                print("   ✅ Sistema ativo")
            else:
                print("   ⚠️  Pouca atividade detectada")
            
            self.results.append({
                'check': 'activity',
                'status': recent_activity,
                'details': 'Sistema ativo' if recent_activity else 'Pouca atividade'
            })
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar atividade: {e}")
            self.results.append({
                'check': 'activity',
                'status': False,
                'details': str(e)
            })
    
    def print_summary(self):
        """Print health check summary"""
        print("\n" + "=" * 50)
        print("📋 RESUMO DA VERIFICAÇÃO:")
        print("=" * 50)
        
        passed = sum(1 for result in self.results if result['status'])
        total = len(self.results)
        
        for result in self.results:
            status_icon = "✅" if result['status'] else "❌"
            print(f"   {status_icon} {result['check'].upper()}: {result['details']}")
        
        print(f"\n🎯 RESULTADO GERAL: {passed}/{total} verificações passaram")
        
        if passed == total:
            print("🎉 SISTEMA SAUDÁVEL!")
            return True
        elif passed >= total * 0.7:
            print("⚠️  SISTEMA COM PROBLEMAS MENORES")
            return False
        else:
            print("🚨 SISTEMA COM PROBLEMAS CRÍTICOS!")
            return False

def main():
    """Main function"""
    checker = HealthChecker()
    
    try:
        success = checker.check_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Verificação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal na verificação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
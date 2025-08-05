#!/usr/bin/env python3
"""
Health Monitor for Freqtrade Multi-Strategy
Monitors container health and sends alerts via Telegram
"""
import asyncio
import docker
import logging
import os
from datetime import datetime, timedelta
from telegram import Bot
from typing import Dict, List

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 300  # 5 minutes
ALERT_THRESHOLD = 300  # 5 minutes offline before alert

# Services to monitor
MONITORED_SERVICES = {
    'ft-stratA': 'Strategy A',
    'ft-stratB': 'Strategy B', 
    'ft-telegram': 'Telegram Bot',
    'freqtrade_redis_1': 'Redis Cache'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.last_alerts = {}  # Track when we last sent alerts
        self.container_states = {}  # Track container states
        
    async def send_alert(self, message: str):
        """Send alert to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Alert sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def get_container_status(self, container_name: str) -> Dict:
        """Get detailed container status"""
        try:
            container = self.docker_client.containers.get(container_name)
            return {
                'name': container_name,
                'status': container.status,
                'running': container.status == 'running',
                'health': getattr(container.attrs.get('State', {}), 'Health', {}).get('Status', 'unknown'),
                'started_at': container.attrs['State'].get('StartedAt'),
                'finished_at': container.attrs['State'].get('FinishedAt'),
                'exit_code': container.attrs['State'].get('ExitCode'),
                'restart_count': container.attrs['RestartCount']
            }
        except docker.errors.NotFound:
            return {
                'name': container_name,
                'status': 'not_found',
                'running': False,
                'health': 'not_found'
            }
        except Exception as e:
            logger.error(f"Error checking {container_name}: {e}")
            return {
                'name': container_name,
                'status': 'error',
                'running': False,
                'health': 'error',
                'error': str(e)
            }
    
    async def check_container_health(self, container_name: str, display_name: str):
        """Check individual container health and send alerts if needed"""
        status = self.get_container_status(container_name)
        current_time = datetime.now()
        
        # Store previous state
        previous_state = self.container_states.get(container_name, {})
        self.container_states[container_name] = status
        
        # Check if container is down
        if not status['running']:
            # Check if we need to send an alert
            last_alert = self.last_alerts.get(f"{container_name}_down")
            
            if not last_alert or (current_time - last_alert).seconds > ALERT_THRESHOLD:
                emoji = "🔴" if status['status'] == 'exited' else "⚠️"
                message = f"{emoji} <b>CONTAINER OFFLINE</b>\n\n"
                message += f"📦 Serviço: {display_name}\n"
                message += f"🏷️ Container: {container_name}\n"
                message += f"📊 Status: {status['status']}\n"
                
                if status.get('exit_code'):
                    message += f"🚪 Exit Code: {status['exit_code']}\n"
                
                if status.get('finished_at'):
                    message += f"🕐 Parou em: {status['finished_at'][:19]}\n"
                
                message += f"\n⚡ Ação necessária: Verificar logs e reiniciar"
                
                await self.send_alert(message)
                self.last_alerts[f"{container_name}_down"] = current_time
        
        # Check if container just recovered
        elif status['running'] and previous_state.get('running') == False:
            message = f"✅ <b>CONTAINER RECUPERADO</b>\n\n"
            message += f"📦 Serviço: {display_name}\n"
            message += f"🏷️ Container: {container_name}\n"
            message += f"🕐 Reiniciado em: {current_time.strftime('%H:%M:%S')}\n"
            
            if status.get('restart_count', 0) > 0:
                message += f"🔄 Reinicializações: {status['restart_count']}\n"
            
            await self.send_alert(message)
            
            # Clear down alert
            if f"{container_name}_down" in self.last_alerts:
                del self.last_alerts[f"{container_name}_down"]
    
    async def check_system_resources(self):
        """Check system resources and alert if critical"""
        try:
            # Check disk space
            import shutil
            disk_usage = shutil.disk_usage('.')
            disk_free_gb = disk_usage.free / (1024**3)
            disk_total_gb = disk_usage.total / (1024**3)
            disk_used_pct = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            
            if disk_used_pct > 90:
                message = f"⚠️ <b>DISCO QUASE CHEIO</b>\n\n"
                message += f"💾 Uso: {disk_used_pct:.1f}%\n"
                message += f"📊 Livre: {disk_free_gb:.1f}GB / {disk_total_gb:.1f}GB\n"
                message += f"🧹 Ação: Limpar logs e backups antigos"
                
                last_disk_alert = self.last_alerts.get("disk_space")
                if not last_disk_alert or (datetime.now() - last_disk_alert).seconds > 3600:  # 1 hour
                    await self.send_alert(message)
                    self.last_alerts["disk_space"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
    
    async def generate_health_report(self):
        """Generate periodic health report"""
        message = f"📊 <b>RELATÓRIO DE SAÚDE</b>\n\n"
        
        all_healthy = True
        for container_name, display_name in MONITORED_SERVICES.items():
            status = self.get_container_status(container_name)
            
            if status['running']:
                emoji = "✅"
                status_text = "Online"
            else:
                emoji = "🔴"
                status_text = f"Offline ({status['status']})"
                all_healthy = False
            
            message += f"{emoji} {display_name}: {status_text}\n"
            
            if status.get('restart_count', 0) > 0:
                message += f"   🔄 Reinicializações: {status['restart_count']}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        if all_healthy:
            message += f"\n\n🎉 Todos os serviços funcionando normalmente!"
        
        return message
    
    async def run_health_checks(self):
        """Run all health checks"""
        logger.info("Running health checks...")
        
        # Check each monitored service
        for container_name, display_name in MONITORED_SERVICES.items():
            await self.check_container_health(container_name, display_name)
        
        # Check system resources
        await self.check_system_resources()
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("Starting health monitoring...")
        
        # Send startup message
        await self.send_alert("🔍 <b>MONITOR DE SAÚDE INICIADO</b>\n\nMonitorando containers a cada 5 minutos...")
        
        # Send initial health report
        report = await self.generate_health_report()
        await self.send_alert(report)
        
        while True:
            try:
                await self.run_health_checks()
                
                # Send periodic health report (every 4 hours)
                current_time = datetime.now()
                if current_time.hour % 4 == 0 and current_time.minute < 5:
                    last_report = self.last_alerts.get("health_report")
                    if not last_report or (current_time - last_report).seconds > 3600:
                        report = await self.generate_health_report()
                        await self.send_alert(report)
                        self.last_alerts["health_report"] = current_time
                
                await asyncio.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def main():
    monitor = HealthMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
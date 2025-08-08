#!/usr/bin/env python3
"""
Strategy Controller - Controle individual de estratégias
Permite controle granular de cada estratégia via API
"""
import json
import os
import subprocess
import docker
from typing import Dict, List, Optional
from pathlib import Path

class StrategyController:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.project_root = Path("/app/project")
        
    def get_strategy_config(self, strategy_id: str) -> Dict:
        """Obter configuração de uma estratégia"""
        config_path = self.project_root / f"user_data/configs/{strategy_id}.json"
        
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'error': str(e)}
    
    def update_strategy_config(self, strategy_id: str, updates: Dict) -> Dict:
        """Atualizar configuração de uma estratégia"""
        config_path = self.project_root / f"user_data/configs/{strategy_id}.json"
        
        if not config_path.exists():
            return {'success': False, 'message': 'Configuração não encontrada'}
        
        try:
            # Ler configuração atual
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Aplicar atualizações
            for key, value in updates.items():
                if key in ['stake_amount', 'max_open_trades', 'dry_run']:
                    config[key] = value
            
            # Salvar configuração
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {'success': True, 'message': 'Configuração atualizada'}
            
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def get_strategy_logs(self, strategy_id: str, lines: int = 50) -> List[str]:
        """Obter logs de uma estratégia"""
        try:
            result = subprocess.run([
                'docker', 'compose', 'logs', '--tail', str(lines), strategy_id
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return result.stdout.split('\n')
            else:
                return [f"Erro ao obter logs: {result.stderr}"]
                
        except Exception as e:
            return [f"Erro interno: {str(e)}"]
    
    def get_container_stats(self, container_name: str) -> Dict:
        """Obter estatísticas de uso do container"""
        try:
            container = self.docker_client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Calcular uso de CPU
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            
            cpu_percent = 0.0
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
            
            # Calcular uso de memória
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
                'memory_limit_mb': round(memory_limit / 1024 / 1024, 2),
                'memory_percent': round(memory_percent, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def toggle_dry_run(self, strategy_id: str) -> Dict:
        """Alternar modo dry-run de uma estratégia"""
        config = self.get_strategy_config(strategy_id)
        
        if not config or 'error' in config:
            return {'success': False, 'message': 'Erro ao ler configuração'}
        
        current_dry_run = config.get('dry_run', True)
        new_dry_run = not current_dry_run
        
        result = self.update_strategy_config(strategy_id, {'dry_run': new_dry_run})
        
        if result['success']:
            mode = "DRY-RUN" if new_dry_run else "LIVE"
            result['message'] = f'Estratégia alterada para modo {mode}'
            result['new_mode'] = mode
            result['restart_required'] = True
        
        return result
    
    def update_stake_amount(self, strategy_id: str, new_amount: float) -> Dict:
        """Atualizar stake amount de uma estratégia"""
        if new_amount <= 0:
            return {'success': False, 'message': 'Valor deve ser maior que zero'}
        
        result = self.update_strategy_config(strategy_id, {'stake_amount': new_amount})
        
        if result['success']:
            result['message'] = f'Stake amount alterado para {new_amount} USDT'
            result['restart_required'] = True
        
        return result
    
    def update_max_trades(self, strategy_id: str, new_max: int) -> Dict:
        """Atualizar máximo de trades simultâneos"""
        if new_max <= 0:
            return {'success': False, 'message': 'Valor deve ser maior que zero'}
        
        result = self.update_strategy_config(strategy_id, {'max_open_trades': new_max})
        
        if result['success']:
            result['message'] = f'Máximo de trades alterado para {new_max}'
            result['restart_required'] = True
        
        return result
    
    def get_strategy_summary(self, strategy_id: str) -> Dict:
        """Obter resumo completo de uma estratégia"""
        config = self.get_strategy_config(strategy_id)
        
        if not config or 'error' in config:
            return {'error': 'Configuração não encontrada'}
        
        # Informações básicas
        summary = {
            'strategy_id': strategy_id,
            'strategy_name': config.get('strategy', 'Unknown'),
            'dry_run': config.get('dry_run', True),
            'stake_amount': config.get('stake_amount', 0),
            'max_open_trades': config.get('max_open_trades', 0),
            'stake_currency': config.get('stake_currency', 'USDT'),
            'timeframe': '5m' if 'waveHyperNW' in strategy_id else '15m'
        }
        
        # Status do container
        container_name = f"ft-{strategy_id}"
        try:
            container = self.docker_client.containers.get(container_name)
            summary['container_status'] = container.status
            summary['container_running'] = container.status == 'running'
        except:
            summary['container_status'] = 'not_found'
            summary['container_running'] = False
        
        return summary
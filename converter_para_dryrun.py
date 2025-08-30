#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSOR PARA MODO DRY-RUN (SEGURO)
Converte todas as configurações de volta para modo seguro
"""

import json
import os
import subprocess

def convert_to_dryrun():
    """Converte todas as configurações para modo DRY-RUN"""
    print("🔒 CONVERTENDO PARA MODO SEGURO (DRY-RUN)")
    print("="*50)
    
    configs = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/multiTimeframe.json',
        'user_data/configs/waveHyperNWEnhanced.json'
    ]
    
    converted = 0
    
    for config_file in configs:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Converter para DRY-RUN
                config['dry_run'] = True
                
                # Configurações seguras
                config['stake_amount'] = 20  # Valor baixo para simulação
                config['max_open_trades'] = 2  # Limite baixo
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {config_file} convertido para DRY-RUN")
                converted += 1
                
            except Exception as e:
                print(f"❌ Erro ao converter {config_file}: {e}")
    
    print(f"\n📊 Configurações convertidas: {converted}/{len(configs)}")
    
    if converted > 0:
        print("\n🔄 Reiniciando sistema...")
        try:
            subprocess.run(['docker-compose', '-f', 'docker-compose-simple.yml', 'restart'], 
                         capture_output=True)
            print("✅ Sistema reiniciado em modo DRY-RUN (SEGURO)")
        except Exception as e:
            print(f"❌ Erro ao reiniciar: {e}")
            print("Execute manualmente: docker-compose -f docker-compose-simple.yml restart")

if __name__ == "__main__":
    convert_to_dryrun()
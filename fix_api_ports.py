#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir as portas das APIs
Todas devem usar porta 8080 internamente
"""
import json
import os

def fix_api_port(config_path):
    """Corrige a porta da API para 8080"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'api_server' in config and 'listen_port' in config['api_server']:
            old_port = config['api_server']['listen_port']
            config['api_server']['listen_port'] = 8080
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Corrigido porta {old_port} -> 8080 em {config_path}")
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ Erro em {config_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORRIGINDO PORTAS DAS APIS")
    print("=" * 40)
    
    config_files = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/waveHyperNWEnhanced.json',
        'user_data/configs/multiTimeframe.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            fix_api_port(config_file)

if __name__ == "__main__":
    main()
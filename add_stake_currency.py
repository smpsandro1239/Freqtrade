#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar stake_currency nas configurações
"""
import json
import os

def add_stake_currency(config_path):
    """Adiciona stake_currency se não existir"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'stake_currency' not in config:
            config['stake_currency'] = 'USDT'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Adicionado stake_currency em {config_path}")
            return True
        else:
            print(f"ℹ️ stake_currency já existe em {config_path}")
            return True
        
    except Exception as e:
        print(f"❌ Erro em {config_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 ADICIONANDO STAKE_CURRENCY")
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
            add_stake_currency(config_file)

if __name__ == "__main__":
    main()
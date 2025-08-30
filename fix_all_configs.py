#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir todas as configurações JSON
Adiciona seções faltantes: entry_pricing, exit_pricing, unfilledtimeout
"""
import json
import os
from pathlib import Path

def fix_config_file(config_path):
    """Corrige um arquivo de configuração específico"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Seções a adicionar/corrigir
        entry_pricing = {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1,
            "price_last_balance": 0.0,
            "check_depth_of_market": {
                "enabled": False,
                "bids_to_ask_delta": 1
            }
        }
        
        exit_pricing = {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1
        }
        
        # Adicionar seções se não existirem
        if 'entry_pricing' not in config:
            config['entry_pricing'] = entry_pricing
            print(f"✅ Adicionado entry_pricing em {config_path}")
        
        if 'exit_pricing' not in config:
            config['exit_pricing'] = exit_pricing
            print(f"✅ Adicionado exit_pricing em {config_path}")
        
        # Corrigir unfilledtimeout se necessário
        if 'unfilledtimeout' in config:
            old_timeout = config['unfilledtimeout']
            if 'buy' in old_timeout or 'sell' in old_timeout:
                config['unfilledtimeout'] = {
                    "entry": old_timeout.get('buy', 10),
                    "exit": old_timeout.get('sell', 30),
                    "exit_timeout_count": 0,
                    "unit": "minutes"
                }
                print(f"✅ Corrigido unfilledtimeout em {config_path}")
        
        # Salvar arquivo corrigido
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir {config_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORRIGINDO TODAS AS CONFIGURAÇÕES JSON")
    print("=" * 50)
    
    # Lista de arquivos de configuração
    config_files = [
        'user_data/configs/waveHyperNW.json',
        'user_data/configs/mlStrategy.json',
        'user_data/configs/mlStrategySimple.json',
        'user_data/configs/waveHyperNWEnhanced.json',
        'user_data/configs/multiTimeframe.json',
        'user_data/configs/adaptiveMomentum.json',
        'user_data/configs/hybridAdvanced.json',
        'user_data/configs/intelligentScalping.json',
        'user_data/configs/volatilityAdaptive.json'
    ]
    
    fixed_count = 0
    total_count = 0
    
    for config_file in config_files:
        if os.path.exists(config_file):
            total_count += 1
            if fix_config_file(config_file):
                fixed_count += 1
        else:
            print(f"⚠️ Arquivo não encontrado: {config_file}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {fixed_count}/{total_count} arquivos corrigidos")
    
    if fixed_count == total_count:
        print("✅ Todas as configurações foram corrigidas com sucesso!")
    else:
        print("⚠️ Algumas configurações podem ter problemas")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir configurações depreciadas no FreqTrade
Remove seções 'protections' e corrige notification_settings
"""
import json
import os
from pathlib import Path

def fix_deprecated_config(config_path):
    """Corrige configurações depreciadas em um arquivo específico"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        changes_made = False
        
        # Remover seção 'protections' se existir
        if 'protections' in config:
            del config['protections']
            print(f"✅ Removido 'protections' de {config_path}")
            changes_made = True
        
        # Corrigir notification_settings se existir
        if 'telegram' in config and 'notification_settings' in config['telegram']:
            notifications = config['telegram']['notification_settings']
            
            # Mapear configurações antigas para novas
            mappings = {
                'buy': 'entry',
                'sell': 'exit',
                'buy_cancel': 'entry_cancel',
                'sell_cancel': 'exit_cancel'
            }
            
            for old_key, new_key in mappings.items():
                if old_key in notifications:
                    notifications[new_key] = notifications[old_key]
                    del notifications[old_key]
                    print(f"✅ Corrigido {old_key} -> {new_key} em {config_path}")
                    changes_made = True
        
        # Salvar apenas se houve mudanças
        if changes_made:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        else:
            print(f"ℹ️ Nenhuma correção necessária em {config_path}")
            return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir {config_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORRIGINDO CONFIGURAÇÕES DEPRECIADAS")
    print("=" * 50)
    
    # Lista de arquivos de configuração
    config_files = [
        'user_data/configs/stratA.json',
        'user_data/configs/stratB.json',
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
            if fix_deprecated_config(config_file):
                fixed_count += 1
        else:
            print(f"⚠️ Arquivo não encontrado: {config_file}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {fixed_count}/{total_count} arquivos processados")
    
    if fixed_count == total_count:
        print("✅ Todas as configurações foram corrigidas!")
        print("\n🔄 Reiniciando containers...")
        return True
    else:
        print("⚠️ Algumas configurações podem ter problemas")
        return False

if __name__ == "__main__":
    main()
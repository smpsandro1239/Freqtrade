#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSOR PARA MODO LIVE
ATENÇÃO: Use apenas quando tiver certeza!
"""

import json
import os
from pathlib import Path

def convert_to_live():
    """Converte todas as configurações para modo LIVE"""
    print("⚠️ ATENÇÃO: CONVERSÃO PARA MODO LIVE")
    print("="*50)
    print()
    print("🚨 RISCOS:")
    print("• Trades reais com dinheiro real")
    print("• Possibilidade de perdas financeiras")
    print("• Necessário monitoramento constante")
    print()
    
    confirm = input("Digite 'CONFIRMO' para continuar: ")
    if confirm != 'CONFIRMO':
        print("❌ Conversão cancelada")
        return
    
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
                
                # Converter para LIVE
                config['dry_run'] = False
                
                # Ajustar configurações para LIVE
                config['stake_amount'] = 50  # Valor conservador
                config['max_open_trades'] = 3  # Limite conservador
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {config_file} convertido para LIVE")
                converted += 1
                
            except Exception as e:
                print(f"❌ Erro ao converter {config_file}: {e}")
    
    print(f"\n📊 Configurações convertidas: {converted}/{len(configs)}")
    
    if converted > 0:
        print("\n🔄 Reiniciando sistema...")
        os.system('docker-compose -f docker-compose-simple.yml restart')
        print("✅ Sistema reiniciado em modo LIVE")
        print("\n🚨 MONITORAMENTO OBRIGATÓRIO!")
        print("• Acesse: http://localhost:5000")
        print("• Use Telegram para controle")
        print("• Monitore trades constantemente")

if __name__ == "__main__":
    convert_to_live()

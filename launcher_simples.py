#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAUNCHER SIMPLES - FreqTrade Multi-Strategy
Sem emojis para compatibilidade com Windows
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Menu principal simplificado"""
    print("\nFREQTRADE MULTI-STRATEGY - LAUNCHER")
    print("="*50)
    print()
    print("1. Iniciar Dashboard Web (Demo)")
    print("2. Verificar Status do Sistema") 
    print("3. Testar APIs")
    print("4. Reiniciar Sistema Docker")
    print("5. Converter para Modo LIVE (CUIDADO!)")
    print("6. Sair")
    print()
    
    while True:
        try:
            choice = input("Escolha (1-6): ").strip()
            
            if choice == '1':
                print("\nIniciando Dashboard...")
                os.system('python -c "from scripts.dashboard_main import app; app.run(host=\'0.0.0.0\', port=5000)"')
                
            elif choice == '2':
                print("\nVerificando sistema...")
                os.system('python diagnostico_completo.py')
                
            elif choice == '3':
                print("\nTestando APIs...")
                os.system('python test_all_apis.py')
                
            elif choice == '4':
                print("\nReiniciando Docker...")
                os.system('docker-compose -f docker-compose-simple.yml restart')
                
            elif choice == '5':
                print("\nCONVERSÃO PARA MODO LIVE...")
                os.system('python converter_para_live.py')
                
            elif choice == '6':
                print("\nSaindo...")
                break
                
            else:
                print("Opção inválida!")
                
            input("\nPressione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\nSaindo...")
            break

if __name__ == "__main__":
    main()

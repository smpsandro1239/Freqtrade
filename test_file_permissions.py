#!/usr/bin/env python3
"""
Teste de permissões de arquivo para identificar o problema read-only
"""
import json
import os
from pathlib import Path

def test_file_permissions():
    print("🔍 TESTE DE PERMISSÕES DE ARQUIVO")
    print("=" * 50)
    
    config_path = Path('/app/project/user_data/configs/stratA.json')
    
    print(f"📁 Arquivo: {config_path}")
    print(f"📂 Existe: {config_path.exists()}")
    
    if config_path.exists():
        stat = config_path.stat()
        print(f"📊 Permissões: {oct(stat.st_mode)}")
        print(f"👤 Proprietário: {stat.st_uid}:{stat.st_gid}")
        print(f"📏 Tamanho: {stat.st_size} bytes")
        
        # Verificar processo atual
        print(f"🔧 Processo atual UID: {os.getuid()}")
        print(f"🔧 Processo atual GID: {os.getgid()}")
        
        try:
            # Tentar ler
            print("\n📖 TESTE DE LEITURA:")
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ Leitura bem-sucedida")
            print(f"📊 Stake atual: {config.get('stake_amount', 'N/A')}")
            
            # Tentar escrever
            print("\n✏️ TESTE DE ESCRITA:")
            original_stake = config.get('stake_amount', 20)
            test_stake = 99
            
            config['stake_amount'] = test_stake
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Escrita bem-sucedida")
            
            # Verificar se foi salvo
            print("\n🔍 VERIFICAÇÃO:")
            with open(config_path, 'r') as f:
                config_check = json.load(f)
            
            saved_stake = config_check.get('stake_amount')
            print(f"📊 Stake salvo: {saved_stake}")
            
            if saved_stake == test_stake:
                print("✅ Arquivo foi modificado com sucesso!")
                
                # Restaurar valor original
                config_check['stake_amount'] = original_stake
                with open(config_path, 'w') as f:
                    json.dump(config_check, f, indent=2)
                print(f"🔄 Valor restaurado para: {original_stake}")
            else:
                print("❌ Arquivo não foi modificado corretamente")
                
        except PermissionError as e:
            print(f"❌ ERRO DE PERMISSÃO: {e}")
        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
    else:
        print("❌ Arquivo não encontrado")

if __name__ == "__main__":
    test_file_permissions()
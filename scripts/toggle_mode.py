#!/usr/bin/env python3
"""
Script to safely toggle between dry-run and live trading modes
"""
import json
import os
import sys
from pathlib import Path

def load_config(config_path):
    """Load JSON config file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config_path, config):
    """Save JSON config file with proper formatting"""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def toggle_dry_run(config_dir, mode):
    """Toggle dry_run mode for all strategy configs"""
    config_dir = Path(config_dir)
    configs_updated = []
    
    for config_file in config_dir.glob("*.json"):
        try:
            config = load_config(config_file)
            old_mode = config.get('dry_run', True)
            config['dry_run'] = (mode == 'dry')
            
            save_config(config_file, config)
            configs_updated.append({
                'file': config_file.name,
                'strategy': config.get('strategy', 'Unknown'),
                'old_mode': 'DRY' if old_mode else 'LIVE',
                'new_mode': 'DRY' if config['dry_run'] else 'LIVE'
            })
            
        except Exception as e:
            print(f"❌ Error updating {config_file}: {e}")
            return False
    
    return configs_updated

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['dry', 'live']:
        print("Usage: python toggle_mode.py [dry|live]")
        sys.exit(1)
    
    mode = sys.argv[1]
    config_dir = "user_data/configs"
    
    if not os.path.exists(config_dir):
        print(f"❌ Config directory not found: {config_dir}")
        sys.exit(1)
    
    if mode == 'live':
        print("⚠️  WARNING: You are about to enable LIVE TRADING!")
        print("This will use REAL MONEY. Are you absolutely sure?")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("❌ Operation cancelled")
            sys.exit(1)
    
    print(f"🔄 Switching to {mode.upper()} mode...")
    
    configs_updated = toggle_dry_run(config_dir, mode)
    
    if not configs_updated:
        print("❌ Failed to update configs")
        sys.exit(1)
    
    print("\n✅ Configuration updated:")
    for config in configs_updated:
        print(f"  📄 {config['file']} ({config['strategy']}): {config['old_mode']} → {config['new_mode']}")
    
    if mode == 'live':
        print("\n🚨 LIVE TRADING IS NOW ENABLED!")
        print("💰 Please restart containers: docker compose restart")
    else:
        print("\n🟡 DRY-RUN mode enabled")
        print("🔄 Please restart containers: docker compose restart")

if __name__ == "__main__":
    main()
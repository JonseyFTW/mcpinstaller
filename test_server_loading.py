#!/usr/bin/env python3
"""
Test server loading functionality
"""

import sys
import json
from pathlib import Path

def test_server_loading():
    """Test loading of server definitions"""
    print("Testing server loading...")
    
    # Test direct file loading
    config_file = Path("config/servers.json")
    
    if config_file.exists():
        print(f"Config file exists: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded data type: {type(data)}")
        print(f"Top-level keys: {list(data.keys())}")
        
        if "servers" in data:
            servers_dict = data["servers"]
            print(f"Number of servers in dict: {len(servers_dict)}")
            print(f"Server IDs: {list(servers_dict.keys())}")
            
            # Test converting to list like the dialog does
            local_servers = list(servers_dict.values())
            print(f"Number of server objects: {len(local_servers)}")
            
            for i, server in enumerate(local_servers):
                print(f"  Server {i}: {server.get('name', 'No name')} ({server.get('type', 'No type')})")
                
            return len(local_servers)
        else:
            print("No 'servers' key found in loaded data")
            return 0
    else:
        print(f"Config file does not exist: {config_file}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("SERVER LOADING TEST")
    print("=" * 60)
    
    server_count = test_server_loading()
    
    print("=" * 60)
    print(f"RESULT: {server_count} servers loaded successfully")
    print("=" * 60)
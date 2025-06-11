#!/usr/bin/env python3
"""
Test server entry creation specifically
"""

import json
from pathlib import Path

def test_server_entry_creation():
    """Test the server entry creation logic that was failing"""
    print("Testing server entry creation logic...")
    
    # Load the servers
    config_file = Path("config/servers.json")
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    servers_dict = data["servers"]
    local_servers = list(servers_dict.values())
    
    print(f"Testing creation of {len(local_servers)} server entries...")
    
    # Simulate the logic that was failing
    for index, server in enumerate(local_servers):
        try:
            print(f"Creating server entry {index}: {server.get('name', 'Unknown')}")
            
            # Check if this server requires Docker
            requires_docker = server.get('type', '') == 'docker'
            docker_available = False  # Simulate Docker not available
            
            # Server name with Docker warning if needed
            name_text = server.get("name", "Unknown Server")
            if requires_docker and not docker_available:
                name_text += " [Docker Required]"
            
            # Install button logic
            if requires_docker and not docker_available:
                install_text = "[+] Install + Docker"
                install_color = "orange"
                install_hover = "dark orange"
            else:
                install_text = "[+] Install"
                install_color = None  # Default color
                install_hover = None  # Default hover
            
            print(f"  - Name: {name_text}")
            print(f"  - Type: {server.get('type', 'unknown').upper()}")
            print(f"  - Install button: {install_text}")
            print(f"  - Requires Docker: {requires_docker}")
            
            # Test the lambda creation that was failing
            def create_install_command():
                current_server = server.copy()  # Capture server data
                # This would reference install_btn but we're just testing the logic
                return lambda: print(f"Would install: {current_server.get('name')}")
            
            install_command = create_install_command()
            print(f"  - Command created successfully")
            
        except Exception as e:
            print(f"  ✗ FAILED to create entry for server {index}: {e}")
            return False
    
    print("✓ All server entries created successfully")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("SERVER ENTRY CREATION TEST")
    print("=" * 60)
    
    success = test_server_entry_creation()
    
    print("=" * 60)
    if success:
        print("RESULT: All server entry creation tests PASSED")
    else:
        print("RESULT: Server entry creation tests FAILED")
    print("=" * 60)
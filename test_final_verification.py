#!/usr/bin/env python3
"""
Final verification test for all MCP servers after corrections
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_final_server_configuration():
    """Test final corrected server configuration"""
    print("Testing final corrected MCP server configuration...")
    
    try:
        from src.core.server_manager import MCPServerManager
        from src.utils.logger import init_logging
        
        init_logging()
        manager = MCPServerManager()
        
        servers = manager.servers.get("servers", {})
        print(f"✓ Loaded {len(servers)} servers from corrected config")
        
        # Test each server type
        npm_servers = []
        python_servers = []
        docker_servers = []
        
        for server_id, server_config in servers.items():
            name = server_config.get('name', 'Unknown')
            server_type = server_config.get('type', 'unknown')
            package = server_config.get('package', server_config.get('image', server_config.get('repository', 'N/A')))
            
            print(f"  {server_id:20} | {server_type:8} | {name}")
            
            if server_type == 'npm':
                npm_servers.append((server_id, package))
            elif server_type == 'python':
                python_servers.append((server_id, package))
            elif server_type == 'docker':
                docker_servers.append((server_id, package))
        
        print(f"\n✓ Server type breakdown:")
        print(f"  NPM servers: {len(npm_servers)}")
        print(f"  Python servers: {len(python_servers)}")
        print(f"  Docker servers: {len(docker_servers)}")
        
        # Verify expected servers are present
        expected_npm = [
            'filesystem', 'postgres', 'github', 
            'web-search', 'memory', 'browser-automation'
        ]
        expected_python = ['git', 'kubernetes']
        expected_docker = ['docker']
        
        missing_npm = [s for s in expected_npm if s not in [srv[0] for srv in npm_servers]]
        missing_python = [s for s in expected_python if s not in [srv[0] for srv in python_servers]]
        missing_docker = [s for s in expected_docker if s not in [srv[0] for srv in docker_servers]]
        
        if missing_npm or missing_python or missing_docker:
            print(f"⚠️  Missing servers:")
            if missing_npm: print(f"    NPM: {missing_npm}")
            if missing_python: print(f"    Python: {missing_python}")
            if missing_docker: print(f"    Docker: {missing_docker}")
        else:
            print("✓ All expected servers present")
        
        # Verify MongoDB was removed
        if 'mongodb' not in servers:
            print("✓ MongoDB server correctly removed")
        else:
            print("⚠️  MongoDB server still present")
        
        return len(servers) == 9 and 'mongodb' not in servers
        
    except Exception as e:
        print(f"✗ Final configuration test failed: {e}")
        return False

def test_corrected_packages():
    """Test that corrected packages have the right configurations"""
    print("\nTesting corrected package configurations...")
    
    corrections = {
        'git': {
            'expected_type': 'python',
            'expected_package': 'mcp-server-git',
            'expected_command': 'uvx'
        },
        'web-search': {
            'expected_type': 'npm',
            'expected_package': '@modelcontextprotocol/server-brave-search',
            'expected_env': 'BRAVE_API_KEY'
        },
        'browser-automation': {
            'expected_type': 'npm',
            'expected_package': '@playwright/mcp'
        }
    }
    
    try:
        from src.core.server_manager import MCPServerManager
        from src.utils.logger import init_logging
        
        init_logging()
        manager = MCPServerManager()
        servers = manager.servers.get("servers", {})
        
        all_correct = True
        
        for server_id, expected in corrections.items():
            if server_id not in servers:
                print(f"✗ {server_id}: Server missing")
                all_correct = False
                continue
            
            server = servers[server_id]
            
            # Check type
            if server.get('type') != expected['expected_type']:
                print(f"✗ {server_id}: Type is {server.get('type')}, expected {expected['expected_type']}")
                all_correct = False
            else:
                print(f"✓ {server_id}: Type correct ({expected['expected_type']})")
            
            # Check package
            if server.get('package') != expected['expected_package']:
                print(f"✗ {server_id}: Package is {server.get('package')}, expected {expected['expected_package']}")
                all_correct = False
            else:
                print(f"✓ {server_id}: Package correct ({expected['expected_package']})")
            
            # Check command if specified
            if 'expected_command' in expected:
                config_command = server.get('configuration', {}).get('command')
                if config_command != expected['expected_command']:
                    print(f"✗ {server_id}: Command is {config_command}, expected {expected['expected_command']}")
                    all_correct = False
                else:
                    print(f"✓ {server_id}: Command correct ({expected['expected_command']})")
            
            # Check environment variable if specified
            if 'expected_env' in expected:
                config_env = server.get('configuration', {}).get('env', {})
                if expected['expected_env'] not in config_env:
                    print(f"✗ {server_id}: Missing environment variable {expected['expected_env']}")
                    all_correct = False
                else:
                    print(f"✓ {server_id}: Environment variable correct ({expected['expected_env']})")
        
        return all_correct
        
    except Exception as e:
        print(f"✗ Package configuration test failed: {e}")
        return False

def test_profile_updates():
    """Test that profiles were updated to remove MongoDB"""
    print("\nTesting profile updates...")
    
    try:
        from src.core.server_manager import MCPServerManager
        from src.utils.logger import init_logging
        
        init_logging()
        manager = MCPServerManager()
        profiles = manager.servers.get("profiles", {})
        
        mongodb_profiles = []
        for profile_id, profile in profiles.items():
            if 'mongodb' in profile.get('servers', []):
                mongodb_profiles.append(profile_id)
        
        if mongodb_profiles:
            print(f"⚠️  Profiles still contain MongoDB: {mongodb_profiles}")
            return False
        else:
            print("✓ All profiles updated - MongoDB references removed")
            return True
        
    except Exception as e:
        print(f"✗ Profile update test failed: {e}")
        return False

def main():
    """Run all final verification tests"""
    print("=" * 70)
    print("FINAL MCP SERVER CONFIGURATION VERIFICATION")
    print("=" * 70)
    
    tests = [
        test_final_server_configuration,
        test_corrected_packages,
        test_profile_updates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 70)
    print(f"FINAL VERIFICATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL MCP SERVERS VERIFIED AND READY FOR TESTING!")
        print("\n📋 CORRECTED CONFIGURATION SUMMARY:")
        print("✅ Fixed Git server (npm → python/uvx)")
        print("✅ Fixed Web Search server (→ Brave Search)")
        print("✅ Fixed Browser Automation server (→ @playwright/mcp)")
        print("✅ Removed MongoDB server (package not found)")
        print("✅ Updated profiles to remove MongoDB references")
        print("\n🚀 Ready for production testing!")
    else:
        print("⚠️  Some verification tests failed. Check the output above.")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
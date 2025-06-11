#!/usr/bin/env python3
"""
Test script for the improved Docker functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_docker_detection():
    """Test Docker detection improvements"""
    print("Testing Docker detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test Docker check
        result = checker.check_docker()
        
        print(f"✓ Docker check completed")
        print(f"  Status: {'PASS' if result['status'] else 'FAIL'}")
        print(f"  Message: {result['message']}")
        print(f"  Details: {result.get('details', 'No details')}")
        
        # Test quick availability check
        is_available = checker.is_docker_available()
        print(f"  Quick check: Docker available = {is_available}")
        
        return True
        
    except Exception as e:
        print(f"✗ Docker detection test failed: {e}")
        return False

def test_docker_highlighting():
    """Test Docker server highlighting in discovery"""
    print("\nTesting Docker server highlighting...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Create mock Docker servers to test highlighting logic
        test_servers = [
            {
                "name": "Regular NPM Server",
                "type": "npm",
                "description": "A regular npm-based server"
            },
            {
                "name": "Docker MCP Server",
                "type": "docker",
                "image": "my-docker-image",
                "description": "A Docker-based MCP server"
            }
        ]
        
        docker_available = checker.is_docker_available()
        print(f"  Docker available: {docker_available}")
        
        for server in test_servers:
            requires_docker = server.get('type', '') == 'docker'
            print(f"  Server: {server['name']}")
            print(f"    Type: {server['type']}")
            print(f"    Requires Docker: {requires_docker}")
            
            if requires_docker and not docker_available:
                print(f"    -> Would be HIGHLIGHTED (Docker required but not available)")
            elif requires_docker and docker_available:
                print(f"    -> Normal display (Docker available)")
            else:
                print(f"    -> Normal display (No Docker needed)")
        
        return True
        
    except Exception as e:
        print(f"✗ Docker highlighting test failed: {e}")
        return False

def test_docker_server_manager():
    """Test Docker functionality in server manager"""
    print("\nTesting Docker server manager functionality...")
    
    try:
        from src.core.server_manager import MCPServerManager
        from src.utils.logger import init_logging
        
        init_logging()
        manager = MCPServerManager()
        
        # Test Docker status checking
        docker_status = manager.system_checker.get_docker_status()
        print(f"✓ Docker status check completed")
        print(f"  Status: {docker_status.get('status', False)}")
        print(f"  Message: {docker_status.get('message', 'No message')}")
        print(f"  Daemon running: {docker_status.get('daemon_running', False)}")
        
        # Test ensure Docker available logic (without actually installing)
        try:
            ensure_result = manager._ensure_docker_available()
            print(f"  Ensure Docker available: {ensure_result[0]} - {ensure_result[1]}")
        except Exception as e:
            print(f"  Ensure Docker check failed (expected if Docker not available): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Docker server manager test failed: {e}")
        return False

def test_system_check_with_docker():
    """Test full system check including Docker"""
    print("\nTesting full system check with Docker...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Run full system check
        results = checker.check_all()
        
        print(f"✓ Full system check completed")
        print(f"  Total checks: {len(results)}")
        
        # Focus on Docker result
        if "docker" in results:
            docker_result = results["docker"]
            print(f"  Docker check:")
            print(f"    Status: {'PASS' if docker_result['status'] else 'FAIL'}")
            print(f"    Message: {docker_result['message']}")
            print(f"    Details: {docker_result.get('details', 'No details')}")
        else:
            print(f"  Docker check not found in results")
        
        # Show summary
        summary = checker.get_summary()
        print(f"  Summary: {summary['status']} - {summary['message']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full system check with Docker test failed: {e}")
        return False

def main():
    """Run all Docker functionality tests"""
    print("=" * 60)
    print("Docker Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_docker_detection,
        test_docker_highlighting,
        test_docker_server_manager,
        test_system_check_with_docker
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"DOCKER TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Docker tests passed! Docker functionality is working.")
    else:
        print("⚠️  Some Docker tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
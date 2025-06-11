#!/usr/bin/env python3
"""
Test script for the improved system checker
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_nodejs_detection():
    """Test Node.js detection improvements"""
    print("Testing Node.js detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test Node.js check
        result = checker.check_nodejs()
        
        print(f"✓ Node.js check completed")
        print(f"  Status: {'PASS' if result['status'] else 'FAIL'}")
        print(f"  Message: {result['message']}")
        print(f"  Details: {result.get('details', 'No details')}")
        
        return result['status']
        
    except Exception as e:
        print(f"✗ Node.js detection test failed: {e}")
        return False

def test_internet_connectivity():
    """Test internet connectivity improvements"""
    print("\nTesting internet connectivity...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test internet connectivity
        result = checker.check_internet_connectivity()
        
        print(f"✓ Internet connectivity check completed")
        print(f"  Status: {'PASS' if result['status'] else 'FAIL'}")
        print(f"  Message: {result['message']}")
        print(f"  Details: {result.get('details', 'No details')}")
        
        return result['status']
        
    except Exception as e:
        print(f"✗ Internet connectivity test failed: {e}")
        return False

def test_vscode_detection():
    """Test VS Code detection without opening the app"""
    print("\nTesting VS Code detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test VS Code detection
        vscode_info = checker._check_vscode()
        
        if vscode_info:
            print(f"✓ VS Code detected: {vscode_info['name']} v{vscode_info['version']}")
            print(f"  Path: {vscode_info['path']}")
            print(f"  Extensions: {len(vscode_info['extensions'])} found")
            for ext in vscode_info['extensions']:
                print(f"    - {ext['name']} ({ext['status']})")
            return True
        else:
            print("ℹ VS Code not detected (may not be installed)")
            return True  # Not finding VS Code is OK
        
    except Exception as e:
        print(f"✗ VS Code detection test failed: {e}")
        return False

def test_full_system_check():
    """Test the full system check"""
    print("\nTesting full system check...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Run full system check
        results = checker.check_all()
        
        print(f"✓ Full system check completed")
        print(f"  Total checks: {len(results)}")
        
        passed = sum(1 for result in results.values() if result['status'])
        print(f"  Passed: {passed}/{len(results)}")
        
        # Show summary
        summary = checker.get_summary()
        print(f"  Summary: {summary['status']} - {summary['message']}")
        
        # Show any failed critical checks
        if summary['status'] == 'failed':
            print(f"  Critical failures: {summary.get('critical_failed', [])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full system check test failed: {e}")
        return False

def main():
    """Run all system checker tests"""
    print("=" * 60)
    print("System Checker Improvement Tests")
    print("=" * 60)
    
    tests = [
        test_nodejs_detection,
        test_internet_connectivity,
        test_vscode_detection,
        test_full_system_check
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
    print(f"SYSTEM CHECKER TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All system checker tests passed! Improvements are working.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
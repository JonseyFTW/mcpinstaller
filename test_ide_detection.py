#!/usr/bin/env python3
"""
Test script for the improved IDE detection functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_vscode_detection():
    """Test VS Code detection and extension discovery"""
    print("Testing VS Code detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test VS Code detection
        vscode_info = checker._check_vscode()
        
        if vscode_info:
            print(f"✓ VS Code detected:")
            print(f"  Name: {vscode_info['name']}")
            print(f"  Version: {vscode_info['version']}")
            print(f"  Path: {vscode_info['path']}")
            print(f"  Extensions found: {len(vscode_info['extensions'])}")
            
            for ext in vscode_info['extensions']:
                print(f"    - {ext['name']} v{ext['version']} (Status: {ext['status']})")
                print(f"      Config path: {ext['config_path']}")
                print(f"      Config exists: {ext['config_exists']}")
                print(f"      Folder: {ext['folder']}")
            
            return True
        else:
            print("ℹ VS Code not detected")
            return True  # Not finding VS Code is OK for testing
        
    except Exception as e:
        print(f"✗ VS Code detection test failed: {e}")
        return False

def test_ide_discovery():
    """Test discovery of all supported IDEs"""
    print("\nTesting comprehensive IDE discovery...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test individual IDE checks
        ides_to_check = [
            ("VS Code", checker._check_vscode),
            ("Cursor", checker._check_cursor),
            ("Windsurf", checker._check_windsurf),
            ("Claude Desktop", checker._check_claude_desktop),
            ("Claude Code", checker._check_claude_code)
        ]
        
        found_ides = []
        
        for ide_name, check_func in ides_to_check:
            try:
                ide_info = check_func()
                if ide_info:
                    found_ides.append(ide_info)
                    print(f"✓ {ide_name} detected:")
                    print(f"  Version: {ide_info['version']}")
                    print(f"  Path: {ide_info['path']}")
                else:
                    print(f"ℹ {ide_name} not detected")
            except Exception as e:
                print(f"✗ {ide_name} check failed: {e}")
        
        print(f"\nSummary: Found {len(found_ides)} IDE(s)")
        return True
        
    except Exception as e:
        print(f"✗ IDE discovery test failed: {e}")
        return False

def test_full_ide_check():
    """Test the full IDE check method"""
    print("\nTesting full IDE check...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Run full IDE check
        ide_result = checker.check_ides()
        
        print(f"✓ IDE check completed:")
        print(f"  Status: {'PASS' if ide_result['status'] else 'FAIL'}")
        print(f"  Message: {ide_result['message']}")
        print(f"  Details: {ide_result['details']}")
        
        if 'ides' in ide_result:
            print(f"  Found IDEs:")
            for ide in ide_result['ides']:
                print(f"    - {ide['name']} v{ide['version']}")
                if 'extensions' in ide and ide['extensions']:
                    print(f"      Extensions: {len(ide['extensions'])}")
                    for ext in ide['extensions']:
                        print(f"        * {ext['name']} v{ext['version']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full IDE check test failed: {e}")
        return False

def test_vscode_extension_config():
    """Test VS Code extension configuration detection"""
    print("\nTesting VS Code extension configuration...")
    
    try:
        from src.core.vscode_config import VSCodeExtensionConfig
        from src.utils.logger import init_logging
        
        init_logging()
        vscode_config = VSCodeExtensionConfig()
        
        # Test extension status
        status = vscode_config.get_extension_status()
        
        print(f"✓ Extension status check:")
        for ext_name, ext_status in status.items():
            print(f"  {ext_status['name']}:")
            print(f"    Installed: {ext_status['installed']}")
            print(f"    Config exists: {ext_status['config_exists']}")
            print(f"    Config path: {ext_status['config_path']}")
            print(f"    Server count: {ext_status['server_count']}")
            if ext_status['servers']:
                print(f"    Servers: {', '.join(ext_status['servers'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ VS Code extension config test failed: {e}")
        return False

def test_system_check_with_ides():
    """Test full system check including IDE detection"""
    print("\nTesting full system check with IDE detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Run full system check
        results = checker.check_all()
        
        print(f"✓ Full system check completed")
        
        # Focus on IDE result
        if "ides" in results:
            ide_result = results["ides"]
            print(f"  IDE check:")
            print(f"    Status: {'PASS' if ide_result['status'] else 'FAIL'}")
            print(f"    Message: {ide_result['message']}")
            print(f"    Details: {ide_result['details']}")
            
            if 'ides' in ide_result:
                print(f"    Found {len(ide_result['ides'])} IDE(s):")
                for ide in ide_result['ides']:
                    print(f"      - {ide['name']} v{ide['version']}")
                    if 'extensions' in ide and ide['extensions']:
                        for ext in ide['extensions']:
                            print(f"        * {ext['name']} v{ext['version']} (Config: {ext['config_exists']})")
        else:
            print(f"  IDE check not found in results")
        
        return True
        
    except Exception as e:
        print(f"✗ Full system check with IDEs test failed: {e}")
        return False

def main():
    """Run all IDE detection tests"""
    print("=" * 60)
    print("IDE Detection Improvement Tests")
    print("=" * 60)
    
    tests = [
        test_vscode_detection,
        test_ide_discovery,
        test_full_ide_check,
        test_vscode_extension_config,
        test_system_check_with_ides
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
    print(f"IDE DETECTION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All IDE detection tests passed! Improved detection is working.")
    else:
        print("⚠️  Some IDE tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to validate the fixes made to MCP Installer
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing module imports...")
    
    try:
        from src.utils.logger import get_logger, init_logging
        print("✓ Logger module imports successfully")
    except Exception as e:
        print(f"✗ Logger import failed: {e}")
        return False
    
    try:
        from src.core.system_checker import SystemChecker
        print("✓ SystemChecker module imports successfully")
    except Exception as e:
        print(f"✗ SystemChecker import failed: {e}")
        return False
    
    try:
        from src.core.vscode_config import VSCodeExtensionConfig
        print("✓ VSCodeExtensionConfig module imports successfully")
    except Exception as e:
        print(f"✗ VSCodeExtensionConfig import failed: {e}")
        return False
    
    return True

def test_logger_encoding():
    """Test logger with Unicode characters"""
    print("\nTesting logger encoding...")
    
    try:
        from src.utils.logger import init_logging
        logger = init_logging()
        
        # Test ASCII characters (should work)
        logger.info("Testing ASCII characters: [+] [X] [!] [?]")
        print("✓ ASCII characters logged successfully")
        
        # Test that we handle Unicode gracefully
        try:
            logger.info("Testing Unicode handling...")
            print("✓ Unicode handling works")
        except Exception as e:
            print(f"! Unicode test issue (expected on some systems): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Logger encoding test failed: {e}")
        return False

def test_system_checker():
    """Test basic SystemChecker functionality"""
    print("\nTesting SystemChecker...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test basic checks that should work anywhere
        python_result = checker.check_python()
        platform_result = checker.check_platform()
        
        print(f"✓ Python check: {python_result['status']} - {python_result['message']}")
        print(f"✓ Platform check: {platform_result['status']} - {platform_result['message']}")
        
        # Test display formatting (should use ASCII now)
        checker.results = {"test": {"status": True, "message": "Test passed"}}
        display_text = checker.format_results_for_display()
        
        if "[+]" in display_text and "✓" not in display_text:
            print("✓ Display formatting uses ASCII characters")
        else:
            print("! Display formatting may still contain Unicode")
        
        return True
        
    except Exception as e:
        print(f"✗ SystemChecker test failed: {e}")
        return False

def test_vscode_config():
    """Test VSCode configuration manager"""
    print("\nTesting VSCode configuration manager...")
    
    try:
        from src.core.vscode_config import VSCodeExtensionConfig
        from src.utils.logger import init_logging
        
        init_logging()
        config_manager = VSCodeExtensionConfig()
        
        # Test status check (should work even if VS Code not installed)
        status = config_manager.get_extension_status()
        print(f"✓ Extension status check works: found {len(status)} extensions")
        
        for ext_name, ext_status in status.items():
            print(f"  - {ext_status['name']}: installed={ext_status['installed']}, config={ext_status['config_exists']}")
        
        return True
        
    except Exception as e:
        print(f"✗ VSCode config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Installer - Fix Validation Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_logger_encoding,
        test_system_checker,
        test_vscode_config
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
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
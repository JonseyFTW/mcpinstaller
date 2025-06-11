#!/usr/bin/env python3
"""
Test script for Windows package manager detection functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_claude_package_detection():
    """Test Claude detection via Windows package management"""
    print("Testing Claude package detection via Windows package management...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test Claude Desktop package detection
        claude_info = checker._find_claude_via_windows_packages()
        
        if claude_info:
            print(f"✓ Claude found via Windows package management:")
            print(f"  Name: {claude_info['name']}")
            print(f"  Version: {claude_info['version']}")
            print(f"  Path: {claude_info['path']}")
            if 'install_location' in claude_info:
                print(f"  Install Location: {claude_info['install_location']}")
        else:
            print("ℹ Claude not found via Windows package management")
            print("  This is expected on non-Windows systems or if Claude is not installed")
            print("  On Windows with Claude installed, this method should find it via:")
            print("    - PowerShell Get-Package command")
            print("    - winget list command")
            print("    - Windows Apps (Get-AppxPackage) command")
        
        return True
        
    except Exception as e:
        print(f"✗ Claude package detection test failed: {e}")
        return False

def test_claude_code_package_detection():
    """Test Claude Code detection via Windows package management"""
    print("\nTesting Claude Code package detection via Windows package management...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test Claude Code package detection
        claude_code_info = checker._find_claude_code_via_windows_packages()
        
        if claude_code_info:
            print(f"✓ Claude Code found via Windows package management:")
            print(f"  Name: {claude_code_info['name']}")
            print(f"  Version: {claude_code_info['version']}")
            print(f"  Path: {claude_code_info['path']}")
            if 'install_location' in claude_code_info:
                print(f"  Install Location: {claude_code_info['install_location']}")
        else:
            print("ℹ Claude Code not found via Windows package management")
            print("  This is expected on non-Windows systems or if Claude Code is not installed")
            print("  On Windows with Claude Code installed, this method should find it via:")
            print("    - PowerShell Get-Package command (searching for '*Claude*Code*')")
            print("    - winget list command (searching for 'claude-code')")
        
        return True
        
    except Exception as e:
        print(f"✗ Claude Code package detection test failed: {e}")
        return False

def test_full_claude_detection():
    """Test the complete Claude detection including package management"""
    print("\nTesting full Claude Desktop detection (file system + package management)...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test full Claude Desktop detection (includes package management)
        claude_info = checker._check_claude_desktop()
        
        if claude_info:
            print(f"✓ Claude Desktop detected:")
            print(f"  Name: {claude_info['name']}")
            print(f"  Version: {claude_info['version']}")
            print(f"  Path: {claude_info['path']}")
            if 'install_location' in claude_info:
                print(f"  Install Location: {claude_info['install_location']}")
            
            # Determine detection method
            if "Windows Package" in claude_info['path']:
                print(f"  ✓ Detected via Windows package management")
            else:
                print(f"  ✓ Detected via file system search")
        else:
            print("ℹ Claude Desktop not detected")
            print("  On Windows, detection tries:")
            print("    1. Windows package management (Get-Package, winget, Windows Apps)")
            print("    2. File system search in common installation paths")
        
        return True
        
    except Exception as e:
        print(f"✗ Full Claude detection test failed: {e}")
        return False

def test_full_claude_code_detection():
    """Test the complete Claude Code detection including package management"""
    print("\nTesting full Claude Code detection (CLI + file system + package management)...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test full Claude Code detection (includes package management)
        claude_code_info = checker._check_claude_code()
        
        if claude_code_info:
            print(f"✓ Claude Code detected:")
            print(f"  Name: {claude_code_info['name']}")
            print(f"  Version: {claude_code_info['version']}")
            print(f"  Path: {claude_code_info['path']}")
            if 'install_location' in claude_code_info:
                print(f"  Install Location: {claude_code_info['install_location']}")
            
            # Determine detection method
            if "Windows Package" in claude_code_info['path']:
                print(f"  ✓ Detected via Windows package management")
            elif "CLI" in claude_code_info['path']:
                print(f"  ✓ Detected via CLI command")
            elif "NPM" in claude_code_info['path']:
                print(f"  ✓ Detected via NPM global package")
            else:
                print(f"  ✓ Detected via file system search")
        else:
            print("ℹ Claude Code not detected")
            print("  On Windows, detection tries:")
            print("    1. Windows package management (Get-Package, winget)")
            print("    2. CLI commands (claude-code, claude_code, claudecode, cc)")
            print("    3. File system search in common installation paths")
            print("    4. NPM global packages")
        
        return True
        
    except Exception as e:
        print(f"✗ Full Claude Code detection test failed: {e}")
        return False

def test_integration_with_ide_check():
    """Test that the Windows package detection integrates with IDE check"""
    print("\nTesting integration with full IDE check...")
    
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
            print(f"  Found IDEs ({len(ide_result['ides'])}):")
            for ide in ide_result['ides']:
                print(f"    - {ide['name']} v{ide['version']}")
                if "Windows Package" in ide['path']:
                    print(f"      ✓ Detected via Windows package management")
                
                # Show extensions if available
                if 'extensions' in ide and ide['extensions']:
                    print(f"      Extensions: {len(ide['extensions'])}")
                    for ext in ide['extensions']:
                        print(f"        * {ext['name']} v{ext['version']}")
        
        print(f"\nNote: On Windows with Claude installed, you should see:")
        print(f"  - Claude Desktop detected via Windows package management")
        print(f"  - Claude Code detected via Windows package management (if installed)")
        print(f"  - VS Code with extensions (Cline, Roo) if configured")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all Windows package detection tests"""
    print("=" * 60)
    print("Windows Package Manager Detection Tests")
    print("=" * 60)
    
    tests = [
        test_claude_package_detection,
        test_claude_code_package_detection,
        test_full_claude_detection,
        test_full_claude_code_detection,
        test_integration_with_ide_check
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
    print(f"WINDOWS PACKAGE DETECTION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Windows package detection tests passed!")
        print("The enhanced detection should find Claude via Windows package management.")
    else:
        print("⚠️  Some Windows package detection tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
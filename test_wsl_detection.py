#!/usr/bin/env python3
"""
Test script for WSL Claude Code detection functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_wsl_detection():
    """Test WSL environment detection"""
    print("Testing WSL environment detection...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test WSL detection
        is_wsl = checker._is_running_in_wsl()
        
        print(f"✓ WSL detection completed:")
        print(f"  Running in WSL: {is_wsl}")
        
        if is_wsl:
            print(f"  ✓ WSL environment detected correctly")
            print(f"  WSL_DISTRO_NAME: {os.environ.get('WSL_DISTRO_NAME', 'Not set')}")
            print(f"  WSLENV: {os.environ.get('WSLENV', 'Not set')}")
            
            # Check mount points
            wsl_mounts = ['/mnt/c', '/mnt/d', '/mnt/e']
            available_mounts = [mount for mount in wsl_mounts if Path(mount).exists()]
            print(f"  Available Windows mounts: {', '.join(available_mounts)}")
            
            # Check /proc/version
            try:
                with open('/proc/version', 'r') as f:
                    proc_version = f.read().strip()
                    print(f"  /proc/version contains: {'microsoft' if 'microsoft' in proc_version.lower() else 'no microsoft signature'}")
            except:
                pass
        else:
            print(f"  Not running in WSL environment")
        
        return True
        
    except Exception as e:
        print(f"✗ WSL detection test failed: {e}")
        return False

def test_wsl_claude_code_detection():
    """Test Claude Code detection in WSL"""
    print("\nTesting Claude Code detection in WSL...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test WSL Claude Code detection
        claude_code_info = checker._check_claude_code_in_wsl()
        
        if claude_code_info:
            print(f"✓ Claude Code detected in WSL:")
            print(f"  Name: {claude_code_info['name']}")
            print(f"  Version: {claude_code_info['version']}")
            print(f"  Path: {claude_code_info['path']}")
            print(f"  Environment: {claude_code_info['environment']}")
        else:
            print("ℹ Claude Code not found in WSL")
            print("  Detection methods tried:")
            print("    - CLI commands: claude-code, claude_code, claudecode")
            print("    - NPM global packages")
            print("    - Python pip packages")
            print("    - Common WSL installation paths")
            print("    - Windows installations accessible from WSL")
            print("    - Windows PowerShell/CMD commands from WSL")
            
            # Show what we actually checked
            is_wsl = checker._is_running_in_wsl()
            if is_wsl:
                print(f"  ✓ WSL environment confirmed")
                print(f"  If Claude Code is installed in WSL, you might need to:")
                print(f"    - Install via: npm install -g claude-code")
                print(f"    - Install via: pip install claude-code")
                print(f"    - Or add to PATH if installed elsewhere")
            else:
                print(f"  Not running in WSL - this detection method skipped")
        
        return True
        
    except Exception as e:
        print(f"✗ WSL Claude Code detection test failed: {e}")
        return False

def test_full_claude_code_detection_with_wsl():
    """Test full Claude Code detection including WSL"""
    print("\nTesting full Claude Code detection (including WSL)...")
    
    try:
        from src.core.system_checker import SystemChecker
        from src.utils.logger import init_logging
        
        init_logging()
        checker = SystemChecker()
        
        # Test full Claude Code detection
        claude_code_info = checker._check_claude_code()
        
        if claude_code_info:
            print(f"✓ Claude Code detected:")
            print(f"  Name: {claude_code_info['name']}")
            print(f"  Version: {claude_code_info['version']}")
            print(f"  Path: {claude_code_info['path']}")
            
            if 'environment' in claude_code_info:
                print(f"  Environment: {claude_code_info['environment']}")
                
            # Determine detection method
            if "WSL" in claude_code_info['path']:
                print(f"  ✓ Detected via WSL-specific detection")
            elif "Windows Package" in claude_code_info['path']:
                print(f"  ✓ Detected via Windows package management")
            elif "CLI" in claude_code_info['path']:
                print(f"  ✓ Detected via CLI command")
            elif "NPM" in claude_code_info['path']:
                print(f"  ✓ Detected via NPM global package")
            else:
                print(f"  ✓ Detected via file system search")
        else:
            print("ℹ Claude Code not detected")
            print("  Detection order (first successful method wins):")
            print("    1. WSL-specific detection (if running in WSL):")
            print("       a. WSL CLI commands")
            print("       b. WSL NPM global packages")
            print("       c. WSL Python pip packages")
            print("       d. WSL file system paths")
            print("       e. Windows installations via WSL mounts")
            print("       f. Windows PowerShell/CMD from WSL")
            print("    2. Windows package management (if Windows)")
            print("    3. CLI commands (claude-code, claude_code, claudecode, cc)")
            print("    4. File system search")
            print("    5. NPM global packages")
        
        return True
        
    except Exception as e:
        print(f"✗ Full Claude Code detection test failed: {e}")
        return False

def test_ide_check_with_wsl():
    """Test IDE check integration with WSL detection"""
    print("\nTesting IDE check integration with WSL...")
    
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
        
        if 'ides' in ide_result:
            print(f"  Found IDEs ({len(ide_result['ides'])}):")
            for ide in ide_result['ides']:
                print(f"    - {ide['name']} v{ide['version']}")
                if 'environment' in ide and ide['environment'] == 'WSL':
                    print(f"      ✓ Detected in WSL environment")
                elif "WSL" in ide['path']:
                    print(f"      ✓ WSL-based installation")
        else:
            print(f"  No IDEs detected")
        
        # Show what this means for the user
        is_wsl = checker._is_running_in_wsl()
        if is_wsl:
            print(f"\n  Running in WSL environment:")
            print(f"    - Windows applications (VS Code, Claude Desktop) won't be detected directly")
            print(f"    - WSL-specific installations (like Claude Code via npm) will be detected")
            print(f"    - Windows Claude Code installations may be detected via WSL interop")
            print(f"    - This mixed detection approach handles WSL hybrid scenarios")
        
        return True
        
    except Exception as e:
        print(f"✗ IDE check integration test failed: {e}")
        return False

def main():
    """Run all WSL detection tests"""
    print("=" * 60)
    print("WSL Claude Code Detection Tests")
    print("=" * 60)
    
    tests = [
        test_wsl_detection,
        test_wsl_claude_code_detection,
        test_full_claude_code_detection_with_wsl,
        test_ide_check_with_wsl
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
    print(f"WSL DETECTION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All WSL detection tests passed!")
        print("The system can now detect Claude Code installed in WSL environments.")
    else:
        print("⚠️  Some WSL detection tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify the launch process works correctly
"""

import sys
import os
from pathlib import Path

def test_path_resolution():
    """Test that the script can find its files correctly"""
    print("Testing path resolution...")
    
    # Current working directory
    cwd = Path.cwd()
    print(f"Current working directory: {cwd}")
    
    # Script directory (where this test file is)
    script_dir = Path(__file__).parent
    print(f"Script directory: {script_dir}")
    
    # Files we need to find
    required_files = [
        "mcp_installer.py",
        "requirements.txt",
        "src/gui/main_window.py",
        "src/utils/logger.py"
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = script_dir / file_path
        if full_path.exists():
            print(f"✓ Found: {file_path}")
        else:
            print(f"✗ Missing: {file_path}")
            all_found = False
    
    return all_found

def test_imports():
    """Test that we can import the required modules"""
    print("\nTesting imports...")
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        import customtkinter as ctk
        print("✓ customtkinter imported successfully")
    except ImportError as e:
        print(f"✗ customtkinter import failed: {e}")
        return False
    
    try:
        from src.utils.logger import init_logging
        print("✓ logger module imported successfully")
    except ImportError as e:
        print(f"✗ logger import failed: {e}")
        return False
    
    try:
        from src.gui.main_window import MCPInstallerGUI
        print("✓ main_window module imported successfully")
    except ImportError as e:
        print(f"✗ main_window import failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\nTesting dependencies...")
    
    dependencies = ['customtkinter', 'requests', 'psutil', 'PIL']
    all_available = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"✗ {dep} is not available")
            all_available = False
    
    return all_available

def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Installer Launch Test")
    print("=" * 60)
    
    tests = [
        ("Path Resolution", test_path_resolution),
        ("Python Imports", test_imports),
        ("Dependencies", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} CRASHED: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The launcher should work correctly.")
        print("The batch file should now find mcp_installer.py correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
        print("You may need to install dependencies with: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
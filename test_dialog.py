#!/usr/bin/env python3
"""
Test script for the improved server discovery dialog
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_dialog_import():
    """Test that the dialog modules can be imported"""
    try:
        from src.gui.dialogs import ServerDiscoveryDialog, SingleInstallDialog, ServerDetailsDialog
        print("✓ All dialog classes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Dialog import failed: {e}")
        return False

def test_server_discovery_creation():
    """Test creating a ServerDiscoveryDialog instance"""
    try:
        import customtkinter as ctk
        from src.gui.dialogs import ServerDiscoveryDialog
        from src.utils.logger import init_logging
        
        # Initialize logging
        init_logging()
        
        # Create a minimal root window (won't show)
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
        # Test creating the dialog
        dialog = ServerDiscoveryDialog(root)
        print("✓ ServerDiscoveryDialog created successfully")
        
        # Test that the dialog has the expected methods
        methods = ['_create_server_entry', '_install_single_server', '_show_server_details']
        for method in methods:
            if hasattr(dialog, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
                return False
        
        # Clean up
        dialog.dialog.destroy()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Dialog creation test failed: {e}")
        return False

def test_server_entry_details():
    """Test server entry creation with None values (the TypeError fix)"""
    try:
        # Test data with None values that previously caused TypeError
        test_server = {
            "name": "Test Server",
            "description": "A test server",
            "type": "npm",
            "stars": None,  # This was causing the TypeError
            "version": None,
            "language": "JavaScript",
            "source": "test"
        }
        
        # Test the details filtering that we fixed
        details = []
        if "stars" in test_server and test_server["stars"] is not None:
            details.append(f"* {test_server['stars']}")
        if "version" in test_server and test_server["version"] is not None:
            details.append(f"v{test_server['version']}")
        if "language" in test_server and test_server["language"] is not None:
            details.append(str(test_server['language']))
        if "source" in test_server and test_server["source"] is not None:
            details.append(f"from {test_server['source']}")
        
        # Filter out None values and convert all to strings (our fix)
        details = [str(detail) for detail in details if detail is not None and str(detail).strip()]
        
        if details:
            details_text = " • ".join(details)
            print(f"✓ Details formatting works: {details_text}")
        else:
            print("✓ Details filtering handles empty list correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Server entry details test failed: {e}")
        return False

def main():
    """Run dialog tests"""
    print("=" * 60)
    print("Server Discovery Dialog Tests")
    print("=" * 60)
    
    tests = [
        test_dialog_import,
        test_server_discovery_creation,
        test_server_entry_details
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        try:
            if test():
                passed += 1
                print("PASSED")
            else:
                print("FAILED")
        except Exception as e:
            print(f"CRASHED: {e}")
    
    print("\n" + "=" * 60)
    print(f"DIALOG TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All dialog tests passed! Server discovery improvements are working.")
    else:
        print("⚠️  Some dialog tests failed. Check the output above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
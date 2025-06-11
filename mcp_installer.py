#!/usr/bin/env python3
"""
MCP Server Auto-Installer v2.0
A modern, professional MCP server management tool built with Python and CustomTkinter

Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import customtkinter as ctk
    from src.utils.logger import init_logging
    from src.gui.main_window import MCPInstallerGUI
except ImportError as e:
    print("Error: Required dependencies not installed.")
    print("Please run: pip install -r requirements.txt")
    print(f"Missing: {e}")
    sys.exit(1)


def check_python_version():
    """Ensure Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)


def main():
    """Main application entry point"""
    print("=" * 60)
    print("[*] MCP Server Auto-Installer v2.0")
    print("Professional MCP Server Management Tool")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Initialize logging
    try:
        logger = init_logging()
        logger.info("Application initialization started")
        
        # Create and run GUI
        app = MCPInstallerGUI()
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if 'logger' in locals():
            logger.error("Fatal application error", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
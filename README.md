# MCP Server Auto-Installer (Python Edition)

A modern, cross-platform MCP (Model Context Protocol) server installer with a professional GUI built using Python and CustomTkinter.

## Features

- 🚀 **Modern GUI** - Professional dark theme interface
- 📊 **Real-time Logging** - Complete activity tracking and debugging
- 🔍 **Server Discovery** - Find and install MCP servers automatically  
- 🛠️ **Custom Server Creation** - Build your own server configurations
- 🐳 **Docker Support** - Container-based server management
- 🌐 **Web Dashboard** - Browser-based monitoring interface
- ⚙️ **System Checking** - Automatic prerequisite detection and installation

## Requirements

- Windows 10/11
- Python 3.8+ 
- Node.js 18+ (auto-installed if missing)
- Internet connection

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the installer:**
   ```bash
   python mcp_installer.py
   ```

## Project Structure

```
mcpinstaller/
├── mcp_installer.py          # Main GUI application
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   ├── components.py     # Reusable GUI components
│   │   └── dialogs.py        # Dialog windows
│   ├── core/
│   │   ├── __init__.py
│   │   ├── system_checker.py # System compatibility checking
│   │   ├── server_manager.py # MCP server installation/management
│   │   ├── discovery.py      # Server discovery functionality
│   │   └── docker_manager.py # Docker container management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py         # Logging configuration
│   │   ├── config.py         # Configuration management
│   │   └── helpers.py        # Utility functions
│   └── assets/
│       ├── icons/            # Application icons
│       └── themes/           # Custom themes
├── config/
│   ├── servers.json          # Server definitions
│   └── settings.json         # Application settings
├── logs/                     # Application logs (auto-created)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Building Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "config;config" --add-data "src/assets;assets" mcp_installer.py
```

## Logging

All activities are logged to:
- `logs/mcp_installer.log` - General application logs
- `logs/system_check.log` - System compatibility checks
- `logs/installations.log` - Server installation activities
- `logs/errors.log` - Error tracking

## Configuration

Server configurations are stored in `config/servers.json` and can be customized or extended with new server definitions.
# MCP Server Auto-Installer v2.0 - Installation Guide

## Quick Start (Windows)

1. **Download and extract** the MCP Installer files to a folder
2. **Double-click** `launch.bat` to start the application
3. The installer will automatically:
   - Check Python installation
   - Install required dependencies
   - Launch the modern GUI interface

## Manual Installation

### Prerequisites

- **Windows 10/11**
- **Python 3.8 or higher** ([Download here](https://python.org))
- **Internet connection**

### Step-by-Step Installation

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Open Command Prompt** in the installer folder:
   - Right-click in the folder → "Open in Terminal" (Windows 11)
   - Or hold Shift + Right-click → "Open command window here" (Windows 10)

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python mcp_installer.py
   ```

## Features Overview

### 🚀 **Modern GUI Interface**
- Professional dark theme
- Real-time activity logging
- Progress indicators
- System information display

### 🔍 **Comprehensive System Checking**
- Python version compatibility
- Node.js installation and version
- Windows Package Manager (winget)
- IDE detection (VS Code, Cursor, Claude Desktop)
- Internet connectivity
- Disk space availability
- Docker availability (optional)

### 📦 **MCP Server Management**
- **Discover Servers**: Find available MCP servers from multiple sources
- **Install Servers**: One-click installation with automatic dependency resolution
- **Create Custom Servers**: Build your own server configurations
- **Docker Support**: Container-based server deployment

### 🌐 **Web Dashboard Integration**
- Real-time server monitoring
- Performance metrics
- Update management
- Browser-based interface

### 📝 **Complete Activity Logging**
All activities are automatically logged to:
- `logs/mcp_installer.log` - Main application log
- `logs/system_check.log` - System compatibility checks
- `logs/installations.log` - Server installation activities
- `logs/errors.log` - Error tracking

## Troubleshooting

### Common Issues

**"Python is not recognized"**
- Python is not installed or not in PATH
- Reinstall Python with "Add to PATH" option checked

**"No module named 'customtkinter'"**
- Dependencies not installed
- Run: `pip install -r requirements.txt`

**"Permission denied" errors**
- Run Command Prompt as Administrator
- Or run `launch.bat` as Administrator

**System check fails**
- Check internet connection
- Ensure sufficient disk space (2GB+)
- Install missing prerequisites as indicated

### Getting Help

1. **Check the logs** in the `logs/` folder for detailed error information
2. **System Check** - Run the system compatibility check from the GUI
3. **Activity Log** - Monitor real-time activity in the GUI log panel

## Configuration

### Server Definitions
Edit `config/servers.json` to:
- Add new MCP servers
- Modify server configurations
- Create custom installation profiles

### Application Settings
The application automatically creates necessary directories:
- `logs/` - Application logs
- `config/` - Configuration files

## Advanced Usage

### Creating Standalone Executable
To create a single executable file:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "config;config" mcp_installer.py
```

The executable will be created in the `dist/` folder.

### Custom Server Development
See the `config/servers.json` file for examples of server definitions. You can add your own servers by following the same structure.

## What's New in v2.0

- ✅ **Complete rewrite in Python** for better reliability
- ✅ **Modern CustomTkinter GUI** with professional appearance
- ✅ **Comprehensive logging system** for full traceability
- ✅ **Enhanced system checking** with automatic fixes
- ✅ **Improved error handling** with clear messages
- ✅ **Cross-platform compatibility** (Windows focus)
- ✅ **Threaded operations** to prevent GUI freezing
- ✅ **Real-time status updates** and progress indicators

## Migration from v1.x (PowerShell)

Your old PowerShell files have been automatically moved to the `powershell-backup/` folder for reference. The new Python version provides all the same functionality with significant improvements in reliability and user experience.
# MCP Installer Troubleshooting Guide

## Common Launch Issues

### 1. "can't open file 'mcp_installer.py': No such file or directory"

**Problem**: The batch file cannot find the main Python script.

**Solutions**:
- Ensure you're running `launch.bat` from the MCP installer directory
- Check that `mcp_installer.py` exists in the same folder as `launch.bat`
- Right-click `launch.bat` and select "Run as administrator" if needed

### 2. "Python is not installed or not in PATH"

**Problem**: Python is not installed or not accessible from the command line.

**Solutions**:
- Install Python 3.8+ from https://python.org
- During installation, check "Add Python to PATH"
- Restart your command prompt after installation

### 3. "Failed to install dependencies"

**Problem**: pip cannot install required packages.

**Solutions**:
- Run Command Prompt as administrator
- Manually install: `pip install -r requirements.txt`
- Try: `pip install --user -r requirements.txt`
- Update pip: `python -m pip install --upgrade pip`

### 4. "Import Error: No module named 'customtkinter'"

**Problem**: GUI library not installed.

**Solutions**:
- Run: `pip install customtkinter>=5.2.0`
- Check Python version is 3.8+
- Try reinstalling all dependencies

### 5. GUI Window Doesn't Appear

**Problem**: Application starts but no window shows.

**Solutions**:
- Check logs in the `logs/` directory
- Ensure you're not running in a headless environment
- Try running: `python mcp_installer.py` directly for error messages

### 6. "Permission Denied" Errors

**Problem**: Insufficient permissions to run or install.

**Solutions**:
- Run Command Prompt as administrator
- Check antivirus software isn't blocking the application
- Ensure the installation directory has write permissions

## WSL-Specific Issues

### 7. Running in WSL Environment

**Problem**: GUI applications don't work in WSL by default.

**Solutions**:
- Install an X server for Windows (like VcXsrv or Xming)
- Set DISPLAY environment variable: `export DISPLAY=:0`
- Consider running the installer on Windows instead

### 8. Claude Code Detection in WSL

**Problem**: Claude Code installed in WSL not detected.

**Note**: The installer now supports WSL detection including:
- Native WSL installations via npm/pip
- Windows installations accessible from WSL
- Cross-platform detection methods

## Advanced Troubleshooting

### Manual Installation Check

Run these commands to verify your setup:

```bash
# Check Python version
python --version

# Check if in correct directory
dir

# Check if main script exists
python -c "import os; print('mcp_installer.py exists:', os.path.exists('mcp_installer.py'))"

# Test imports
python -c "import customtkinter, requests, psutil, PIL; print('All dependencies OK')"

# Test path resolution
python test_launch.py
```

### Log File Analysis

Check these log files for detailed error information:
- `logs/mcp_installer.log` - Main application log
- `logs/system_check.log` - System compatibility checks
- `logs/installations.log` - Server installation logs
- `logs/errors.log` - Error details

### Environment Information

To get help, provide this information:
- Windows version
- Python version (`python --version`)
- Working directory when running launcher
- Full error message
- Contents of log files

## Getting Help

If issues persist:
1. Check the log files in the `logs/` directory
2. Try running `python test_launch.py` for diagnostic information
3. Run `python mcp_installer.py` directly to see error messages
4. Report issues with full error messages and environment details

## Quick Fixes

### Reset Installation
```bash
# Remove dependencies and reinstall
pip uninstall customtkinter requests psutil Pillow -y
pip install -r requirements.txt
```

### Clean Start
```bash
# Delete logs and restart
rmdir /s logs
launch.bat
```

### Alternative Launch
```bash
# If batch file fails, run directly
cd /d "C:\path\to\mcp\installer"
python mcp_installer.py
```
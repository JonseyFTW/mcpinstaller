@echo off
:: Advanced MCP Server Auto-Installer Launcher for Windows 11
:: Now includes System Compatibility Checker

title Advanced MCP Server Auto-Installer

echo.
echo ========================================================
echo   Advanced MCP Server Auto-Installer for Windows 11
echo   Features: Web Dashboard, Health Monitoring, 
echo   Auto-Updates, Configuration Profiles
echo ========================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator
    echo Some installations may require elevated privileges
    echo.
)

:: Check PowerShell version
echo [INFO] Checking PowerShell version...
powershell -Command "if ($PSVersionTable.PSVersion.Major -lt 5) { exit 1 } else { Write-Host 'PowerShell version:' $PSVersionTable.PSVersion.ToString() }"
if %errorLevel% neq 0 (
    echo [ERROR] PowerShell 5.0 or higher is required
    echo Please update PowerShell and try again
    pause
    goto :end
)

:: Check if all required files exist
echo [INFO] Checking required files...
set "files_missing=0"

if not exist "%~dp0MCP-Auto-Installer.ps1" (
    echo [ERROR] MCP-Auto-Installer.ps1 not found
    set "files_missing=1"
)

if not exist "%~dp0mcp-servers-config.json" (
    echo [INFO] Configuration file not found. It will be created automatically.
)

if not exist "%~dp0mcp-dashboard.html" (
    echo [ERROR] mcp-dashboard.html not found
    set "files_missing=1"
)

if "%files_missing%"=="1" (
    echo [ERROR] Required files are missing. Please ensure all files are in the same directory.
    pause
    goto :end
)

:: Create necessary directories
echo [INFO] Creating working directories...
if not exist "C:\mcp-tools" mkdir "C:\mcp-tools"
if not exist "C:\mcp-tools\logs" mkdir "C:\mcp-tools\logs"
if not exist "C:\mcp-tools\backups" mkdir "C:\mcp-tools\backups"

:: Set execution policy for current session
echo [INFO] Setting PowerShell execution policy for current session...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force"

:: Show menu options
echo.
echo Choose your preferred option:
echo.
echo [1] System Compatibility Check (RECOMMENDED FIRST)
echo [2] Launch GUI Installer
echo [3] Open Web Dashboard Only
echo [4] Launch Both GUI and Web Dashboard
echo [5] System Check with Auto-Fix
echo [6] Command Line Help
echo [7] Troubleshooting Guide
echo [8] Exit
echo.
choice /C 12345678 /M "Select option"

if errorlevel 8 goto :end
if errorlevel 7 goto :troubleshooting
if errorlevel 6 goto :help
if errorlevel 5 goto :autofix
if errorlevel 4 goto :both
if errorlevel 3 goto :web_only
if errorlevel 2 goto :gui_only
if errorlevel 1 goto :system_check

:system_check
echo [INFO] Running system compatibility check...
echo.
if exist "%~dp0System-Checker.ps1" (
    powershell -File "%~dp0System-Checker.ps1"
) else (
    echo [ERROR] System-Checker.ps1 not found
    echo Please ensure all files are in the same directory
)
pause
goto :menu

:autofix
echo [INFO] Running system compatibility check with auto-fix...
echo.
if exist "%~dp0System-Checker.ps1" (
    powershell -File "%~dp0System-Checker.ps1" -AutoFix
) else (
    echo [ERROR] System-Checker.ps1 not found
    echo Please ensure all files are in the same directory
)
pause
goto :menu

:gui_only
echo [INFO] Launching GUI Installer...
echo.
powershell -File "%~dp0MCP-Auto-Installer.ps1"
goto :cleanup

:web_only
echo [INFO] Opening Web Dashboard...
start "" "%~dp0mcp-dashboard.html"
echo.
echo [INFO] Web Dashboard opened in your default browser
echo [INFO] The dashboard provides real-time monitoring and management
pause
goto :end

:both
echo [INFO] Launching both GUI and Web Dashboard...
echo.
start "" "%~dp0mcp-dashboard.html"
timeout /t 2 /nobreak > nul
powershell -File "%~dp0MCP-Auto-Installer.ps1"
goto :cleanup

:troubleshooting
echo.
echo ========================================================
echo                 TROUBLESHOOTING GUIDE
echo ========================================================
echo.
echo COMMON ISSUES AND SOLUTIONS:
echo.
echo 1. "winget is not recognized":
echo    - Run option 5 (System Check with Auto-Fix)
echo    - Or install manually from Microsoft Store
echo.
echo 2. "Node.js not found" or npm errors:
echo    - Run option 5 (System Check with Auto-Fix)
echo    - Or download from https://nodejs.org
echo    - Restart command prompt after installation
echo.
echo 3. "PowerShell execution policy" errors:
echo    - Run as Administrator
echo    - Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
echo.
echo 4. "Failed to update IDE configuration":
echo    - Check if IDE is properly installed
echo    - Verify configuration file paths exist
echo    - Run installer as Administrator
echo.
echo 5. MCP servers not working in IDE:
echo    - Restart your IDE after installation
echo    - Check IDE's MCP settings/extensions
echo    - Verify server status in Web Dashboard
echo.
echo 6. Docker-related errors:
echo    - Ensure Docker Desktop is running
echo    - Check Docker version compatibility
echo    - Restart Docker service if needed
echo.
echo 7. Permission errors:
echo    - Run installer as Administrator
echo    - Check antivirus software interference
echo    - Temporarily disable real-time protection
echo.
echo LOG LOCATIONS:
echo    - Installation logs: C:\mcp-tools\logs\
echo    - Configuration backups: C:\mcp-tools\backups\
echo    - Health status: health-status.json
echo.
pause
goto :menu

:help
echo.
echo ========================================================
echo                  COMMAND LINE HELP
echo ========================================================
echo.
echo FEATURES:
echo   - Auto-detection of IDEs (VS Code, Cursor, Claude Desktop, etc.)
echo   - 21+ MCP servers across 9 categories
echo   - Configuration profiles for different development scenarios
echo   - Health monitoring and auto-updates
echo   - Web-based dashboard for advanced management
echo   - Automatic prerequisite installation with fallbacks
echo   - System compatibility checking and auto-fixing
echo.
echo CONFIGURATION PROFILES:
echo   - Web Development: Frontend and full-stack development
echo   - Data Science ^& AI: Machine learning and data analysis  
echo   - DevOps Engineer: Container management and deployment
echo   - Full-Stack Enterprise: Complete enterprise development
echo   - API Developer: REST and GraphQL API development
echo   - Minimal Setup: Essential tools only
echo.
echo SUPPORTED MCP SERVERS:
echo   Core: Filesystem, Git, Terminal Controller
echo   Memory: Memory Service, OpenMemory, Qdrant
echo   Database: PostgreSQL Pro/Official, MongoDB
echo   API: GitHub, GraphQL, OpenAPI, Web Fetch
echo   Documentation: Context7
echo   DevOps: Docker, Kubernetes, CircleCI, Jenkins
echo   Development: Browser Tools, VS Code Integration
echo.
echo WEB DASHBOARD FEATURES:
echo   - Real-time server status monitoring
echo   - Performance metrics and health checks
echo   - Update management and notifications
echo   - Configuration profile management
echo   - Activity logs and troubleshooting
echo.
echo SYSTEM REQUIREMENTS:
echo   - Windows 10/11
echo   - PowerShell 5.0+
echo   - 2GB+ free disk space
echo   - Internet connection
echo   - Administrator privileges (recommended)
echo.
pause
goto :menu

:menu
echo.
echo Return to main menu? (Y/N)
choice /C YN /M "Your choice"
if errorlevel 2 goto :end
cls
goto :show_menu

:show_menu
:: Redirect to the main menu display
goto :begin_menu

:begin_menu
echo.
echo Choose your preferred option:
echo.
echo [1] System Compatibility Check (RECOMMENDED FIRST)
echo [2] Launch GUI Installer
echo [3] Open Web Dashboard Only
echo [4] Launch Both GUI and Web Dashboard
echo [5] System Check with Auto-Fix
echo [6] Command Line Help
echo [7] Troubleshooting Guide
echo [8] Exit
echo.
choice /C 12345678 /M "Select option"

if errorlevel 8 goto :end
if errorlevel 7 goto :troubleshooting
if errorlevel 6 goto :help
if errorlevel 5 goto :autofix
if errorlevel 4 goto :both
if errorlevel 3 goto :web_only
if errorlevel 2 goto :gui_only
if errorlevel 1 goto :system_check

:cleanup
echo.
echo [INFO] Advanced MCP Auto-Installer session completed
echo [INFO] Check C:\mcp-tools\logs\ for detailed logs
echo [INFO] Configuration backups are in C:\mcp-tools\backups\
echo [INFO] Use the Web Dashboard for ongoing monitoring
pause

:end
exit /b

:: ==============================================================================
:: ADVANCED SETUP INSTRUCTIONS
:: ==============================================================================
::
:: NEW FEATURES IN ADVANCED VERSION:
::
:: 1. WEB DASHBOARD:
::    - Modern browser-based interface for monitoring
::    - Real-time server status and performance metrics
::    - Update management and health monitoring
::    - Mobile-responsive design with dark theme
::
:: 2. CONFIGURATION PROFILES:
::    - Pre-configured server combinations for specific use cases
::    - Web Development, Data Science, DevOps, Enterprise profiles
::    - One-click application of entire server stacks
::    - Customizable profiles for team environments
::
:: 3. AUTO-UPDATE SYSTEM:
::    - Automatic detection of server updates
::    - Version comparison and update notifications
::    - Batch update capabilities for multiple servers
::    - Rollback support for failed updates
::
:: 4. HEALTH MONITORING:
::    - Real-time server status monitoring
::    - Performance metrics (CPU, memory, response time)
::    - Automatic restart for failed servers
::    - Background monitoring with configurable intervals
::
:: INSTALLATION STRUCTURE:
::    C:\MCP-Installer\
::    ├── MCP-Auto-Installer.ps1      # Enhanced PowerShell GUI
::    ├── mcp-servers-config.json     # Extended server definitions
::    ├── mcp-dashboard.html           # Web-based dashboard
##    ├── Launch-Advanced-MCP.bat      # This enhanced launcher
##    └── health-status.json           # Generated health status file
::
:: USAGE WORKFLOWS:
::
:: 1. FIRST-TIME SETUP:
::    - Run Launch-Advanced-MCP.bat
::    - Choose option 3 (both GUI and Web)
::    - Select a configuration profile
::    - Install selected servers
::    - Monitor via web dashboard
::
:: 2. DAILY MONITORING:
::    - Open web dashboard (option 2)
::    - Check server health status
::    - Review performance metrics
::    - Apply updates if available
::
:: 3. TEAM DEPLOYMENT:
::    - Use configuration profiles for consistency
::    - Share profile configurations
::    - Monitor multiple environments
::    - Automate updates across team
::
:: 4. MAINTENANCE:
::    - Weekly update checks
::    - Health monitoring alerts
##    - Configuration backup reviews
::    - Performance optimization
::
:: ADVANCED FEATURES:
::
:: - Profile Management: Create custom server combinations
:: - Bulk Operations: Install/update multiple servers at once
:: - Health Dashboard: Visual server status indicators
:: - Update Notifications: Automatic update detection
:: - Performance Metrics: CPU, memory, and response time monitoring
:: - Background Monitoring: Continuous health checking
:: - Mobile Support: Responsive web dashboard
:: - Team Collaboration: Shared configuration profiles
::
:: ==============================================================================
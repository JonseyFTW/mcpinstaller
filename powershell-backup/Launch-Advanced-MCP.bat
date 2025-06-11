@echo off
:: Advanced MCP Server Auto-Installer Launcher for Windows 11
:: Now includes Automatic System Compatibility Checker

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

if not exist "%~dp0System-Checker.ps1" (
    echo [ERROR] System-Checker.ps1 not found
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

:: Automatically run system compatibility check first
echo.
echo [INFO] Running automatic system compatibility check...
echo [INFO] This ensures your system has all required prerequisites
echo.

powershell -Command "& '%~dp0System-Checker.ps1' -AutoFix; exit $LASTEXITCODE"
set "system_check_result=%errorLevel%"

if %system_check_result% neq 0 (
    echo.
    echo [ERROR] System compatibility check failed!
    echo [ERROR] Please resolve the issues above before continuing.
    echo.
    echo Would you like to try the manual fix options?
    choice /C YN /M "Continue to manual options (Y) or Exit (N)"
    if errorlevel 2 goto :end
    goto :manual_options
) else (
    echo.
    echo [SUCCESS] System compatibility check passed!
    echo [INFO] Your system is ready for MCP installation.
    echo [INFO] Launching Advanced GUI Installer automatically...
    echo.
    goto :gui_only
)

:: Show main menu after successful system check (fallback)
:show_main_menu
echo Choose your preferred option:
echo.
echo [1] [*] Setup Wizard (Recommended for first-time users)
echo [2] [^>] Launch Advanced GUI Installer
echo [3] [=] Open Web Dashboard Only  
echo [4] [?] Discover New MCP Servers
echo [5] [+] Create Custom MCP Server
echo [6] [D] Docker Container Manager
echo [7] [!] System Compatibility Check
echo [8] [i] Command Line Help
echo [9] [#] Troubleshooting Guide
echo [10] Exit
echo.
choice /C 1234567890 /M "Select option (1-10)"

if errorlevel 10 goto :end
if errorlevel 9 goto :troubleshooting
if errorlevel 8 goto :help
if errorlevel 7 goto :system_check
if errorlevel 6 goto :docker_manager
if errorlevel 5 goto :create_server
if errorlevel 4 goto :discover_servers
if errorlevel 3 goto :web_only
if errorlevel 2 goto :gui_only
if errorlevel 1 goto :setup_wizard

:setup_wizard
echo [INFO] [*] Starting Setup Wizard for first-time users...
echo This will guide you through the entire process step by step.
echo.
powershell -File "%~dp0Setup-Wizard.ps1"
goto :cleanup

:discover_servers
echo [INFO] [?] Launching MCP Server Discovery Tool...
echo This will help you find and add new MCP servers to your collection.
echo.
powershell -File "%~dp0MCP-Discovery.ps1" -Interactive
pause
goto :show_main_menu

:create_server
echo [INFO] [+] Launching MCP Server Creator...
echo Create custom server configurations using templates.
echo.
powershell -File "%~dp0Create-MCPServer.ps1" -Interactive
pause
goto :show_main_menu

:docker_manager
echo [INFO] [D] Launching Docker Container Manager...
echo Manage MCP servers running in Docker containers.
echo.
powershell -File "%~dp0Docker-Manager.ps1"
pause
goto :show_main_menu

:system_check
echo [INFO] Running system compatibility check...
echo.
powershell -Command "& '%~dp0System-Checker.ps1' -AutoFix -CheckIDEs; exit $LASTEXITCODE"
pause
goto :show_main_menu

:gui_only
echo [INFO] [>] Launching Advanced GUI Installer...
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
echo    - Run option 4 or 5 (System Check with Auto-Fix)
echo    - Or install manually from Microsoft Store
echo.
echo 2. "Node.js not found" or npm errors:
echo    - Run option 4 or 5 (System Check with Auto-Fix)
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
echo 8. System compatibility check failures:
echo    - Use option 4 or 5 to re-run with fixes
echo    - Check internet connectivity
echo    - Ensure sufficient disk space (2GB+)
echo.
echo LOG LOCATIONS:
echo    - Installation logs: C:\mcp-tools\logs\
echo    - Configuration backups: C:\mcp-tools\backups\
echo    - Health status: health-status.json
echo.
pause
goto :show_main_menu

:help
echo.
echo ========================================================
echo                  COMMAND LINE HELP
echo ========================================================
echo.
echo FEATURES:
echo   - [*] Setup Wizard for guided first-time installation
echo   - [?] Auto-discovery of new MCP servers from multiple sources
echo   - [+] Template-based custom server creation
echo   - [D] Advanced Docker container management
echo   - [!] Automatic system compatibility checking with auto-fix
echo   - [^] Auto-detection of IDEs (VS Code, Cursor, Claude Desktop, etc.)
echo   - [#] Expandable server catalog with 20+ servers across 7 categories
echo   - [=] Configuration profiles for different development scenarios
echo   - [i] Smart server recommendations based on your environment
echo   - [~] Health monitoring and auto-updates
echo   - [=] Web-based dashboard for advanced management
echo   - [+] Automatic prerequisite installation with fallbacks
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
echo   - Node.js 18+ (auto-installed if missing)
echo   - Windows Package Manager (auto-installed if missing)
echo   - 2GB+ free disk space
echo   - Internet connection
echo   - Administrator privileges (recommended)
echo.
echo AUTOMATIC FEATURES:
echo   - System compatibility check runs automatically on startup
echo   - Missing prerequisites are detected and installed
echo   - Execution policy is automatically configured if needed
echo   - PATH environment variables are updated automatically
echo.
pause
goto :show_main_menu

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
:: 1. AUTOMATIC SYSTEM COMPATIBILITY CHECKING:
::    - Runs automatically when the launcher starts
::    - Detects and fixes missing prerequisites automatically
::    - Checks PowerShell version, execution policy, disk space
::    - Installs Node.js and winget if missing
::    - Only proceeds if system is ready for installation
::
:: 2. WEB DASHBOARD:
::    - Modern browser-based interface for monitoring
::    - Real-time server status and performance metrics
::    - Update management and health monitoring
::    - Mobile-responsive design with dark theme
::
:: 3. CONFIGURATION PROFILES:
::    - Pre-configured server combinations for specific use cases
::    - Web Development, Data Science, DevOps, Enterprise profiles
::    - One-click application of entire server stacks
::    - Customizable profiles for team environments
::
:: 4. AUTO-UPDATE SYSTEM:
::    - Automatic detection of server updates
::    - Version comparison and update notifications
::    - Batch update capabilities for multiple servers
::    - Rollback support for failed updates
::
:: 5. HEALTH MONITORING:
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
::    ├── System-Checker.ps1           # System compatibility checker
##    ├── Launch-Advanced-MCP.bat      # This enhanced launcher
##    └── health-status.json           # Generated health status file
::
:: USAGE WORKFLOWS:
::
:: 1. FIRST-TIME SETUP (AUTOMATIC):
::    - Run Launch-Advanced-MCP.bat
::    - System compatibility check runs automatically
::    - Missing prerequisites are installed automatically
::    - Choose installation method once system is ready
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
:: - Automatic System Checking: Runs compatibility check on startup
:: - Auto-Fix Prerequisites: Installs missing components automatically
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
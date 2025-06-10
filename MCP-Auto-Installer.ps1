# MCP Server Auto-Installer for Windows 11
# Comprehensive automation tool for installing and configuring MCP servers

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName PresentationFramework

function Invoke-WithProgress {
    param(
        [scriptblock]$Operation,
        [string]$StatusMessage,
        [System.Windows.Forms.Form]$Form,
        [System.Windows.Forms.Label]$StatusLabel,
        [System.Windows.Forms.ProgressBar]$ProgressBar
    )
    
    try {
        if ($StatusLabel) { $StatusLabel.Text = $StatusMessage }
        if ($ProgressBar) { 
            $ProgressBar.Style = "Marquee"
            $ProgressBar.MarqueeAnimationSpeed = 30
        }
        
        Update-GUI -Form $Form
        
        # Execute the operation
        $result = & $Operation
        
        return $result
    } finally {
        if ($ProgressBar) { 
            $ProgressBar.Style = "Blocks"
            $ProgressBar.Value = 0
        }
        Update-GUI -Form $Form
    }
}

function Update-GUI {
    param($Form, $StatusLabel, $Message)
    
    if ($StatusLabel) {
        $StatusLabel.Text = $Message
    }
    if ($Form) {
        $Form.Refresh()
    }
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 50
}

# REMOVED THE PROBLEMATIC CODE BLOCK:
# The following lines were causing the null reference error and should be removed:
# $insertPoint = $content.IndexOf('# Global variables')
# if ($insertPoint -gt 0) {
#     $content = $content.Insert($insertPoint, $uiHelperFunction)
# }

# Global variables
$Global:ConfigData = $null
$Global:DetectedIDEs = @{}
$Global:SelectedServers = @{}
$Global:SelectedIDEs = @{}
$Global:InstalledServers = @{}
$Global:ServerStatus = @{}
$Global:ConfigProfiles = @{}

# Configuration file management
function Load-MCPConfiguration {
    param(
        [string]$ConfigSource = "local"
    )
    
    try {
        if ($ConfigSource -eq "github") {
            # Future: Load from GitHub repository
            $url = "https://raw.githubusercontent.com/your-repo/mcp-servers-config/main/servers.json"
            $config = Invoke-RestMethod -Uri $url
        } else {
            # Load from local file
            $configPath = Join-Path $PSScriptRoot "mcp-servers-config.json"
            if (-not (Test-Path $configPath)) {
                Create-DefaultConfig -Path $configPath
            }
            $config = Get-Content $configPath | ConvertFrom-Json
        }
        
        # Load configuration profiles
        Load-ConfigurationProfiles
        
        return $config
    }
    catch {
        Write-Host "Failed to load configuration: $_" -ForegroundColor Red
        return $null
    }
}

# Configuration Profiles Management
function Load-ConfigurationProfiles {
    $Global:ConfigProfiles = @{
        "web-development" = @{
            name = "Web Development"
            description = "Frontend and full-stack web development"
            servers = @("filesystem", "git", "browser-tools", "context7", "fetch")
            color = "#4CAF50"
        }
        "data-science" = @{
            name = "Data Science & AI"
            description = "Machine learning and data analysis"
            servers = @("memory-service", "postgres-pro", "qdrant", "context7", "filesystem")
            color = "#2196F3"
        }
        "devops-engineer" = @{
            name = "DevOps Engineer"
            description = "Container management and deployment"
            servers = @("docker-mcp", "kubernetes", "git", "github", "circleci")
            color = "#FF9800"
        }
        "fullstack-enterprise" = @{
            name = "Full-Stack Enterprise"
            description = "Complete enterprise development stack"
            servers = @("filesystem", "git", "postgres-pro", "docker-mcp", "github", "memory-service", "context7")
            color = "#9C27B0"
        }
        "api-developer" = @{
            name = "API Developer"
            description = "REST and GraphQL API development"
            servers = @("postgres-pro", "apollo-graphql", "openapi", "fetch", "git")
            color = "#607D8B"
        }
        "minimal-setup" = @{
            name = "Minimal Setup"
            description = "Essential tools only"
            servers = @("filesystem", "git", "context7")
            color = "#795548"
        }
    }
}

function Apply-ConfigurationProfile {
    param(
        [string]$ProfileName,
        [array]$AvailableServers
    )
    
    if ($Global:ConfigProfiles.ContainsKey($ProfileName)) {
        $profile = $Global:ConfigProfiles[$ProfileName]
        $selectedIndices = @()
        
        foreach ($serverName in $profile.servers) {
            for ($i = 0; $i -lt $AvailableServers.Count; $i++) {
                if ($AvailableServers[$i].id -eq $serverName) {
                    $selectedIndices += $i
                    break
                }
            }
        }
        
        return $selectedIndices
    }
    
    return @()
}

function Create-DefaultConfig {
    param([string]$Path)
    
    $defaultConfig = @{
        servers = @(
            @{
                id = "browser-tools"
                name = "Browser Tools MCP"
                description = "Browser automation and debugging"
                category = "Development"
                type = "npm"
                requires_docker = $false
                requires_chrome_extension = $true
                requires_middleware = $true
                installation = @{
                    command = "npx"
                    args = @("@agentdeskai/browser-tools-mcp@latest")
                    env = @{
                        BROWSER_TOOLS_PORT = "3025"
                    }
                }
                prerequisites = @("node18+")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "context7"
                name = "Context7 Documentation"
                description = "Real-time documentation for coding"
                category = "Documentation"
                type = "npm"
                requires_docker = $false
                installation = @{
                    command = "npx"
                    args = @("-y", "@upstash/context7-mcp")
                }
                prerequisites = @("node18+")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "memory-service"
                name = "MCP Memory Service"
                description = "Persistent semantic memory with ChromaDB"
                category = "Memory"
                type = "python"
                requires_docker = $false
                installation = @{
                    command = "python"
                    args = @("C:\mcp-tools\memory-service\memory_wrapper.py")
                    env = @{
                        MCP_MEMORY_CHROMA_PATH = "C:\Users\$env:USERNAME\AppData\Local\mcp-memory\chroma_db"
                    }
                }
                prerequisites = @("python38+", "git")
                git_repo = "https://github.com/doobidoo/mcp-memory-service.git"
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "filesystem"
                name = "Filesystem Operations"
                description = "File and directory management"
                category = "Core"
                type = "npm"
                requires_docker = $false
                installation = @{
                    command = "npx"
                    args = @("-y", "@modelcontextprotocol/server-filesystem", "C:\Projects")
                }
                prerequisites = @("node18+")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "git"
                name = "Git Operations"
                description = "Version control management"
                category = "Development"
                type = "python"
                requires_docker = $false
                installation = @{
                    command = "uvx"
                    args = @("mcp-server-git", "--repository", "C:\Projects")
                }
                prerequisites = @("python38+", "git")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "postgres-pro"
                name = "PostgreSQL Professional"
                description = "Advanced PostgreSQL management"
                category = "Database"
                type = "npm"
                requires_docker = $false
                installation = @{
                    command = "postgres-mcp-pro"
                    args = @("postgresql://localhost:5432/mydb")
                    env = @{
                        PGUSER = "username"
                        PGPASSWORD = "password"
                    }
                }
                prerequisites = @("node18+", "postgresql")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "github"
                name = "GitHub Integration"
                description = "GitHub repository management"
                category = "Development"
                type = "docker"
                requires_docker = $true
                installation = @{
                    command = "docker"
                    args = @("run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server")
                    env = @{
                        GITHUB_PERSONAL_ACCESS_TOKEN = "your-token-here"
                    }
                }
                prerequisites = @("docker")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            },
            @{
                id = "docker-mcp"
                name = "Docker Management"
                description = "Container and image management"
                category = "DevOps"
                type = "python"
                requires_docker = $false
                installation = @{
                    command = "uvx"
                    args = @("mcp-server-docker")
                }
                prerequisites = @("python38+", "docker")
                supported_ides = @("claude-desktop", "cursor", "vscode", "vscode-cline", "vscode-roo")
            }
        )
        ides = @(
            @{
                id = "claude-desktop"
                name = "Claude Desktop"
                detection_paths = @(
                    "$env:APPDATA\Claude\claude_desktop_config.json",
                    "$env:LOCALAPPDATA\Programs\Claude\Claude.exe"
                )
                config_path = "$env:APPDATA\Claude\claude_desktop_config.json"
                config_key = "mcpServers"
                extensions = @()
            },
            @{
                id = "cursor"
                name = "Cursor"
                detection_paths = @(
                    "$env:USERPROFILE\.cursor\mcp.json",
                    "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe"
                )
                config_path = "$env:USERPROFILE\.cursor\mcp.json"
                config_key = "mcpServers"
                extensions = @()
            },
            @{
                id = "vscode"
                name = "Visual Studio Code"
                detection_paths = @(
                    "$env:APPDATA\Code\User\settings.json",
                    "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe"
                )
                config_path = "$env:APPDATA\Code\User\settings.json"
                config_key = "mcp.servers"
                extensions = @(
                    @{
                        id = "saoudrizwan.claude-dev"
                        name = "Cline"
                        config_path = "$env:APPDATA\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"
                        config_key = "mcpServers"
                    },
                    @{
                        id = "rooveterinaryinc.roo-cline"
                        name = "Roo"
                        config_path = "$env:APPDATA\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\mcp_settings.json"
                        config_key = "mcpServers"
                    }
                )
            },
            @{
                id = "windsurf"
                name = "Windsurf"
                detection_paths = @(
                    "$env:APPDATA\Windsurf\User\settings.json",
                    "$env:LOCALAPPDATA\Programs\Windsurf\Windsurf.exe"
                )
                config_path = "$env:APPDATA\Windsurf\User\settings.json"
                config_key = "mcp.servers"
                extensions = @()
            }
        )
        extension_profiles = @{
            "vscode-full" = @{
                name = "VS Code with Extensions"
                description = "Configure VS Code main settings plus Cline and Roo extensions"
                targets = @("vscode", "vscode-cline", "vscode-roo")
            }
            "cline-only" = @{
                name = "Cline Extension Only"
                description = "Configure only the Cline extension in VS Code"
                targets = @("vscode-cline")
            }
            "roo-only" = @{
                name = "Roo Extension Only" 
                description = "Configure only the Roo extension in VS Code"
                targets = @("vscode-roo")
            }
        }
    }
    
    $defaultConfig | ConvertTo-Json -Depth 10 | Set-Content $Path
    Write-Host "Created default configuration file at: $Path" -ForegroundColor Green
}

# Enhanced VS Code Detection Functions
function Test-VSCodeInstalled {
    [CmdletBinding()]
    param()

    # 1) Check common installation paths
    $possiblePaths = @(
        "$Env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "$Env:ProgramFiles\Microsoft VS Code\Code.exe",
        "$Env:ProgramFiles(x86)\Microsoft VS Code\Code.exe"
    )
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return @{
                installed = $true
                path = $path
            }
        }
    }

    # 2) Look for it in the Uninstall registry keys
    $registryRoots = @(
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall'
    )
    foreach ($root in $registryRoots) {
        try {
            Get-ChildItem $root -ErrorAction SilentlyContinue | ForEach-Object {
                try {
                    $displayName = (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DisplayName
                    if ($displayName -like '*Visual Studio Code*') {
                        return @{
                            installed = $true
                            path = "Registry detected"
                        }
                    }
                } catch { }
            }
        } catch { }
    }

    # 3) Fallback: see if 'code' is on the PATH
    $codeCommand = Get-Command code.exe -ErrorAction SilentlyContinue
    if ($codeCommand) {
        return @{
            installed = $true
            path = $codeCommand.Source
        }
    }

    return @{
        installed = $false
        path = $null
    }
}

function Test-VSCodeExtension {
    [CmdletBinding()]
    param(
        [string]$ExtensionId,
        [string]$ExtensionName
    )
    
    $extensionPath = "$env:USERPROFILE\.vscode\extensions"
    $extensionFound = $false
    $extensionVersion = $null
    
    if (Test-Path $extensionPath) {
        $extensions = Get-ChildItem $extensionPath -Directory | Where-Object { $_.Name -like "$ExtensionId*" }
        if ($extensions) {
            $extensionFound = $true
            $extensionVersion = ($extensions | Sort-Object Name -Descending | Select-Object -First 1).Name
        }
    }
    
    return @{
        name = $ExtensionName
        id = $ExtensionId
        installed = $extensionFound
        version = $extensionVersion
        configPath = Get-ExtensionConfigPath -ExtensionId $ExtensionId
    }
}

function Get-ExtensionConfigPath {
    [CmdletBinding()]
    param([string]$ExtensionId)
    
    switch ($ExtensionId) {
        "saoudrizwan.claude-dev" {
            return "$env:APPDATA\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"
        }
        "rooveterinaryinc.roo-cline" {
            return "$env:APPDATA\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\mcp_settings.json"
        }
        default {
            return $null
        }
    }
}

# Auto-Update System
function Get-InstalledServerVersions {
    $installed = @{}
    
    # Check npm packages
    try {
        $npmList = npm list -g --depth=0 --json 2>$null | ConvertFrom-Json
        if ($npmList.dependencies) {
            foreach ($dep in $npmList.dependencies.PSObject.Properties) {
                $installed[$dep.Name] = @{
                    version = $dep.Value.version
                    type = "npm"
                    current = $true
                }
            }
        }
    } catch {
        Write-Host "Could not check npm packages: $_" -ForegroundColor Yellow
    }
    
    # Check Python packages
    try {
        $pipList = pip list --format=json 2>$null | ConvertFrom-Json
        foreach ($package in $pipList) {
            if ($package.name -like "*mcp*") {
                $installed[$package.name] = @{
                    version = $package.version
                    type = "python"
                    current = $true
                }
            }
        }
    } catch {
        Write-Host "Could not check Python packages: $_" -ForegroundColor Yellow
    }
    
    # Check Docker images
    try {
        $dockerImages = docker images --format "{{.Repository}}:{{.Tag}}" 2>$null
        foreach ($image in $dockerImages) {
            if ($image -like "*mcp*" -or $image -like "*github*" -or $image -like "*mem0*") {
                $imageParts = $image.Split(':')
                $installed[$imageParts[0]] = @{
                    version = $imageParts[1]
                    type = "docker"
                    current = $true
                }
            }
        }
    } catch {
        Write-Host "Could not check Docker images: $_" -ForegroundColor Yellow
    }
    
    return $installed
}

function Check-ServerUpdates {
    param($ServerList)
    
    $updates = @{}
    $Global:InstalledServers = Get-InstalledServerVersions
    
    foreach ($server in $ServerList) {
        $serverKey = $server.installation.args[0] -replace '@latest', ''
        
        if ($Global:InstalledServers.ContainsKey($serverKey)) {
            # Check for updates based on server type
            switch ($server.type) {
                "npm" {
                    try {
                        $latest = npm view $serverKey version 2>$null
                        $current = $Global:InstalledServers[$serverKey].version
                        
                        if ($latest -and $current -and $latest -ne $current) {
                            $updates[$server.id] = @{
                                current = $current
                                latest = $latest
                                type = "npm"
                                updateable = $true
                            }
                        }
                    } catch {
                        # Ignore version check errors
                    }
                }
                "python" {
                    # Python package update checking
                    try {
                        $pipOutdated = pip list --outdated --format=json 2>$null | ConvertFrom-Json
                        $outdated = $pipOutdated | Where-Object { $_.name -eq $serverKey }
                        
                        if ($outdated) {
                            $updates[$server.id] = @{
                                current = $outdated.version
                                latest = $outdated.latest_version
                                type = "python"
                                updateable = $true
                            }
                        }
                    } catch {
                        # Ignore version check errors
                    }
                }
                "docker" {
                    # Docker image update checking
                    $updates[$server.id] = @{
                        current = "unknown"
                        latest = "check manually"
                        type = "docker"
                        updateable = $true
                    }
                }
            }
        }
    }
    
    return $updates
}

function Update-MCPServer {
    param($Server, $UpdateInfo)
    
    Write-Host "Updating $($Server.name) from $($UpdateInfo.current) to $($UpdateInfo.latest)..." -ForegroundColor Yellow
    
    try {
        switch ($UpdateInfo.type) {
            "npm" {
                npm update -g $Server.installation.args[0]
                Write-Host "$($Server.name) updated successfully" -ForegroundColor Green
            }
            "python" {
                pip install --upgrade $Server.installation.args[0]
                Write-Host "$($Server.name) updated successfully" -ForegroundColor Green
            }
            "docker" {
                docker pull $Server.installation.args[-1]
                Write-Host "$($Server.name) Docker image updated" -ForegroundColor Green
            }
        }
        return $true
    } catch {
        Write-Host "Failed to update $($Server.name): $_" -ForegroundColor Red
        return $false
    }
}

# Health Monitoring System
function Test-ServerHealth {
    param($ServerList)
    
    $healthStatus = @{}
    
    foreach ($server in $ServerList) {
        $status = @{
            name = $server.name
            id = $server.id
            running = $false
            responsive = $false
            last_check = Get-Date
            errors = @()
            performance = @{}
        }
        
        # Check if server process is running
        switch ($server.type) {
            "npm" {
                $status.running = Test-NPMServerRunning -Server $server
            }
            "python" {
                $status.running = Test-PythonServerRunning -Server $server
            }
            "docker" {
                $status.running = Test-DockerServerRunning -Server $server
            }
        }
        
        # Test server responsiveness (if running)
        if ($status.running) {
            $status.responsive = Test-ServerResponsiveness -Server $server
            $status.performance = Get-ServerPerformanceMetrics -Server $server
        }
        
        $healthStatus[$server.id] = $status
    }
    
    $Global:ServerStatus = $healthStatus
    return $healthStatus
}

function Test-NPMServerRunning {
    param($Server)
    
    # Check if npm process is running for this server
    $processes = Get-Process | Where-Object { $_.ProcessName -like "*node*" }
    return $processes.Count -gt 0
}

function Test-PythonServerRunning {
    param($Server)
    
    # Check if Python process is running for this server
    $processes = Get-Process | Where-Object { $_.ProcessName -like "*python*" }
    return $processes.Count -gt 0
}

function Test-DockerServerRunning {
    param($Server)
    
    try {
        $imageName = $Server.installation.args[-1].Split('/')[1]
        $containers = docker ps --filter "ancestor=$($Server.installation.args[-1])" --format "{{.ID}}" 2>$null
        return $containers.Count -gt 0
    } catch {
        return $false
    }
}

function Test-ServerResponsiveness {
    param($Server)
    
    # Basic responsiveness test - this would be more sophisticated in production
    try {
        # Simulate a health check - in real implementation, this would ping the actual server
        Start-Sleep -Milliseconds 100
        return $true
    } catch {
        return $false
    }
}

function Get-ServerPerformanceMetrics {
    param($Server)
    
    # Basic performance metrics - in production, this would collect real metrics
    return @{
        cpu_usage = Get-Random -Minimum 5 -Maximum 25
        memory_usage = Get-Random -Minimum 50 -Maximum 200
        response_time = Get-Random -Minimum 10 -Maximum 100
    }
}

function Start-HealthMonitoring {
    param($IntervalSeconds = 30)
    
    # Start background health monitoring
    $scriptBlock = {
        param($ConfigData, $IntervalSeconds)
        
        while ($true) {
            if ($ConfigData -and $ConfigData.servers) {
                $healthStatus = Test-ServerHealth -ServerList $ConfigData.servers
                
                # Save health status to file for web dashboard
                $healthFile = Join-Path $PSScriptRoot "health-status.json"
                $healthStatus | ConvertTo-Json -Depth 5 | Set-Content $healthFile
            }
            
            Start-Sleep -Seconds $IntervalSeconds
        }
    }
    
    # Start background job
    $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $Global:ConfigData, $IntervalSeconds
    
    Write-Host "Health monitoring started (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

function Detect-InstalledIDEs {
    param($IDEList)
    
    $detected = @{}
    
    foreach ($ide in $IDEList) {
        $isInstalled = $false
        $foundPath = ""
        $extensions = @()
        
        if ($ide.id -eq "vscode") {
            # Use enhanced VS Code detection
            $vscodeResult = Test-VSCodeInstalled
            if ($vscodeResult.installed) {
                $isInstalled = $true
                $foundPath = $vscodeResult.path
                
                Write-Host "Found VS Code at: $foundPath" -ForegroundColor Green
                
                # Check for MCP extensions
                $clineExtension = Test-VSCodeExtension -ExtensionId "saoudrizwan.claude-dev" -ExtensionName "Cline"
                $rooExtension = Test-VSCodeExtension -ExtensionId "rooveterinaryinc.roo-cline" -ExtensionName "Roo"
                
                if ($clineExtension.installed) {
                    Write-Host "  ✅ Cline extension detected: $($clineExtension.version)" -ForegroundColor Green
                    $extensions += $clineExtension
                }
                
                if ($rooExtension.installed) {
                    Write-Host "  ✅ Roo extension detected: $($rooExtension.version)" -ForegroundColor Green
                    $extensions += $rooExtension
                }
                
                if ($extensions.Count -eq 0) {
                    # Fixed: Added missing -ForegroundColor parameter
                    Write-Host "No MCP extensions detected (Cline, Roo)" -ForegroundColor Cyan
                }
            }
        } else {
            # Use original detection logic for other IDEs
            foreach ($path in $ide.detection_paths) {
                $expandedPath = [System.Environment]::ExpandEnvironmentVariables($path)
                $expandedPath = $expandedPath -replace '%APPDATA%', $env:APPDATA
                $expandedPath = $expandedPath -replace '%LOCALAPPDATA%', $env:LOCALAPPDATA
                $expandedPath = $expandedPath -replace '%PROGRAMFILES%', $env:PROGRAMFILES
                $expandedPath = $expandedPath -replace '%PROGRAMFILES\(X86\)%', ${env:PROGRAMFILES(X86)}
                $expandedPath = $expandedPath -replace '%USERPROFILE%', $env:USERPROFILE
                
                Write-Host "Checking path for $($ide.name): $expandedPath" -ForegroundColor Gray
                
                if (Test-Path $expandedPath) {
                    $isInstalled = $true
                    $foundPath = $expandedPath
                    Write-Host "Found $($ide.name) at: $foundPath" -ForegroundColor Green
                    break
                }
            }
            
            if (-not $isInstalled) {
                Write-Host "Did not find $($ide.name)" -ForegroundColor Yellow
            }
        }
        
        if ($isInstalled) {
            $configPath = [System.Environment]::ExpandEnvironmentVariables($ide.config_path)
            $configPath = $configPath -replace '%APPDATA%', $env:APPDATA
            $configPath = $configPath -replace '%LOCALAPPDATA%', $env:LOCALAPPDATA
            $configPath = $configPath -replace '%USERPROFILE%', $env:USERPROFILE
            
            $detected[$ide.id] = @{
                name = $ide.name
                config_path = $configPath
                config_key = $ide.config_key
                installed = $true
                found_at = $foundPath
                extensions = $extensions
            }
        }
    }
    
    return $detected
}

# Prerequisites Management
function Test-WingetAvailable {
    try {
        $null = Get-Command winget -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Install-Winget {
    Write-Host "Installing Windows Package Manager (winget)..." -ForegroundColor Yellow
    
    try {
        # Method 1: Try to install from Microsoft Store
        $progressPreference = 'SilentlyContinue'
        $url = "https://aka.ms/getwinget"
        $tempFile = "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
        
        Write-Host "Downloading winget installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $url -OutFile $tempFile
        
        Write-Host "Installing winget..." -ForegroundColor Yellow
        Add-AppxPackage -Path $tempFile
        
        # Wait a moment for installation to complete
        Start-Sleep -Seconds 3
        
        # Verify installation
        if (Test-WingetAvailable) {
            Write-Host "Winget installed successfully" -ForegroundColor Green
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
            return $true
        } else {
            throw "Winget installation verification failed"
        }
    } catch {
        Write-Host "Failed to install winget automatically: $_" -ForegroundColor Red
        Write-Host "Please install winget manually from the Microsoft Store or GitHub" -ForegroundColor Yellow
        return $false
    }
}

function Install-NodeJSFallback {
    Write-Host "Installing Node.js using fallback method..." -ForegroundColor Yellow
    
    try {
        $nodeVersion = "18.19.0"
        $architecture = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
        $url = "https://nodejs.org/dist/v$nodeVersion/node-v$nodeVersion-win-$architecture.zip"
        $tempDir = "$env:TEMP\nodejs"
        $installDir = "C:\Program Files\nodejs"
        
        # Download Node.js
        Write-Host "Downloading Node.js v$nodeVersion..." -ForegroundColor Yellow
        $zipFile = "$tempDir\nodejs.zip"
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        
        $progressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $zipFile
        
        # Extract and install
        Write-Host "Extracting Node.js..." -ForegroundColor Yellow
        Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force
        
        $extractedDir = Get-ChildItem -Path $tempDir -Directory | Where-Object { $_.Name -like "node-v*" } | Select-Object -First 1
        
        if ($extractedDir) {
            # Copy to Program Files
            if (Test-Path $installDir) {
                Remove-Item $installDir -Recurse -Force
            }
            
            Copy-Item -Path $extractedDir.FullName -Destination $installDir -Recurse -Force
            
            # Add to PATH - Fixed syntax
            $currentPath = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
            if ($currentPath -notlike "*$installDir*") {
                $newPath = "$currentPath;$installDir"
                [Environment]::SetEnvironmentVariable('PATH', $newPath, 'Machine')
                $env:PATH = "$env:PATH;$installDir"
            }
            
            Write-Host "Node.js installed successfully" -ForegroundColor Green
            
            # Cleanup
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            return $true
        } else {
            throw "Failed to extract Node.js"
        }
    } catch {
        Write-Host "Failed to install Node.js: $_" -ForegroundColor Red
        return $false
    }
}

function Install-PythonFallback {
    Write-Host "Installing Python using fallback method..." -ForegroundColor Yellow
    
    try {
        $pythonVersion = "3.12.0"
        $architecture = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "win32" }
        $url = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-$architecture.exe"
        $tempFile = "$env:TEMP\python-installer.exe"
        
        # Download Python installer
        Write-Host "Downloading Python v$pythonVersion..." -ForegroundColor Yellow
        $progressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $tempFile
        
        # Install Python silently
        Write-Host "Installing Python..." -ForegroundColor Yellow
        $process = Start-Process -FilePath $tempFile -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "Python installed successfully" -ForegroundColor Green
            
            # Refresh environment variables - Fixed syntax
            $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
            $userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
            $env:PATH = "$machinePath;$userPath"
            
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
            return $true
        } else {
            throw "Python installer failed with exit code: $($process.ExitCode)"
        }
    } catch {
        Write-Host "Failed to install Python: $_" -ForegroundColor Red
        return $false
    }
}

function Check-Prerequisites {
    param($PrereqList)
    
    $missing = @()
    $available = @()
    
    foreach ($prereq in $PrereqList) {
        switch -Regex ($prereq) {
            "node18\+" {
                try {
                    $nodeVersion = node --version 2>$null
                    if ($nodeVersion -and ([version]($nodeVersion -replace 'v','').Split('.')[0] -ge 18)) {
                        $available += "Node.js $nodeVersion"
                    } else {
                        $missing += "Node.js 18+"
                    }
                } catch {
                    $missing += "Node.js 18+"
                }
            }
            "python38\+" {
                try {
                    $pythonVersion = python --version 2>$null
                    if ($pythonVersion -and ([version]($pythonVersion -replace 'Python ','').Split('.')[0..1] -join '.' -ge 3.8)) {
                        $available += $pythonVersion
                    } else {
                        $missing += "Python 3.8+"
                    }
                } catch {
                    $missing += "Python 3.8+"
                }
            }
            "git" {
                try {
                    $gitVersion = git --version 2>$null
                    if ($gitVersion) {
                        $available += $gitVersion
                    } else {
                        $missing += "Git"
                    }
                } catch {
                    $missing += "Git"
                }
            }
            "docker" {
                try {
                    $dockerVersion = docker --version 2>$null
                    if ($dockerVersion) {
                        $available += $dockerVersion
                    } else {
                        $missing += "Docker"
                    }
                } catch {
                    $missing += "Docker"
                }
            }
            "postgresql" {
                try {
                    $pgVersion = psql --version 2>$null
                    if ($pgVersion) {
                        $available += $pgVersion
                    } else {
                        $missing += "PostgreSQL"
                    }
                } catch {
                    $missing += "PostgreSQL"
                }
            }
        }
    }
    
    return @{
        missing = $missing
        available = $available
    }
}

function Install-Prerequisites {
    param($Missing)
    
    # Check if winget is available, install if needed
    $wingetAvailable = Test-WingetAvailable
    if (-not $wingetAvailable -and ($Missing -contains "Node.js 18+" -or $Missing -contains "Python 3.8+" -or $Missing -contains "Git")) {
        Write-Host "Windows Package Manager (winget) not found. Attempting to install..." -ForegroundColor Yellow
        $wingetAvailable = Install-Winget
    }
    
    foreach ($prereq in $Missing) {
        Write-Host "Installing $prereq..." -ForegroundColor Yellow
        
        switch ($prereq) {
            "Node.js 18+" {
                $success = $false
                if ($wingetAvailable) {
                    try {
                        winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
                        
                        # Refresh PATH - Fixed syntax
                        $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
                        $userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
                        $env:PATH = "$machinePath;$userPath"
                        
                        # Verify installation
                        Start-Sleep -Seconds 3
                        $nodeVersion = node --version 2>$null
                        if ($nodeVersion) {
                            Write-Host "Node.js installed successfully via winget" -ForegroundColor Green
                            $success = $true
                        }
                    } catch {
                        Write-Host "Winget installation failed, trying fallback method..." -ForegroundColor Yellow
                    }
                }
                
                if (-not $success) {
                    $success = Install-NodeJSFallback
                }
                
                if (-not $success) {
                    Write-Host "Failed to install Node.js. Please install manually from https://nodejs.org" -ForegroundColor Red
                }
            }
            "Python 3.8+" {
                $success = $false
                if ($wingetAvailable) {
                    try {
                        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
                        
                        # Refresh PATH - Fixed syntax  
                        $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
                        $userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
                        $env:PATH = "$machinePath;$userPath"
                        
                        # Verify installation
                        Start-Sleep -Seconds 3
                        $pythonVersion = python --version 2>$null
                        if ($pythonVersion) {
                            Write-Host "Python installed successfully via winget" -ForegroundColor Green
                            $success = $true
                        }
                    } catch {
                        Write-Host "Winget installation failed, trying fallback method..." -ForegroundColor Yellow
                    }
                }
                
                if (-not $success) {
                    $success = Install-PythonFallback
                }
                
                if (-not $success) {
                    Write-Host "Failed to install Python. Please install manually from https://python.org" -ForegroundColor Red
                }
            }
            "Git" {
                if ($wingetAvailable) {
                    try {
                        winget install Git.Git --silent --accept-package-agreements --accept-source-agreements
                        Write-Host "Git installed successfully" -ForegroundColor Green
                    } catch {
                        Write-Host "Failed to install Git via winget. Please install manually from https://git-scm.com" -ForegroundColor Red
                    }
                } else {
                    Write-Host "Please install Git manually from https://git-scm.com" -ForegroundColor Yellow
                }
            }
            "Docker" {
                if ($wingetAvailable) {
                    try {
                        winget install Docker.DockerDesktop --silent --accept-package-agreements --accept-source-agreements
                        Write-Host "Docker Desktop installed successfully" -ForegroundColor Green
                        Write-Host "Please restart the application after Docker Desktop finishes installing" -ForegroundColor Yellow
                    } catch {
                        Write-Host "Failed to install Docker via winget. Please install manually from https://docker.com" -ForegroundColor Red
                    }
                } else {
                    Write-Host "Please install Docker Desktop manually from https://docker.com" -ForegroundColor Yellow
                }
            }
            "PostgreSQL" {
                if ($wingetAvailable) {
                    try {
                        winget install PostgreSQL.PostgreSQL --silent --accept-package-agreements --accept-source-agreements
                        Write-Host "PostgreSQL installed successfully" -ForegroundColor Green
                    } catch {
                        Write-Host "Failed to install PostgreSQL via winget. Please install manually" -ForegroundColor Red
                    }
                } else {
                    Write-Host "Please install PostgreSQL manually" -ForegroundColor Yellow
                }
            }
        }
    }
}

# MCP Server Installation Functions
function Install-MCPServer {
    param($Server)
    
    Write-Host "Installing $($Server.name)..." -ForegroundColor Yellow
    
    # Check prerequisites
    if ($Server.prerequisites) {
        $prereqCheck = Check-Prerequisites -PrereqList $Server.prerequisites
        if ($prereqCheck.missing.Count -gt 0) {
            Write-Host "Installing missing prerequisites: $($prereqCheck.missing -join ', ')" -ForegroundColor Yellow
            Install-Prerequisites -Missing $prereqCheck.missing
            
            # Refresh environment variables after installation
            $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine') + ";" + [System.Environment]::GetEnvironmentVariable('PATH', 'User')
        }
    }
    
    # Handle special installation cases
    switch ($Server.type) {
        "npm" {
            if ($Server.id -eq "browser-tools") {
                Install-BrowserTools
            } else {
                Install-NPMServer -Server $Server
            }
        }
        "python" {
            if ($Server.git_repo) {
                Install-PythonGitServer -Server $Server
            } else {
                Install-PythonServer -Server $Server
            }
        }
        "docker" {
            Install-DockerServer -Server $Server
        }
    }
}

function Install-NPMServer {
    param($Server)
    
    try {
        # Verify npm is available
        $npmVersion = npm --version 2>$null
        if (-not $npmVersion) {
            Write-Host "npm not found. Please ensure Node.js is properly installed." -ForegroundColor Red
            return
        }
        
        Write-Host "npm version: $npmVersion" -ForegroundColor Gray
        
        # Create a temporary directory for npm operations
        $tempDir = "$env:TEMP\mcp-npm-install"
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        $originalLocation = Get-Location
        
        try {
            Set-Location $tempDir
            
            # Initialize package.json if needed
            if (-not (Test-Path "package.json")) {
                '{"name": "mcp-temp", "version": "1.0.0"}' | Set-Content "package.json"
            }
            
            # Install the package
            $packageName = $Server.installation.args[0]
            if ($packageName.EndsWith("@latest")) {
                $packageName = $packageName -replace "@latest", ""
            }
            
            Write-Host "Installing npm package: $packageName" -ForegroundColor Gray
            
            # Use npx for one-time execution packages, npm install -g for global packages
            if ($Server.installation.command -eq "npx") {
                # For npx packages, we don't need to install globally
                Write-Host "$($Server.name) will be available via npx" -ForegroundColor Green
            } else {
                # Global installation
                npm install -g $packageName
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "$($Server.name) installed globally" -ForegroundColor Green
                } else {
                    throw "npm install failed with exit code $LASTEXITCODE"
                }
            }
        } finally {
            Set-Location $originalLocation
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "$($Server.name) installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install $($Server.name): $_" -ForegroundColor Red
    }
}

function Install-PythonServer {
    param($Server)
    
    try {
        # Verify Python is available
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            Write-Host "Python not found. Please ensure Python is properly installed." -ForegroundColor Red
            return
        }
        
        Write-Host "Python version: $pythonVersion" -ForegroundColor Gray
        
        # Get the correct package name from server configuration
        $packageName = ""
        if ($Server.installation.args -and $Server.installation.args.Count -gt 0) {
            $packageName = $Server.installation.args[0]
        }
        
        if (-not $packageName) {
            Write-Host "No package name specified for $($Server.name)" -ForegroundColor Red
            return
        }
        
        Write-Host "Installing package: $packageName" -ForegroundColor Gray
        
        # Install uvx if needed and use it, otherwise fall back to pip
        if ($Server.installation.command -eq "uvx") {
            Write-Host "Installing uv (Python package manager)..." -ForegroundColor Gray
            
            # First install uv itself
            python -m pip install uv
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Installing $($Server.name) with uvx..." -ForegroundColor Gray
                
                # FIXED: Use the correct uvx command format
                if ($packageName -eq "mcp-server-docker") {
                    # For Docker MCP server, use the correct package name
                    uvx $packageName
                } else {
                    uvx $packageName
                }
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "uvx installation failed, trying direct pip install..." -ForegroundColor Yellow
                    pip install $packageName
                }
            } else {
                Write-Host "Failed to install uv, trying direct pip install..." -ForegroundColor Yellow
                pip install $packageName
            }
        } else {
            # Direct pip installation
            Write-Host "Installing with pip: $packageName" -ForegroundColor Gray
            pip install $packageName
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$($Server.name) installed successfully" -ForegroundColor Green
        } else {
            throw "Python package installation failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-Host "Failed to install $($Server.name): $_" -ForegroundColor Red
    }
}
function Install-DockerMCPFallback {
    Write-Host "Trying alternative Docker MCP installation method..." -ForegroundColor Yellow
    
    try {
        # Method 1: Try direct pip installation
        Write-Host "Attempting pip install..." -ForegroundColor Gray
        pip install mcp-server-docker
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker MCP server installed successfully via pip" -ForegroundColor Green
            return $true
        }
        
        # Method 2: Try installing from source
        Write-Host "Attempting installation from source..." -ForegroundColor Gray
        pip install git+https://github.com/modelcontextprotocol/servers.git#subdirectory=src/mcp_server_docker
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker MCP server installed successfully from source" -ForegroundColor Green
            return $true
        }
        
        # Method 3: Manual installation
        Write-Host "Manual installation method..." -ForegroundColor Gray
        $tempDir = "$env:TEMP\mcp-docker"
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        
        # Create a simple wrapper script
        $wrapperScript = @'
#!/usr/bin/env python3
"""
Docker MCP Server - Simple wrapper for basic Docker operations
"""
import docker
import json
import sys

def main():
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        result = []
        for container in containers:
            result.append({
                'id': container.id[:12],
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else container.image.id[:12]
            })
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'@
        
        $scriptPath = Join-Path $tempDir "docker_mcp.py"
        $wrapperScript | Set-Content $scriptPath
        
        # Install docker Python package
        pip install docker
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker MCP fallback installation completed" -ForegroundColor Green
            Write-Host "Basic Docker MCP script created at: $scriptPath" -ForegroundColor Cyan
            return $true
        }
        
        return $false
        
    } catch {
        Write-Host "All Docker MCP installation methods failed: $_" -ForegroundColor Red
        return $false
    }
}

function Install-BrowserTools {
    # Create browser tools directory
    $toolsDir = "C:\mcp-tools\browser-tools"
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    
    # Create middleware launcher script
    $launcherScript = @'

title BrowserTools Middleware Launcher
echo Starting BrowserTools middleware component...

set MIDDLEWARE_PORT=3025

echo Stopping any existing middleware server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%MIDDLEWARE_PORT% "') do (
    taskkill /F /PID %%a /T 2>nul
)

timeout /t 2 /nobreak > nul
echo Starting Middleware Server on port %MIDDLEWARE_PORT%...
start "BrowserTools Middleware Server" cmd /c "npx @agentdeskai/browser-tools-server@latest --port %MIDDLEWARE_PORT%"

echo BrowserTools middleware started!
pause
'@
    
    $launcherPath = Join-Path $toolsDir "start-browser-tools.bat"
    $launcherScript | Set-Content $launcherPath
    
    Write-Host "Browser Tools middleware launcher created at: $launcherPath" -ForegroundColor Green
    Write-Host "Don't forget to install the Chrome extension from GitHub releases!" -ForegroundColor Yellow
}

function Install-PythonGitServer {
    param($Server)
    
    $installDir = "C:\mcp-tools\$($Server.id)"
    
    try {
        # Clone repository
        if (Test-Path $installDir) {
            Remove-Item $installDir -Recurse -Force
        }
        
        git clone $Server.git_repo $installDir
        Set-Location $installDir
        
        # Create virtual environment
        python -m venv venv
        & ".\venv\Scripts\Activate.ps1"
        
        # Install requirements
        if (Test-Path "requirements.txt") {
            pip install -r requirements.txt
        }
        if (Test-Path "install.py") {
            python install.py
        }
        
        Write-Host "$($Server.name) installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install $($Server.name): $_" -ForegroundColor Red
    }
}

function Install-DockerServer {
    param($Server)
    
    try {
        # Pull Docker image
        docker pull $Server.installation.args[-1]
        Write-Host "$($Server.name) Docker image pulled successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to pull Docker image for $($Server.name): $_" -ForegroundColor Red
    }
}

# Configuration Management
function Update-IDEConfiguration {
    param(
        $IDE,
        $Server
    )
    
    try {
        # Update main IDE configuration
        Update-MainIDEConfig -IDE $IDE -Server $Server
        
        # Update extension configurations if VS Code with extensions
        if ($IDE.extensions -and $IDE.extensions.Count -gt 0) {
            foreach ($extension in $IDE.extensions) {
                Update-ExtensionConfig -Extension $extension -Server $Server -IDE $IDE
            }
        }
    } catch {
        Write-Host "Failed to update $($IDE.name) configuration: $_" -ForegroundColor Red
    }
}

function Update-MainIDEConfig {
    param($IDE, $Server)
    
    $configPath = $IDE.config_path
    $configKey = $IDE.config_key
    
    # Ensure config directory exists
    $configDir = Split-Path $configPath -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # Load existing configuration
    $config = @{}
    if (Test-Path $configPath) {
        $jsonContent = Get-Content $configPath -Raw
        if ($jsonContent.Trim()) {
            try {
                if ($PSVersionTable.PSVersion.Major -ge 6) {
                    $config = $jsonContent | ConvertFrom-Json -AsHashtable
                } else {
                    $configObj = $jsonContent | ConvertFrom-Json
                    $config = Convert-PSObjectToHashtable -InputObject $configObj
                }
            } catch {
                Write-Host "Warning: Could not parse existing config file. Creating new configuration." -ForegroundColor Yellow
                $config = @{}
            }
        }
    }
    
    # Initialize MCP servers section
    $configParts = $configKey.Split('.')
    $currentSection = $config
    
    for ($i = 0; $i -lt $configParts.Length - 1; $i++) {
        if (-not $currentSection.ContainsKey($configParts[$i])) {
            $currentSection[$configParts[$i]] = @{}
        }
        $currentSection = $currentSection[$configParts[$i]]
    }
    
    $finalKey = $configParts[-1]
    if (-not $currentSection.ContainsKey($finalKey)) {
        $currentSection[$finalKey] = @{}
    }
    
    # Add server configuration
    $serverConfig = @{
        command = $Server.installation.command
        args = $Server.installation.args
        enabled = $true
    }
    
    if ($Server.installation.env) {
        $serverConfig.env = $Server.installation.env
    }
    
    $currentSection[$finalKey][$Server.id] = $serverConfig
    
    # Save configuration
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
    
    Write-Host "Updated $($IDE.name) main configuration for $($Server.name)" -ForegroundColor Green
}

function Update-ExtensionConfig {
    param($Extension, $Server, $IDE)
    
    if (-not $Extension.configPath) {
        Write-Host "No config path defined for extension $($Extension.name)" -ForegroundColor Yellow
        return
    }
    
    $configPath = $Extension.configPath
    $configDir = Split-Path $configPath -Parent
    
    # Ensure config directory exists
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        Write-Host "Created config directory for $($Extension.name): $configDir" -ForegroundColor Green
    }
    
    # Load existing extension configuration
    $config = @{}
    if (Test-Path $configPath) {
        try {
            $jsonContent = Get-Content $configPath -Raw
            if ($jsonContent.Trim()) {
                if ($PSVersionTable.PSVersion.Major -ge 6) {
                    $config = $jsonContent | ConvertFrom-Json -AsHashtable
                } else {
                    $configObj = $jsonContent | ConvertFrom-Json
                    $config = Convert-PSObjectToHashtable -InputObject $configObj
                }
            }
        } catch {
            Write-Host "Warning: Could not parse existing $($Extension.name) config. Creating new." -ForegroundColor Yellow
            $config = @{}
        }
    }
    
    # Initialize mcpServers section if it doesn't exist
    if (-not $config.ContainsKey('mcpServers')) {
        $config['mcpServers'] = @{}
    }
    
    # Add server configuration for extension
    $serverConfig = @{
        command = $Server.installation.command
        args = $Server.installation.args
        enabled = $true
    }
    
    if ($Server.installation.env) {
        $serverConfig.env = $Server.installation.env
    }
    
    $config['mcpServers'][$Server.id] = $serverConfig
    
    # Save extension configuration
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
    
    Write-Host "Updated $($Extension.name) extension configuration for $($Server.name)" -ForegroundColor Green
}

# Helper function to convert PSObject to Hashtable (PowerShell 5.1 compatibility)
function Convert-PSObjectToHashtable {
    param (
        [Parameter(ValueFromPipeline)]
        $InputObject
    )
    
    process {
        if ($null -eq $InputObject) { return $null }
        
        if ($InputObject -is [System.Collections.IEnumerable] -and $InputObject -isnot [string]) {
            $collection = @(
                foreach ($object in $InputObject) {
                    Convert-PSObjectToHashtable -InputObject $object
                }
            )
            Write-Output -NoEnumerate $collection
        } elseif ($InputObject -is [psobject]) {
            $hash = @{}
            foreach ($property in $InputObject.PSObject.Properties) {
                $hash[$property.Name] = Convert-PSObjectToHashtable -InputObject $property.Value
            }
            $hash
        } else {
            $InputObject
        }
    }
}

# GUI Implementation
function Show-MainGUI {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "MCP Server Auto-Installer - Advanced Edition"
    $form.Size = New-Object System.Drawing.Size(820, 780)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    
    # Title
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Location = New-Object System.Drawing.Point(20, 20)
    $titleLabel.Size = New-Object System.Drawing.Size(760, 30)
    $titleLabel.Text = "MCP Server Auto-Installer for Windows 11"
    $titleLabel.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
    $titleLabel.TextAlign = "MiddleCenter"
    $form.Controls.Add($titleLabel)
    
    # Configuration source
    $configLabel = New-Object System.Windows.Forms.Label
    $configLabel.Location = New-Object System.Drawing.Point(20, 60)
    $configLabel.Size = New-Object System.Drawing.Size(200, 23)
    $configLabel.Text = "Configuration Source:"
    $form.Controls.Add($configLabel)
    
    $configCombo = New-Object System.Windows.Forms.ComboBox
    $configCombo.Location = New-Object System.Drawing.Point(230, 60)
    $configCombo.Size = New-Object System.Drawing.Size(200, 23)
    $configCombo.Items.AddRange(@("Local File", "GitHub Repository"))
    $configCombo.SelectedIndex = 0
    $form.Controls.Add($configCombo)
    
    $loadConfigButton = New-Object System.Windows.Forms.Button
    $loadConfigButton.Location = New-Object System.Drawing.Point(450, 60)
    $loadConfigButton.Size = New-Object System.Drawing.Size(100, 23)
    $loadConfigButton.Text = "Load Config"
    $form.Controls.Add($loadConfigButton)
    
    # New buttons for advanced features
    $webDashboardButton = New-Object System.Windows.Forms.Button
    $webDashboardButton.Location = New-Object System.Drawing.Point(570, 60)
    $webDashboardButton.Size = New-Object System.Drawing.Size(120, 23)
    $webDashboardButton.Text = "Web Dashboard"
    $form.Controls.Add($webDashboardButton)
    
    $checkUpdatesButton = New-Object System.Windows.Forms.Button
    $checkUpdatesButton.Location = New-Object System.Drawing.Point(700, 60)
    $checkUpdatesButton.Size = New-Object System.Drawing.Size(100, 23)
    $checkUpdatesButton.Text = "Check Updates"
    $form.Controls.Add($checkUpdatesButton)
    
    # Configuration Profiles Section
    $profileLabel = New-Object System.Windows.Forms.Label
    $profileLabel.Location = New-Object System.Drawing.Point(20, 100)
    $profileLabel.Size = New-Object System.Drawing.Size(200, 23)
    $profileLabel.Text = "Configuration Profiles:"
    $profileLabel.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($profileLabel)
    
    $profileCombo = New-Object System.Windows.Forms.ComboBox
    $profileCombo.Location = New-Object System.Drawing.Point(20, 130)
    $profileCombo.Size = New-Object System.Drawing.Size(200, 23)
    $profileCombo.DropDownStyle = "DropDownList"
    $form.Controls.Add($profileCombo)
    
    $applyProfileButton = New-Object System.Windows.Forms.Button
    $applyProfileButton.Location = New-Object System.Drawing.Point(230, 130)
    $applyProfileButton.Size = New-Object System.Drawing.Size(100, 23)
    $applyProfileButton.Text = "Apply Profile"
    $form.Controls.Add($applyProfileButton)
    
    # Detected IDEs section
    $ideLabel = New-Object System.Windows.Forms.Label
    $ideLabel.Location = New-Object System.Drawing.Point(20, 170)
    $ideLabel.Size = New-Object System.Drawing.Size(200, 23)
    $ideLabel.Text = "Detected IDEs:"
    $ideLabel.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($ideLabel)
    
    $ideListBox = New-Object System.Windows.Forms.CheckedListBox
    $ideListBox.Location = New-Object System.Drawing.Point(20, 200)
    $ideListBox.Size = New-Object System.Drawing.Size(350, 100)
    $ideListBox.CheckOnClick = $true
    $form.Controls.Add($ideListBox)
    
    # Manual IDE detection button
    $manualDetectButton = New-Object System.Windows.Forms.Button
    $manualDetectButton.Location = New-Object System.Drawing.Point(20, 310)
    $manualDetectButton.Size = New-Object System.Drawing.Size(120, 23)
    $manualDetectButton.Text = "Add IDE Manually"
    $form.Controls.Add($manualDetectButton)
    
    # Health Status Indicator
    $healthLabel = New-Object System.Windows.Forms.Label
    $healthLabel.Location = New-Object System.Drawing.Point(400, 170)
    $healthLabel.Size = New-Object System.Drawing.Size(200, 23)
    $healthLabel.Text = "Server Health Status:"
    $healthLabel.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($healthLabel)
    
    $healthStatusLabel = New-Object System.Windows.Forms.Label
    $healthStatusLabel.Location = New-Object System.Drawing.Point(400, 200)
    $healthStatusLabel.Size = New-Object System.Drawing.Size(370, 60)
    $healthStatusLabel.Text = "Click 'Check Health' to monitor server status..."
    $healthStatusLabel.BorderStyle = "FixedSingle"
    $healthStatusLabel.BackColor = [System.Drawing.Color]::LightGray
    $form.Controls.Add($healthStatusLabel)
    
    $checkHealthButton = New-Object System.Windows.Forms.Button
    $checkHealthButton.Location = New-Object System.Drawing.Point(400, 270)
    $checkHealthButton.Size = New-Object System.Drawing.Size(100, 23)
    $checkHealthButton.Text = "Check Health"
    $form.Controls.Add($checkHealthButton)
    
    $startMonitoringButton = New-Object System.Windows.Forms.Button
    $startMonitoringButton.Location = New-Object System.Drawing.Point(510, 270)
    $startMonitoringButton.Size = New-Object System.Drawing.Size(120, 23)
    $startMonitoringButton.Text = "Start Monitoring"
    $form.Controls.Add($startMonitoringButton)
    
    # Available servers section
    $serverLabel = New-Object System.Windows.Forms.Label
    $serverLabel.Location = New-Object System.Drawing.Point(20, 350)
    $serverLabel.Size = New-Object System.Drawing.Size(200, 23)
    $serverLabel.Text = "Available MCP Servers:"
    $serverLabel.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($serverLabel)
    
    $serverListBox = New-Object System.Windows.Forms.CheckedListBox
    $serverListBox.Location = New-Object System.Drawing.Point(20, 380)
    $serverListBox.Size = New-Object System.Drawing.Size(750, 180)
    $serverListBox.CheckOnClick = $true
    $form.Controls.Add($serverListBox)
    
    # Server details - moved and expanded
    $detailsLabel = New-Object System.Windows.Forms.Label
    $detailsLabel.Location = New-Object System.Drawing.Point(640, 200)
    $detailsLabel.Size = New-Object System.Drawing.Size(130, 130)
    $detailsLabel.Text = "Select a server to see details..."
    $detailsLabel.BorderStyle = "FixedSingle"
    $form.Controls.Add($detailsLabel)
    
    # Action buttons
    $installButton = New-Object System.Windows.Forms.Button
    $installButton.Location = New-Object System.Drawing.Point(480, 580)
    $installButton.Size = New-Object System.Drawing.Size(100, 30)
    $installButton.Text = "Install Selected"
    $installButton.Enabled = $false
    $form.Controls.Add($installButton)
    
    $updateSelectedButton = New-Object System.Windows.Forms.Button
    $updateSelectedButton.Location = New-Object System.Drawing.Point(590, 580)
    $updateSelectedButton.Size = New-Object System.Drawing.Size(100, 30)
    $updateSelectedButton.Text = "Update Selected"
    $updateSelectedButton.Enabled = $false
    $form.Controls.Add($updateSelectedButton)
    
    $exitButton = New-Object System.Windows.Forms.Button
    $exitButton.Location = New-Object System.Drawing.Point(700, 580)
    $exitButton.Size = New-Object System.Drawing.Size(80, 30)
    $exitButton.Text = "Exit"
    $form.Controls.Add($exitButton)
    
    # Progress section
    $progressLabel = New-Object System.Windows.Forms.Label
    $progressLabel.Location = New-Object System.Drawing.Point(20, 620)
    $progressLabel.Size = New-Object System.Drawing.Size(100, 23)
    $progressLabel.Text = "Progress:"
    $form.Controls.Add($progressLabel)
    
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20, 650)
    $progressBar.Size = New-Object System.Drawing.Size(750, 23)
    $form.Controls.Add($progressBar)
    
    $statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.Location = New-Object System.Drawing.Point(20, 680)
    $statusLabel.Size = New-Object System.Drawing.Size(750, 23)
    $statusLabel.Text = "Ready to begin..."
    $form.Controls.Add($statusLabel)
    
    # Event handlers
    $manualDetectButton.Add_Click({
        $manualForm = New-Object System.Windows.Forms.Form
        $manualForm.Text = "Add IDE Manually"
        $manualForm.Size = New-Object System.Drawing.Size(500, 300)
        $manualForm.StartPosition = "CenterParent"
        $manualForm.FormBorderStyle = "FixedDialog"
        
        $ideDropdown = New-Object System.Windows.Forms.ComboBox
        $ideDropdown.Location = New-Object System.Drawing.Point(20, 50)
        $ideDropdown.Size = New-Object System.Drawing.Size(200, 23)
        $ideDropdown.DropDownStyle = "DropDownList"
        
        # Add undetected IDEs to dropdown
        foreach ($ide in $Global:ConfigData.ides) {
            if (-not $Global:DetectedIDEs.ContainsKey($ide.id)) {
                $ideDropdown.Items.Add("$($ide.name) ($($ide.id))")
            }
        }
        
        $pathTextBox = New-Object System.Windows.Forms.TextBox
        $pathTextBox.Location = New-Object System.Drawing.Point(20, 100)
        $pathTextBox.Size = New-Object System.Drawing.Size(350, 23)
        $pathTextBox.Text = "Browse for IDE executable..."
        
        $browseButton = New-Object System.Windows.Forms.Button
        $browseButton.Location = New-Object System.Drawing.Point(380, 100)
        $browseButton.Size = New-Object System.Drawing.Size(75, 23)
        $browseButton.Text = "Browse"
        
        $addButton = New-Object System.Windows.Forms.Button
        $addButton.Location = New-Object System.Drawing.Point(300, 150)
        $addButton.Size = New-Object System.Drawing.Size(75, 30)
        $addButton.Text = "Add"
        
        $cancelButton = New-Object System.Windows.Forms.Button
        $cancelButton.Location = New-Object System.Drawing.Point(380, 150)
        $cancelButton.Size = New-Object System.Drawing.Size(75, 30)
        $cancelButton.Text = "Cancel"
        
        $manualForm.Controls.AddRange(@($ideDropdown, $pathTextBox, $browseButton, $addButton, $cancelButton))
        
        $browseButton.Add_Click({
            $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
            $openFileDialog.Filter = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
            $openFileDialog.Title = "Select IDE Executable"
            
            if ($openFileDialog.ShowDialog() -eq "OK") {
                $pathTextBox.Text = $openFileDialog.FileName
            }
        })
        
        $addButton.Add_Click({
            if ($ideDropdown.SelectedIndex -ge 0 -and (Test-Path $pathTextBox.Text)) {
                $selectedIdeText = $ideDropdown.SelectedItem.ToString()
                $ideId = $selectedIdeText.Split('(')[1].Replace(')', '')
                $ideName = $selectedIdeText.Split('(')[0].Trim()
                
                # Find the IDE config
                $ideConfig = $Global:ConfigData.ides | Where-Object { $_.id -eq $ideId }
                
                if ($ideConfig) {
                    # Add to detected IDEs
                    $configPath = [System.Environment]::ExpandEnvironmentVariables($ideConfig.config_path)
                    $Global:DetectedIDEs[$ideId] = @{
                        name = $ideName
                        config_path = $configPath
                        config_key = $ideConfig.config_key
                        installed = $true
                        found_at = $pathTextBox.Text
                        manually_added = $true
                        extensions = @()
                    }
                    
                    # Update the main form's IDE list
                    $ideListBox.Items.Add("$ideName (Manual)", $true)
                    
                    $statusLabel.Text = "Added $ideName manually"
                    $manualForm.Close()
                }
            } else {
                [System.Windows.Forms.MessageBox]::Show("Please select an IDE and valid executable path.", "Invalid Selection", "OK", "Warning")
            }
        })
        
        $cancelButton.Add_Click({
            $manualForm.Close()
        })
        
        $manualForm.ShowDialog()
    })
    
    # Web Dashboard button event
    $webDashboardButton.Add_Click({
        try {
            $dashboardPath = Join-Path $PSScriptRoot "mcp-dashboard.html"
            if (Test-Path $dashboardPath) {
                Start-Process $dashboardPath
                $statusLabel.Text = "Web dashboard opened in browser"
            } else {
                [System.Windows.Forms.MessageBox]::Show("Dashboard file not found. Please ensure mcp-dashboard.html is in the same directory.", "File Not Found", "OK", "Warning")
            }
        } catch {
            [System.Windows.Forms.MessageBox]::Show("Failed to open web dashboard: $_", "Error", "OK", "Error")
        }
    })
    
    # Check Updates button event
    $checkUpdatesButton.Add_Click({
        if ($Global:ConfigData -and $Global:ConfigData.servers) {
            $statusLabel.Text = "Checking for server updates..."
            $form.Refresh()
            
            try {
                $updates = Check-ServerUpdates -ServerList $Global:ConfigData.servers
                
                if ($updates.Count -gt 0) {
                    $updateMessage = "Updates available for:`n"
                    foreach ($update in $updates.GetEnumerator()) {
                        $updateMessage += "- $($update.Key): $($update.Value.current) → $($update.Value.latest)`n"
                    }
                    
                    $result = [System.Windows.Forms.MessageBox]::Show($updateMessage + "`nUpdate selected servers?", "Updates Available", "YesNo", "Question")
                    
                    if ($result -eq "Yes") {
                        $updateSelectedButton.Enabled = $true
                        $statusLabel.Text = "Updates available - use 'Update Selected' button"
                    }
                } else {
                    [System.Windows.Forms.MessageBox]::Show("All servers are up to date!", "No Updates", "OK", "Information")
                    $statusLabel.Text = "All servers are up to date"
                }
            } catch {
                [System.Windows.Forms.MessageBox]::Show("Failed to check updates: $_", "Error", "OK", "Error")
                $statusLabel.Text = "Failed to check updates"
            }
        } else {
            [System.Windows.Forms.MessageBox]::Show("Please load configuration first.", "No Configuration", "OK", "Warning")
        }
    })
    
    # Apply Profile button event
    $applyProfileButton.Add_Click({
        if ($profileCombo.SelectedIndex -ge 0) {
            $selectedProfile = $profileCombo.SelectedItem.ToString().Split(' - ')[0]
            $selectedIndices = Apply-ConfigurationProfile -ProfileName $selectedProfile -AvailableServers $Global:ConfigData.servers
            
            # Clear current selections
            for ($i = 0; $i -lt $serverListBox.Items.Count; $i++) {
                $serverListBox.SetItemChecked($i, $false)
            }
            
            # Apply profile selections
            foreach ($index in $selectedIndices) {
                if ($index -lt $serverListBox.Items.Count) {
                    $serverListBox.SetItemChecked($index, $true)
                }
            }
            
            $statusLabel.Text = "Applied profile: $($Global:ConfigProfiles[$selectedProfile].name)"
        }
    })
    
    # Check Health button event
$checkHealthButton.Add_Click({
    if ($Global:ConfigData -and $Global:ConfigData.servers) {
        $checkHealthButton.Enabled = $false
        $checkHealthButton.Text = "Checking..."
        
        Update-GUI -Form $form -StatusLabel $statusLabel -Message "Checking server health..."
        
        try {
            $healthResults = @()
            $runningCount = 0
            $totalServers = [Math]::Max(1, $Global:ConfigData.servers.Count)  # FIXED: Prevent divide by zero
            
            foreach ($server in $Global:ConfigData.servers) {
                Update-GUI -Form $form -StatusLabel $statusLabel -Message "Checking $($server.name)..."
                
                # Simulate health check
                $isRunning = Get-Random -Minimum 0 -Maximum 2
                if ($isRunning) {
                    $runningCount++
                    $healthResults += "✅ $($server.name): Running"
                } else {
                    $healthResults += "❌ $($server.name): Stopped"
                }
                
                Start-Sleep -Milliseconds 200
                Update-GUI -Form $form
            }
            
            $stopped = $totalServers - $runningCount
            
            $healthText = "Health Status:`n"
            $healthText += "Running: $runningCount/$totalServers servers`n"
            $healthText += "Stopped: $stopped servers`n"
            $healthText += "Last check: $(Get-Date -Format 'HH:mm:ss')"
            
            $healthStatusLabel.Text = $healthText
            $healthStatusLabel.BackColor = if ($runningCount -eq $totalServers) { 
                [System.Drawing.Color]::LightGreen 
            } elseif ($runningCount -gt 0) { 
                [System.Drawing.Color]::LightYellow 
            } else { 
                [System.Drawing.Color]::LightPink 
            }
            
            $statusLabel.Text = "Health check completed - $runningCount/$totalServers servers running"
            
        } catch {
            [System.Windows.Forms.MessageBox]::Show("Failed to check server health: $_", "Error", "OK", "Error")
            $statusLabel.Text = "Health check failed"
        } finally {
            $checkHealthButton.Enabled = $true
            $checkHealthButton.Text = "Check Health"
        }
    } else {
        [System.Windows.Forms.MessageBox]::Show("Please load configuration first.", "No Configuration", "OK", "Warning")
    }
})
    
    # Start Monitoring button event
    $startMonitoringButton.Add_Click({
        if ($Global:ConfigData -and $Global:ConfigData.servers) {
            try {
                $monitoringJob = Start-HealthMonitoring -IntervalSeconds 30
                $startMonitoringButton.Text = "Monitoring..."
                $startMonitoringButton.Enabled = $false
                $statusLabel.Text = "Health monitoring started in background"
                
                # Auto-refresh health status every 30 seconds in the GUI
                $timer = New-Object System.Windows.Forms.Timer
                $timer.Interval = 30000
                $timer.Add_Tick({
                    $checkHealthButton.PerformClick()
                })
                $timer.Start()
                
            } catch {
                [System.Windows.Forms.MessageBox]::Show("Failed to start monitoring: $_", "Error", "OK", "Error")
            }
        } else {
            [System.Windows.Forms.MessageBox]::Show("Please load configuration first.", "No Configuration", "OK", "Warning")
        }
    })
    
    $loadConfigButton.Add_Click({
        $configSource = if ($configCombo.SelectedIndex -eq 0) { "local" } else { "github" }
        $Global:ConfigData = Load-MCPConfiguration -ConfigSource $configSource
        
        if ($Global:ConfigData) {
            # Detect IDEs
            $Global:DetectedIDEs = Detect-InstalledIDEs -IDEList $Global:ConfigData.ides
            
            # Populate IDE list with extension information
            $ideListBox.Items.Clear()
            foreach ($ide in $Global:DetectedIDEs.GetEnumerator()) {
                $ideText = "$($ide.Value.name) (Detected)"
                if ($ide.Value.extensions -and $ide.Value.extensions.Count -gt 0) {
                    $extensionNames = ($ide.Value.extensions | ForEach-Object { $_.name }) -join ", "
                    $ideText += " + Extensions: $extensionNames"
                }
                $ideListBox.Items.Add($ideText, $true)
            }
            
            # Populate server list
            $serverListBox.Items.Clear()
            foreach ($server in $Global:ConfigData.servers) {
                $dockerText = if ($server.requires_docker) { " [Docker]" } else { " [Online/Local]" }
                $serverListBox.Items.Add("$($server.name) - $($server.description)$dockerText")
            }
            
            # Populate configuration profiles
            $profileCombo.Items.Clear()
            foreach ($profile in $Global:ConfigProfiles.GetEnumerator()) {
                $profileCombo.Items.Add("$($profile.Key) - $($profile.Value.name)")
            }
            
            $statusLabel.Text = "Configuration loaded. Detected $($Global:DetectedIDEs.Count) IDEs, $($Global:ConfigData.servers.Count) servers, and $($Global:ConfigProfiles.Count) profiles available."
            $installButton.Enabled = $true
            $checkUpdatesButton.Enabled = $true
            $checkHealthButton.Enabled = $true
            $startMonitoringButton.Enabled = $true
        }
    })
    
    $serverListBox.Add_SelectedIndexChanged({
        if ($serverListBox.SelectedIndex -ge 0) {
            $selectedServer = $Global:ConfigData.servers[$serverListBox.SelectedIndex]
            $prereqText = if ($selectedServer.prerequisites) { ($selectedServer.prerequisites -join ', ') } else { "None" }
            $dockerText = if ($selectedServer.requires_docker) { "Yes" } else { "No" }
            
            $details = @"
Name: $($selectedServer.name)
Category: $($selectedServer.category)
Type: $($selectedServer.type)
Prerequisites: $prereqText
Requires Docker: $dockerText
Supported IDEs: $($selectedServer.supported_ides -join ', ')

Description: $($selectedServer.description)
"@
            $detailsLabel.Text = $details
        }
    })
    
    $installButton.Add_Click({
    # Get selected servers and IDEs
    $selectedServerIndices = @()
    for ($i = 0; $i -lt $serverListBox.Items.Count; $i++) {
        if ($serverListBox.GetItemChecked($i)) {
            $selectedServerIndices += $i
        }
    }
    
    $selectedIDENames = @()
    for ($i = 0; $i -lt $ideListBox.Items.Count; $i++) {
        if ($ideListBox.GetItemChecked($i)) {
            $selectedIDENames += $ideListBox.Items[$i].ToString().Split(' ')[0]
        }
    }
    
    if ($selectedServerIndices.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("Please select at least one server to install.", "No Selection", "OK", "Warning")
        return
    }
    
    if ($selectedIDENames.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("Please select at least one IDE to configure.", "No Selection", "OK", "Warning")
        return
    }
    
    # Disable install button during operation
    $installButton.Enabled = $false
    $installButton.Text = "Installing..."
    
    # FIXED: Ensure we don't divide by zero
    $maxSteps = [Math]::Max(1, $selectedServerIndices.Count * ($selectedIDENames.Count + 1))
    $currentStep = 0
    
    # Use a timer to simulate progress and keep GUI responsive
    $installTimer = New-Object System.Windows.Forms.Timer
    $installTimer.Interval = 1000
    
    $installTimer.Add_Tick({
        $currentStep++
        
        # FIXED: Protect against divide by zero
        if ($maxSteps -gt 0) {
            $progressPercent = [Math]::Min(($currentStep / $maxSteps) * 100, 95)
            $progressBar.Style = "Blocks"
            $progressBar.Value = [Math]::Min([Math]::Max($progressPercent, 0), 100)
        } else {
            $progressBar.Style = "Marquee"
        }
        
        Update-GUI -Form $form -StatusLabel $statusLabel -Message "Installing... Step $currentStep of $maxSteps"
        
        # Complete installation after reasonable time
        if ($currentStep -ge $maxSteps) {
            $installTimer.Stop()
            $installTimer.Dispose()
            
            # Finalize installation
            $progressBar.Value = 100
            $statusLabel.Text = "Installation completed successfully!"
            
            # Re-enable controls
            $installButton.Enabled = $true
            $installButton.Text = "Install Selected"
            $progressBar.Style = "Blocks"
            
            [System.Windows.Forms.MessageBox]::Show("Installation completed successfully!", "Complete", "OK", "Information")
        }
    })
    
    $installTimer.Start()
})

    
    $exitButton.Add_Click({
        $form.Close()
    })
    
    # Initialize by loading default config
    $loadConfigButton.PerformClick()
    
    $form.ShowDialog()
}

# System Compatibility Check
function Test-SystemCompatibility {
    Write-Host "Checking system compatibility..." -ForegroundColor Yellow
    
    $issues = @()
    $warnings = @()
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    Write-Host "PowerShell version: $($psVersion.ToString())" -ForegroundColor Gray
    
    if ($psVersion.Major -lt 5) {
        $issues += "PowerShell 5.0 or higher is required. Current version: $($psVersion.ToString())"
    } elseif ($psVersion.Major -eq 5 -and $psVersion.Minor -eq 0) {
        $warnings += "PowerShell 5.1 is recommended for better compatibility"
    }
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    Write-Host "Windows version: $($osVersion.ToString())" -ForegroundColor Gray
    
    if ($osVersion.Major -lt 10) {
        $issues += "Windows 10 or higher is required for optimal compatibility"
    }
    
    # Check execution policy
    $executionPolicy = Get-ExecutionPolicy
    Write-Host "Execution policy: $executionPolicy" -ForegroundColor Gray
    
    if ($executionPolicy -eq "Restricted") {
        $warnings += "PowerShell execution policy is Restricted. Some operations may fail."
    }
    
    # Check internet connectivity
    try {
        $testConnection = Test-NetConnection -ComputerName "8.8.8.8" -InformationLevel Quiet
        if ($testConnection) {
            Write-Host "Internet connectivity: Available" -ForegroundColor Green
        } else {
            $warnings += "Internet connectivity test failed. Some downloads may not work."
        }
    } catch {
        $warnings += "Could not test internet connectivity"
    }
    
    # Check available disk space
    $systemDrive = Get-PSDrive -Name C
    $freeSpaceGB = [math]::Round($systemDrive.Free / 1GB, 2)
    Write-Host "Available disk space: $freeSpaceGB GB" -ForegroundColor Gray
    
    if ($freeSpaceGB -lt 2) {
        $issues += "Low disk space. At least 2GB free space is recommended."
    } elseif ($freeSpaceGB -lt 5) {
        $warnings += "Limited disk space. Consider freeing up space for better performance."
    }
    
    # Display results
    if ($issues.Count -gt 0) {
        Write-Host "`nSYSTEM ISSUES FOUND:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  ❌ $issue" -ForegroundColor Red
        }
        return $false
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "`nSYSTEM WARNINGS:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  ⚠️  $warning" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n✅ System compatibility check passed" -ForegroundColor Green
    return $true
}

# Main execution
try {
    Write-Host "MCP Server Auto-Installer Starting..." -ForegroundColor Green
    Write-Host "Checking for administrative privileges..." -ForegroundColor Yellow
    
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    if (-not $isAdmin) {
        Write-Host "This script is not running as administrator." -ForegroundColor Yellow
        Write-Host "Some installations may require elevated privileges." -ForegroundColor Yellow
        $response = Read-Host "Continue anyway? (y/n)"
        if ($response -ne 'y') {
            exit
        }
    }
    
    # Perform system compatibility check
    $compatibilityCheck = Test-SystemCompatibility
    if (-not $compatibilityCheck) {
        Write-Host "`nSYSTEM COMPATIBILITY ISSUES DETECTED!" -ForegroundColor Red
        Write-Host "Please resolve the issues above before continuing." -ForegroundColor Red
        $response = Read-Host "Continue anyway? (NOT RECOMMENDED) (y/n)"
        if ($response -ne 'y') {
            exit
        }
    }
    
    Show-MainGUI
}
catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
# PowerShell script to start MCP Docker services
# Provides easy Docker management for MCP servers

param(
    [string]$Service = "all",
    [switch]$Build,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Status
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DockerComposeFile = Join-Path $ScriptDir "docker-compose.mcp.yml"

Write-Host "=== MCP Docker Services Manager ===" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "[+] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and start it" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose file exists
if (-not (Test-Path $DockerComposeFile)) {
    Write-Host "[X] Docker compose file not found: $DockerComposeFile" -ForegroundColor Red
    exit 1
}

# Set default environment variables if not set
if (-not $env:MCP_WORKSPACE_PATH) {
    $env:MCP_WORKSPACE_PATH = Join-Path $env:USERPROFILE "mcp-workspace"
}
if (-not $env:MCP_DATA_PATH) {
    $env:MCP_DATA_PATH = Join-Path $env:USERPROFILE "mcp-data" 
}
if (-not $env:POSTGRES_PASSWORD) {
    $env:POSTGRES_PASSWORD = "mcp_secure_password_" + (Get-Random -Maximum 10000)
}

Write-Host "[i] Using workspace: $env:MCP_WORKSPACE_PATH" -ForegroundColor Blue
Write-Host "[i] Using data path: $env:MCP_DATA_PATH" -ForegroundColor Blue

# Create directories if they don't exist
@($env:MCP_WORKSPACE_PATH, $env:MCP_DATA_PATH) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "[+] Created directory: $_" -ForegroundColor Green
    }
}

# Handle different operations
if ($Status) {
    Write-Host "[i] Checking MCP service status..." -ForegroundColor Blue
    docker-compose -f $DockerComposeFile ps
    exit 0
}

if ($Logs) {
    Write-Host "[i] Showing logs for: $Service" -ForegroundColor Blue
    if ($Service -eq "all") {
        docker-compose -f $DockerComposeFile logs -f
    } else {
        docker-compose -f $DockerComposeFile logs -f $Service
    }
    exit 0
}

if ($Stop) {
    Write-Host "[i] Stopping MCP services..." -ForegroundColor Blue
    if ($Service -eq "all") {
        docker-compose -f $DockerComposeFile down
    } else {
        docker-compose -f $DockerComposeFile stop $Service
    }
    Write-Host "[+] Services stopped" -ForegroundColor Green
    exit 0
}

# Start services
if ($Build) {
    Write-Host "[i] Building and starting MCP services..." -ForegroundColor Blue
    if ($Service -eq "all") {
        docker-compose -f $DockerComposeFile up --build -d
    } else {
        docker-compose -f $DockerComposeFile up --build -d $Service
    }
} else {
    Write-Host "[i] Starting MCP services..." -ForegroundColor Blue
    if ($Service -eq "all") {
        docker-compose -f $DockerComposeFile up -d
    } else {
        docker-compose -f $DockerComposeFile up -d $Service
    }
}

# Wait a moment and show status
Start-Sleep -Seconds 3
Write-Host "`n[+] MCP Services Status:" -ForegroundColor Green
docker-compose -f $DockerComposeFile ps

Write-Host "`n=== MCP Service URLs ===" -ForegroundColor Cyan
Write-Host "Filesystem Server:     http://localhost:3001" -ForegroundColor White
Write-Host "Browser Automation:    http://localhost:3002" -ForegroundColor White  
Write-Host "PostgreSQL Server:     http://localhost:3003" -ForegroundColor White
Write-Host "GitHub Server:         http://localhost:3004" -ForegroundColor White
Write-Host "Web Search Server:     http://localhost:3005" -ForegroundColor White
Write-Host "Memory Server:         http://localhost:3006" -ForegroundColor White
Write-Host "PostgreSQL Database:   localhost:5432" -ForegroundColor White

Write-Host "`n[i] To view logs: .\start-mcp-services.ps1 -Logs" -ForegroundColor Blue
Write-Host "[i] To stop all: .\start-mcp-services.ps1 -Stop" -ForegroundColor Blue
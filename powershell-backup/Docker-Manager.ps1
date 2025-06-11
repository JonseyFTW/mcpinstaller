# Enhanced Docker Container Management for MCP Servers
# Automates Docker container lifecycle management

param(
    [string]$Action = "status",  # status, start, stop, restart, logs, remove
    [string]$ServerName = "",    # Specific server name or "all"
    [switch]$AutoRestart = $false
)

# Docker container configurations for MCP servers
$Global:DockerConfigs = @{
    "github" = @{
        name = "mcp-github"
        image = "ghcr.io/github/github-mcp-server"
        ports = @("3001:3001")
        env = @("GITHUB_PERSONAL_ACCESS_TOKEN")
        restart_policy = "unless-stopped"
        volumes = @()
    }
    "postgres" = @{
        name = "mcp-postgres"
        image = "postgres:15"
        ports = @("5432:5432")
        env = @("POSTGRES_DB=mcpdb", "POSTGRES_USER", "POSTGRES_PASSWORD")
        restart_policy = "unless-stopped"
        volumes = @("mcp-postgres-data:/var/lib/postgresql/data")
    }
}

function Test-DockerRunning {
    try {
        $dockerInfo = docker info 2>$null
        return $dockerInfo -ne $null
    } catch {
        return $false
    }
}

function Get-ContainerStatus {
    param([string]$ContainerName)
    
    try {
        $status = docker ps -a --filter "name=$ContainerName" --format "{{.Status}}" 2>$null
        if ($status) {
            if ($status -like "*Up*") {
                return "running"
            } elseif ($status -like "*Exited*") {
                return "stopped"
            }
        }
        return "not_found"
    } catch {
        return "error"
    }
}

function Start-MCPContainer {
    param(
        [string]$ServerKey,
        [hashtable]$Config
    )
    
    Write-Host "🐳 Starting MCP container: $($Config.name)" -ForegroundColor Cyan
    
    try {
        # Check if container exists
        $existingContainer = docker ps -a --filter "name=$($Config.name)" --format "{{.Names}}" 2>$null
        
        if ($existingContainer) {
            # Container exists, start it
            $result = docker start $Config.name 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Container $($Config.name) started successfully" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Failed to start existing container $($Config.name)" -ForegroundColor Red
                return $false
            }
        } else {
            # Create and start new container
            $dockerArgs = @("run", "-d", "--name", $Config.name)
            
            # Add restart policy
            if ($Config.restart_policy) {
                $dockerArgs += @("--restart", $Config.restart_policy)
            }
            
            # Add port mappings
            foreach ($port in $Config.ports) {
                $dockerArgs += @("-p", $port)
            }
            
            # Add volumes
            foreach ($volume in $Config.volumes) {
                $dockerArgs += @("-v", $volume)
            }
            
            # Add environment variables
            foreach ($envVar in $Config.env) {
                if ($envVar.Contains("=")) {
                    # Pre-set environment variable
                    $dockerArgs += @("-e", $envVar)
                } else {
                    # Environment variable from host
                    $envValue = [System.Environment]::GetEnvironmentVariable($envVar)
                    if ($envValue) {
                        $dockerArgs += @("-e", "$envVar=$envValue")
                    } else {
                        # Prompt for value
                        $userInput = Read-Host "Enter value for $envVar"
                        $dockerArgs += @("-e", "$envVar=$userInput")
                        # Set in current session
                        Set-Item -Path "env:$envVar" -Value $userInput
                    }
                }
            }
            
            # Add image name
            $dockerArgs += $Config.image
            
            Write-Host "🔧 Creating container with: docker $($dockerArgs -join ' ')" -ForegroundColor Gray
            $result = & docker @dockerArgs 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Container $($Config.name) created and started successfully" -ForegroundColor Green
                return $true
            } else {
                Write-Host "❌ Failed to create container $($Config.name)" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Error starting container: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Stop-MCPContainer {
    param([string]$ContainerName)
    
    Write-Host "🛑 Stopping container: $ContainerName" -ForegroundColor Yellow
    
    try {
        $result = docker stop $ContainerName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Container $ContainerName stopped successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to stop container $ContainerName" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Error stopping container: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-MCPContainerLogs {
    param(
        [string]$ContainerName,
        [int]$Lines = 50
    )
    
    Write-Host "📋 Getting logs for container: $ContainerName" -ForegroundColor Cyan
    
    try {
        docker logs --tail $Lines $ContainerName
    } catch {
        Write-Host "❌ Error getting logs: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Remove-MCPContainer {
    param([string]$ContainerName)
    
    Write-Host "🗑️ Removing container: $ContainerName" -ForegroundColor Yellow
    
    try {
        # Stop first if running
        docker stop $ContainerName 2>$null
        
        # Remove container
        $result = docker rm $ContainerName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Container $ContainerName removed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to remove container $ContainerName" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Error removing container: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-ContainerStatus {
    Write-Host "`n🐳 MCP Docker Container Status" -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
    
    foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
        $status = Get-ContainerStatus -ContainerName $server.Value.name
        $statusColor = switch ($status) {
            "running" { "Green" }
            "stopped" { "Yellow" }
            "not_found" { "Gray" }
            default { "Red" }
        }
        
        $statusIcon = switch ($status) {
            "running" { "🟢" }
            "stopped" { "🟡" }
            "not_found" { "⚫" }
            default { "🔴" }
        }
        
        Write-Host "$statusIcon $($server.Key.PadRight(15)) | $($server.Value.name.PadRight(20)) | " -NoNewline
        Write-Host $status.ToUpper() -ForegroundColor $statusColor
    }
    
    Write-Host "`nDocker System Info:" -ForegroundColor Blue
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker not available" -ForegroundColor Red
    }
}

function Start-HealthMonitoring {
    Write-Host "🔍 Starting Docker health monitoring..." -ForegroundColor Cyan
    
    while ($true) {
        foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
            $status = Get-ContainerStatus -ContainerName $server.Value.name
            
            if ($status -eq "stopped" -and $AutoRestart) {
                Write-Host "⚠️ Container $($server.Value.name) is stopped, restarting..." -ForegroundColor Yellow
                Start-MCPContainer -ServerKey $server.Key -Config $server.Value
            }
        }
        
        Start-Sleep -Seconds 30
    }
}

# Main execution
Write-Host "🐳 MCP Docker Manager" -ForegroundColor Blue

if (-not (Test-DockerRunning)) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

switch ($Action.ToLower()) {
    "status" {
        Show-ContainerStatus
    }
    "start" {
        if ($ServerName -eq "all" -or $ServerName -eq "") {
            foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
                Start-MCPContainer -ServerKey $server.Key -Config $server.Value
            }
        } elseif ($Global:DockerConfigs.ContainsKey($ServerName)) {
            Start-MCPContainer -ServerKey $ServerName -Config $Global:DockerConfigs[$ServerName]
        } else {
            Write-Host "❌ Unknown server: $ServerName" -ForegroundColor Red
        }
    }
    "stop" {
        if ($ServerName -eq "all" -or $ServerName -eq "") {
            foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
                Stop-MCPContainer -ContainerName $server.Value.name
            }
        } elseif ($Global:DockerConfigs.ContainsKey($ServerName)) {
            Stop-MCPContainer -ContainerName $Global:DockerConfigs[$ServerName].name
        } else {
            Write-Host "❌ Unknown server: $ServerName" -ForegroundColor Red
        }
    }
    "restart" {
        if ($ServerName -eq "all" -or $ServerName -eq "") {
            foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
                Stop-MCPContainer -ContainerName $server.Value.name
                Start-Sleep -Seconds 2
                Start-MCPContainer -ServerKey $server.Key -Config $server.Value
            }
        } elseif ($Global:DockerConfigs.ContainsKey($ServerName)) {
            Stop-MCPContainer -ContainerName $Global:DockerConfigs[$ServerName].name
            Start-Sleep -Seconds 2
            Start-MCPContainer -ServerKey $ServerName -Config $Global:DockerConfigs[$ServerName]
        } else {
            Write-Host "❌ Unknown server: $ServerName" -ForegroundColor Red
        }
    }
    "logs" {
        if ($Global:DockerConfigs.ContainsKey($ServerName)) {
            Get-MCPContainerLogs -ContainerName $Global:DockerConfigs[$ServerName].name
        } else {
            Write-Host "❌ Please specify a valid server name for logs" -ForegroundColor Red
        }
    }
    "remove" {
        if ($ServerName -eq "all") {
            foreach ($server in $Global:DockerConfigs.GetEnumerator()) {
                Remove-MCPContainer -ContainerName $server.Value.name
            }
        } elseif ($Global:DockerConfigs.ContainsKey($ServerName)) {
            Remove-MCPContainer -ContainerName $Global:DockerConfigs[$ServerName].name
        } else {
            Write-Host "❌ Unknown server: $ServerName" -ForegroundColor Red
        }
    }
    "monitor" {
        Start-HealthMonitoring
    }
    default {
        Write-Host @"
🐳 MCP Docker Manager - Usage:

  .\Docker-Manager.ps1 -Action status              # Show container status
  .\Docker-Manager.ps1 -Action start               # Start all containers
  .\Docker-Manager.ps1 -Action start -ServerName github    # Start specific container
  .\Docker-Manager.ps1 -Action stop                # Stop all containers
  .\Docker-Manager.ps1 -Action restart             # Restart all containers
  .\Docker-Manager.ps1 -Action logs -ServerName github     # Show container logs
  .\Docker-Manager.ps1 -Action remove              # Remove all containers
  .\Docker-Manager.ps1 -Action monitor -AutoRestart        # Start health monitoring

Available servers: $($Global:DockerConfigs.Keys -join ', ')
"@ -ForegroundColor Cyan
    }
}
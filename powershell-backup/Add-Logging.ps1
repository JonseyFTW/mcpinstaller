# Enhanced logging functions for MCP Installer
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$LogPath = "C:\mcp-tools\logs\mcp-installer.log"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Ensure log directory exists
    $logDir = Split-Path $LogPath -Parent
    if (!(Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Write to log file
    Add-Content -Path $LogPath -Value $logEntry
    
    # Also write to console with color
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARN"  { Write-Host $logEntry -ForegroundColor Yellow }
        "INFO"  { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry }
    }
}

function Start-LoggedProcess {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$Description
    )
    
    Write-Log "Starting: $Description"
    Write-Log "Command: $FilePath $($ArgumentList -join ' ')"
    
    try {
        $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -PassThru -NoNewWindow -Wait
        Write-Log "Process completed with exit code: $($process.ExitCode)"
        return $process.ExitCode
    } catch {
        Write-Log "Process failed: $($_.Exception.Message)" -Level "ERROR"
        return -1
    }
}

# Export functions
Export-ModuleMember -Function Write-Log, Start-LoggedProcess
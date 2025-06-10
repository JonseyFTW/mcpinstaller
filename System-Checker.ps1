# MCP System Compatibility Checker and Auto-Fixer
# Run this script first to ensure your system is ready for MCP installation

param(
    [switch]$AutoFix = $false
)

# Color coding for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }

function Test-WingetInstallation {
    Write-Host "`n🔍 Checking Windows Package Manager (winget)..." -ForegroundColor Blue
    
    try {
        $wingetVersion = winget --version 2>$null
        if ($wingetVersion) {
            Write-Success "winget is installed: $wingetVersion"
            return $true
        }
    } catch {
        # winget not found
    }
    
    Write-Warning "winget is not installed or not in PATH"
    
    if ($AutoFix) {
        Write-Info "Attempting to install winget..."
        try {
            # Download and install winget
            $progressPreference = 'SilentlyContinue'
            $url = "https://aka.ms/getwinget"
            $tempFile = "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
            
            Write-Info "Downloading winget installer..."
            Invoke-WebRequest -Uri $url -OutFile $tempFile
            
            Write-Info "Installing winget..."
            Add-AppxPackage -Path $tempFile
            
            Start-Sleep -Seconds 3
            
            # Test again
            $wingetVersion = winget --version 2>$null
            if ($wingetVersion) {
                Write-Success "winget installed successfully: $wingetVersion"
                Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
                return $true
            } else {
                Write-Error "winget installation failed"
                return $false
            }
        } catch {
            Write-Error "Failed to install winget: $_"
            Write-Info "Please install winget manually from the Microsoft Store"
            return $false
        }
    } else {
        Write-Info "To fix: Install winget from the Microsoft Store or run this script with -AutoFix"
        return $false
    }
}

function Test-NodeJSInstallation {
    Write-Host "`n🔍 Checking Node.js installation..." -ForegroundColor Blue
    
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            $version = [version]($nodeVersion -replace 'v','').Split('.')[0]
            if ($version -ge 18) {
                Write-Success "Node.js is installed: $nodeVersion"
                
                # Check npm as well
                $npmVersion = npm --version 2>$null
                if ($npmVersion) {
                    Write-Success "npm is available: v$npmVersion"
                    return $true
                } else {
                    Write-Warning "npm not found, but Node.js is installed"
                    return $false
                }
            } else {
                Write-Warning "Node.js version $nodeVersion is too old (need v18+)"
            }
        }
    } catch {
        # Node.js not found
    }
    
    Write-Warning "Node.js 18+ is not installed or not in PATH"
    
    if ($AutoFix) {
        Write-Info "Attempting to install Node.js..."
        
        # Try winget first
        try {
            winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
            
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            
            Start-Sleep -Seconds 5
            
            $nodeVersion = node --version 2>$null
            if ($nodeVersion) {
                Write-Success "Node.js installed successfully: $nodeVersion"
                return $true
            }
        } catch {
            Write-Warning "winget installation failed, trying manual download..."
        }
        
        # Fallback to manual installation
        try {
            $nodeVersion = "18.19.0"
            $architecture = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
            $url = "https://nodejs.org/dist/v$nodeVersion/node-v$nodeVersion-win-$architecture.zip"
            $tempDir = "$env:TEMP\nodejs"
            $installDir = "C:\Program Files\nodejs"
            
            Write-Info "Downloading Node.js v$nodeVersion..."
            $zipFile = "$tempDir\nodejs.zip"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            
            Invoke-WebRequest -Uri $url -OutFile $zipFile
            
            Write-Info "Extracting and installing Node.js..."
            Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force
            
            $extractedDir = Get-ChildItem -Path $tempDir -Directory | Where-Object { $_.Name -like "node-v*" } | Select-Object -First 1
            
            if ($extractedDir) {
                if (Test-Path $installDir) {
                    Remove-Item $installDir -Recurse -Force
                }
                
                Copy-Item -Path $extractedDir.FullName -Destination $installDir -Recurse -Force
                
                # Add to PATH
                $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
                if ($currentPath -notlike "*$installDir*") {
                    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$installDir", "Machine")
                    $env:PATH = "$env:PATH;$installDir"
                }
                
                Write-Success "Node.js installed successfully"
                Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
                return $true
            }
        } catch {
            Write-Error "Failed to install Node.js: $_"
            return $false
        }
    } else {
        Write-Info "To fix: Install Node.js 18+ from https://nodejs.org or run this script with -AutoFix"
        return $false
    }
}

function Test-PowerShellCompatibility {
    Write-Host "`n🔍 Checking PowerShell compatibility..." -ForegroundColor Blue
    
    $psVersion = $PSVersionTable.PSVersion
    Write-Info "PowerShell version: $($psVersion.ToString())"
    
    if ($psVersion.Major -ge 5) {
        if ($psVersion.Major -eq 5 -and $psVersion.Minor -eq 0) {
            Write-Warning "PowerShell 5.1 is recommended for better compatibility"
        } else {
            Write-Success "PowerShell version is compatible"
        }
        
        # Check execution policy
        $executionPolicy = Get-ExecutionPolicy
        Write-Info "Execution policy: $executionPolicy"
        
        if ($executionPolicy -eq "Restricted") {
            Write-Warning "PowerShell execution policy is Restricted"
            
            if ($AutoFix) {
                Write-Info "Setting execution policy to RemoteSigned for current user..."
                try {
                    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                    Write-Success "Execution policy updated to RemoteSigned"
                } catch {
                    Write-Error "Failed to update execution policy: $_"
                    return $false
                }
            } else {
                Write-Info "To fix: Run 'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser' or use -AutoFix"
                return $false
            }
        }
        
        return $true
    } else {
        Write-Error "PowerShell 5.0+ is required. Current version: $($psVersion.ToString())"
        Write-Info "Please update PowerShell: https://docs.microsoft.com/powershell/scripting/install/installing-powershell-core-on-windows"
        return $false
    }
}

function Test-SystemRequirements {
    Write-Host "`n🔍 Checking system requirements..." -ForegroundColor Blue
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    Write-Info "Windows version: $($osVersion.ToString())"
    
    if ($osVersion.Major -lt 10) {
        Write-Error "Windows 10 or higher is required"
        return $false
    } else {
        Write-Success "Windows version is supported"
    }
    
    # Check disk space
    $systemDrive = Get-PSDrive -Name C
    $freeSpaceGB = [math]::Round($systemDrive.Free / 1GB, 2)
    Write-Info "Available disk space: $freeSpaceGB GB"
    
    if ($freeSpaceGB -lt 2) {
        Write-Error "Insufficient disk space. At least 2GB free space is required."
        return $false
    } elseif ($freeSpaceGB -lt 5) {
        Write-Warning "Limited disk space. Consider freeing up space for better performance."
    } else {
        Write-Success "Sufficient disk space available"
    }
    
    # Check internet connectivity
    try {
        $testConnection = Test-NetConnection -ComputerName "www.google.com" -Port 80 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($testConnection) {
            Write-Success "Internet connectivity is available"
        } else {
            Write-Warning "Internet connectivity test failed"
        }
    } catch {
        Write-Warning "Could not test internet connectivity"
    }
    
    return $true
}

function Show-Summary {
    param($Results)
    
    Write-Host "`n" + "="*60 -ForegroundColor Blue
    Write-Host "SYSTEM COMPATIBILITY SUMMARY" -ForegroundColor Blue
    Write-Host "="*60 -ForegroundColor Blue
    
    $allPassed = $true
    foreach ($result in $Results.GetEnumerator()) {
        if ($result.Value) {
            Write-Success "$($result.Key): PASSED"
        } else {
            Write-Error "$($result.Key): FAILED"
            $allPassed = $false
        }
    }
    
    Write-Host "`n" + "="*60 -ForegroundColor Blue
    
    if ($allPassed) {
        Write-Success "🎉 Your system is ready for MCP Server installation!"
        Write-Info "You can now run the main MCP installer with confidence."
    } else {
        Write-Error "❌ System compatibility issues detected!"
        Write-Info "Please resolve the issues above before running the MCP installer."
        Write-Info "You can run this script with -AutoFix to attempt automatic fixes."
    }
}

# Main execution
Write-Host "🚀 MCP System Compatibility Checker" -ForegroundColor Blue
Write-Host "Checking if your system is ready for MCP Server installation..." -ForegroundColor Gray

if ($AutoFix) {
    Write-Info "Auto-fix mode enabled - will attempt to resolve issues automatically"
}

$results = @{}

# Run all checks
$results["PowerShell Compatibility"] = Test-PowerShellCompatibility
$results["System Requirements"] = Test-SystemRequirements
$results["Windows Package Manager"] = Test-WingetInstallation
$results["Node.js Installation"] = Test-NodeJSInstallation

# Show summary
Show-Summary -Results $results

# Provide next steps
Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Blue
if ($results.Values -contains $false) {
    Write-Info "1. Resolve the issues listed above"
    Write-Info "2. Run this script again to verify fixes"
    Write-Info "3. Once all checks pass, run the main MCP installer"
    
    if (-not $AutoFix) {
        Write-Info "`n💡 TIP: Run this script with -AutoFix to automatically resolve common issues:"
        Write-Host "   .\System-Checker.ps1 -AutoFix" -ForegroundColor Yellow
    }
} else {
    Write-Info "1. Run the main MCP installer: .\Launch-Advanced-MCP.bat"
    Write-Info "2. Choose your preferred installation method"
    Write-Info "3. Select configuration profiles that match your needs"
}

Write-Host "`n📖 For more help, check the documentation or run the installer's help option." -ForegroundColor Gray
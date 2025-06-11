# PowerShell script to build MCP Docker images locally
# Quick setup for testing without full docker-compose

param(
    [string]$Image = "all",
    [switch]$Test,
    [switch]$Push
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== MCP Docker Image Builder ===" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "[+] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and start it" -ForegroundColor Yellow
    exit 1
}

# Change to docker directory
Set-Location $ScriptDir

# Define images to build
$Images = @{
    "filesystem" = @{
        "tag" = "mcp-filesystem:latest"
        "dockerfile" = "Dockerfile.filesystem"
        "description" = "Filesystem MCP Server"
    }
    "browser" = @{
        "tag" = "mcp-browser:latest" 
        "dockerfile" = "Dockerfile.playwright"
        "description" = "Browser Automation MCP Server"
    }
}

function Build-MCPImage {
    param($ImageInfo, $ImageName)
    
    $tag = $ImageInfo.tag
    $dockerfile = $ImageInfo.dockerfile
    $description = $ImageInfo.description
    
    Write-Host "`n[i] Building: $description" -ForegroundColor Blue
    Write-Host "    Tag: $tag" -ForegroundColor White
    Write-Host "    Dockerfile: $dockerfile" -ForegroundColor White
    
    if (-not (Test-Path $dockerfile)) {
        Write-Host "    [X] Dockerfile not found: $dockerfile" -ForegroundColor Red
        return $false
    }
    
    # Build the image
    $buildCmd = "docker build -f $dockerfile -t $tag ."
    Write-Host "    [>] $buildCmd" -ForegroundColor Yellow
    
    try {
        Invoke-Expression $buildCmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    [+] Build successful: $tag" -ForegroundColor Green
            return $true
        } else {
            Write-Host "    [X] Build failed: $tag" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "    [X] Build error: $_" -ForegroundColor Red
        return $false
    }
}

function Test-MCPImage {
    param($ImageInfo)
    
    $tag = $ImageInfo.tag
    Write-Host "`n[i] Testing image: $tag" -ForegroundColor Blue
    
    try {
        # Test that image exists
        docker image inspect $tag | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    [+] Image exists: $tag" -ForegroundColor Green
            
            # Get image size
            $size = docker image inspect $tag --format "{{.Size}}" | ForEach-Object { [math]::Round($_ / 1MB, 1) }
            Write-Host "    [i] Image size: ${size} MB" -ForegroundColor Blue
            
            return $true
        } else {
            Write-Host "    [X] Image not found: $tag" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "    [X] Test error: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
$successful = @()
$failed = @()

if ($Image -eq "all") {
    $imagesToBuild = $Images.Keys
} else {
    if ($Images.ContainsKey($Image)) {
        $imagesToBuild = @($Image)
    } else {
        Write-Host "[X] Unknown image: $Image" -ForegroundColor Red
        Write-Host "Available images: $($Images.Keys -join ', ')" -ForegroundColor Yellow
        exit 1
    }
}

foreach ($imageName in $imagesToBuild) {
    $imageInfo = $Images[$imageName]
    
    if (Build-MCPImage $imageInfo $imageName) {
        $successful += $imageName
        
        if ($Test) {
            Test-MCPImage $imageInfo | Out-Null
        }
    } else {
        $failed += $imageName
    }
}

# Summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "BUILD SUMMARY" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Cyan

if ($successful.Count -gt 0) {
    Write-Host "✅ Successful builds:" -ForegroundColor Green
    foreach ($img in $successful) {
        Write-Host "   - $($Images[$img].description) ($($Images[$img].tag))" -ForegroundColor White
    }
}

if ($failed.Count -gt 0) {
    Write-Host "❌ Failed builds:" -ForegroundColor Red
    foreach ($img in $failed) {
        Write-Host "   - $($Images[$img].description) ($($Images[$img].tag))" -ForegroundColor White
    }
}

Write-Host "`n[i] To test installations, use the MCP Installer GUI" -ForegroundColor Blue
Write-Host "[i] Images are now available for Docker-first installation" -ForegroundColor Blue
# MCP Server Auto-Discovery and Community Marketplace
# Automatically discovers and catalogs available MCP servers from multiple sources

param(
    [switch]$UpdateCatalog = $false,
    [switch]$ShowAvailable = $false,
    [string]$SearchTerm = "",
    [switch]$AddToInstaller = $false
)

# Community sources for MCP servers
$Global:MCPSources = @{
    "official" = @{
        name = "Official MCP Servers"
        url = "https://api.github.com/repos/modelcontextprotocol/servers/contents/src"
        type = "github"
        priority = 1
    }
    "awesome-mcp" = @{
        name = "Awesome MCP Collection"
        url = "https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md"
        type = "markdown"
        priority = 2
    }
    "npm-search" = @{
        name = "NPM MCP Packages"
        url = "https://registry.npmjs.org/-/v1/search?text=mcp-server&size=100"
        type = "npm"
        priority = 3
    }
    "docker-hub" = @{
        name = "Docker Hub MCP Images"
        url = "https://hub.docker.com/v2/search/repositories/?query=mcp-server&page_size=100"
        type = "docker"
        priority = 4
    }
}

function Get-GitHubMCPServers {
    param([string]$ApiUrl)
    
    try {
        Write-Host "🔍 Scanning GitHub repositories..." -ForegroundColor Cyan
        
        $response = Invoke-RestMethod -Uri $ApiUrl -Headers @{
            "User-Agent" = "MCP-Installer/1.0"
            "Accept" = "application/vnd.github.v3+json"
        }
        
        $servers = @()
        foreach ($item in $response) {
            if ($item.type -eq "dir" -and $item.name -like "*mcp*") {
                # Get package.json or setup.py to extract server info
                $packageUrl = "https://api.github.com/repos/modelcontextprotocol/servers/contents/src/$($item.name)/package.json"
                try {
                    $packageInfo = Invoke-RestMethod -Uri $packageUrl -Headers @{
                        "User-Agent" = "MCP-Installer/1.0"
                        "Accept" = "application/vnd.github.v3+json"
                    }
                    
                    $packageJson = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($packageInfo.content)) | ConvertFrom-Json
                    
                    $servers += @{
                        id = $item.name -replace "mcp-server-", ""
                        name = $packageJson.description ?? $item.name
                        description = $packageJson.description ?? "Official MCP Server"
                        category = "Official"
                        type = "npm"
                        installation = @{
                            command = "npx"
                            args = @("@modelcontextprotocol/server-$($item.name -replace 'mcp-server-', '')")
                        }
                        source = "official"
                        repository = "https://github.com/modelcontextprotocol/servers/tree/main/src/$($item.name)"
                        supported_ides = @("claude-desktop", "cursor", "vscode")
                        requires_docker = $false
                        prerequisites = @("node18+")
                    }
                } catch {
                    # Skip if can't parse package info
                }
            }
        }
        
        return $servers
    } catch {
        Write-Host "❌ Failed to fetch GitHub servers: $_" -ForegroundColor Red
        return @()
    }
}

function Get-NPMMCPServers {
    param([string]$SearchUrl)
    
    try {
        Write-Host "📦 Searching NPM registry..." -ForegroundColor Cyan
        
        $response = Invoke-RestMethod -Uri $SearchUrl
        $servers = @()
        
        foreach ($package in $response.objects) {
            $pkg = $package.package
            if ($pkg.name -like "*mcp*" -and $pkg.name -notlike "*test*") {
                $servers += @{
                    id = $pkg.name -replace "@.*/" -replace "mcp-server-" -replace "-mcp"
                    name = $pkg.description ?? $pkg.name
                    description = $pkg.description ?? "Community MCP Server"
                    category = "Community"
                    type = "npm"
                    installation = @{
                        command = "npx"
                        args = @($pkg.name)
                    }
                    source = "npm"
                    repository = $pkg.links.repository ?? $pkg.links.homepage
                    supported_ides = @("claude-desktop", "cursor", "vscode")
                    requires_docker = $false
                    prerequisites = @("node18+")
                    version = $pkg.version
                    downloads = $pkg.downloads ?? 0
                }
            }
        }
        
        return $servers
    } catch {
        Write-Host "❌ Failed to fetch NPM servers: $_" -ForegroundColor Red
        return @()
    }
}

function Get-DockerMCPServers {
    param([string]$SearchUrl)
    
    try {
        Write-Host "🐳 Searching Docker Hub..." -ForegroundColor Cyan
        
        $response = Invoke-RestMethod -Uri $SearchUrl
        $servers = @()
        
        foreach ($repo in $response.results) {
            if ($repo.name -like "*mcp*") {
                $servers += @{
                    id = $repo.name -replace ".*/" -replace "mcp-server-" -replace "-mcp"
                    name = $repo.short_description ?? $repo.name
                    description = $repo.short_description ?? "Docker MCP Server"
                    category = "Docker"
                    type = "docker"
                    installation = @{
                        command = "docker"
                        args = @("run", "-i", "--rm", $repo.name)
                    }
                    source = "docker"
                    repository = "https://hub.docker.com/r/$($repo.name)"
                    supported_ides = @("claude-desktop", "cursor", "vscode")
                    requires_docker = $true
                    prerequisites = @("docker")
                    pulls = $repo.pull_count ?? 0
                }
            }
        }
        
        return $servers
    } catch {
        Write-Host "❌ Failed to fetch Docker servers: $_" -ForegroundColor Red
        return @()
    }
}

function Update-MCPCatalog {
    Write-Host "🔄 Updating MCP Server Catalog..." -ForegroundColor Blue
    
    $allServers = @()
    
    foreach ($source in $Global:MCPSources.GetEnumerator()) {
        Write-Host "`n📊 Processing source: $($source.Value.name)" -ForegroundColor Yellow
        
        switch ($source.Value.type) {
            "github" {
                $servers = Get-GitHubMCPServers -ApiUrl $source.Value.url
                $allServers += $servers
            }
            "npm" {
                $servers = Get-NPMMCPServers -SearchUrl $source.Value.url
                $allServers += $servers
            }
            "docker" {
                $servers = Get-DockerMCPServers -SearchUrl $source.Value.url
                $allServers += $servers
            }
        }
        
        Write-Host "   Found $($servers.Count) servers" -ForegroundColor Gray
    }
    
    # Remove duplicates based on ID
    $uniqueServers = $allServers | Group-Object -Property id | ForEach-Object {
        # Keep the one with highest priority source
        $_.Group | Sort-Object { $Global:MCPSources[$_.source].priority } | Select-Object -First 1
    }
    
    # Save to discovery catalog
    $catalogPath = Join-Path $PSScriptRoot "mcp-discovery-catalog.json"
    $catalog = @{
        last_updated = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        total_servers = $uniqueServers.Count
        sources = $Global:MCPSources.Keys
        servers = $uniqueServers
    }
    
    $catalog | ConvertTo-Json -Depth 10 | Set-Content $catalogPath -Encoding UTF8
    
    Write-Host "`n✅ Catalog updated! Found $($uniqueServers.Count) unique MCP servers" -ForegroundColor Green
    Write-Host "📁 Saved to: $catalogPath" -ForegroundColor Cyan
    
    return $uniqueServers
}

function Search-MCPServers {
    param([string]$SearchTerm)
    
    $catalogPath = Join-Path $PSScriptRoot "mcp-discovery-catalog.json"
    
    if (-not (Test-Path $catalogPath)) {
        Write-Host "📊 No catalog found. Updating..." -ForegroundColor Yellow
        Update-MCPCatalog | Out-Null
    }
    
    $catalog = Get-Content $catalogPath | ConvertFrom-Json
    $servers = $catalog.servers
    
    if ($SearchTerm) {
        $servers = $servers | Where-Object {
            $_.name -like "*$SearchTerm*" -or 
            $_.description -like "*$SearchTerm*" -or 
            $_.category -like "*$SearchTerm*"
        }
    }
    
    return $servers
}

function Show-MCPServerCatalog {
    param([array]$Servers)
    
    Write-Host "`n🌟 Available MCP Servers" -ForegroundColor Blue
    Write-Host "=========================" -ForegroundColor Blue
    
    $groupedServers = $Servers | Group-Object -Property category | Sort-Object Name
    
    foreach ($group in $groupedServers) {
        Write-Host "`n📁 $($group.Name) ($($group.Count) servers)" -ForegroundColor Yellow
        Write-Host ("-" * 50) -ForegroundColor Gray
        
        foreach ($server in ($group.Group | Sort-Object name)) {
            $typeIcon = switch ($server.type) {
                "npm" { "📦" }
                "python" { "🐍" }
                "docker" { "🐳" }
                default { "⚙️" }
            }
            
            $sourceIcon = switch ($server.source) {
                "official" { "✅" }
                "npm" { "📦" }
                "docker" { "🐳" }
                default { "🌐" }
            }
            
            Write-Host "  $typeIcon $sourceIcon $($server.name.PadRight(30))" -NoNewline
            Write-Host " | $($server.description)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`nLegend: ✅ Official | 📦 NPM | 🐳 Docker | 🌐 Community" -ForegroundColor Cyan
}

function Add-ServerToInstaller {
    param([object]$Server)
    
    $configPath = Join-Path $PSScriptRoot "mcp-servers-config.json"
    
    try {
        # Load existing configuration
        $config = Get-Content $configPath | ConvertFrom-Json
        
        # Check if server already exists
        $existingServer = $config.servers | Where-Object { $_.id -eq $Server.id }
        if ($existingServer) {
            Write-Host "⚠️ Server '$($Server.id)' already exists in installer" -ForegroundColor Yellow
            $response = Read-Host "Update existing server? (y/n)"
            if ($response -ne 'y') {
                return $false
            }
            
            # Remove existing
            $config.servers = $config.servers | Where-Object { $_.id -ne $Server.id }
        }
        
        # Add new server
        $config.servers += $Server
        
        # Save updated configuration
        $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
        
        Write-Host "✅ Added '$($Server.name)' to installer catalog" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "❌ Failed to add server to installer: $_" -ForegroundColor Red
        return $false
    }
}

function Show-ServerDetails {
    param([object]$Server)
    
    Write-Host "`n📋 Server Details" -ForegroundColor Blue
    Write-Host "=================" -ForegroundColor Blue
    Write-Host "Name: $($Server.name)" -ForegroundColor White
    Write-Host "ID: $($Server.id)" -ForegroundColor Gray
    Write-Host "Description: $($Server.description)" -ForegroundColor White
    Write-Host "Category: $($Server.category)" -ForegroundColor Cyan
    Write-Host "Type: $($Server.type)" -ForegroundColor Cyan
    Write-Host "Source: $($Server.source)" -ForegroundColor Cyan
    
    if ($Server.repository) {
        Write-Host "Repository: $($Server.repository)" -ForegroundColor Blue
    }
    
    if ($Server.version) {
        Write-Host "Version: $($Server.version)" -ForegroundColor Green
    }
    
    if ($Server.downloads) {
        Write-Host "Downloads: $($Server.downloads)" -ForegroundColor Green
    }
    
    Write-Host "`nInstallation Command:" -ForegroundColor Yellow
    Write-Host "$($Server.installation.command) $($Server.installation.args -join ' ')" -ForegroundColor White
    
    Write-Host "`nSupported IDEs: $($Server.supported_ides -join ', ')" -ForegroundColor Cyan
    Write-Host "Prerequisites: $($Server.prerequisites -join ', ')" -ForegroundColor Cyan
    Write-Host "Requires Docker: $($Server.requires_docker)" -ForegroundColor Cyan
}

# Main execution
Write-Host "🔍 MCP Server Discovery Tool" -ForegroundColor Blue

if ($UpdateCatalog) {
    Update-MCPCatalog
    exit 0
}

if ($ShowAvailable -or $SearchTerm) {
    $servers = Search-MCPServers -SearchTerm $SearchTerm
    Show-MCPServerCatalog -Servers $servers
    
    if ($AddToInstaller -and $servers.Count -gt 0) {
        Write-Host "`nSelect servers to add to installer:" -ForegroundColor Yellow
        for ($i = 0; $i -lt $servers.Count; $i++) {
            Write-Host "[$i] $($servers[$i].name)" -ForegroundColor White
        }
        
        $selection = Read-Host "Enter server number (or 'q' to quit)"
        if ($selection -ne 'q' -and $selection -match '^\d+$') {
            $selectedIndex = [int]$selection
            if ($selectedIndex -ge 0 -and $selectedIndex -lt $servers.Count) {
                $selectedServer = $servers[$selectedIndex]
                Show-ServerDetails -Server $selectedServer
                
                $confirm = Read-Host "`nAdd this server to installer? (y/n)"
                if ($confirm -eq 'y') {
                    Add-ServerToInstaller -Server $selectedServer
                }
            }
        }
    }
    exit 0
}

# Interactive mode
Write-Host @"

🚀 MCP Server Discovery Menu:

[1] Update server catalog from all sources
[2] Browse available servers
[3] Search for specific servers
[4] Add servers to installer
[5] Show catalog statistics
[6] Exit

"@ -ForegroundColor Cyan

$choice = Read-Host "Select option"

switch ($choice) {
    "1" { Update-MCPCatalog }
    "2" { 
        $servers = Search-MCPServers
        Show-MCPServerCatalog -Servers $servers
    }
    "3" {
        $searchTerm = Read-Host "Enter search term"
        $servers = Search-MCPServers -SearchTerm $searchTerm
        Show-MCPServerCatalog -Servers $servers
    }
    "4" {
        $servers = Search-MCPServers
        Show-MCPServerCatalog -Servers $servers
        # Interactive selection logic here
    }
    "5" {
        $catalogPath = Join-Path $PSScriptRoot "mcp-discovery-catalog.json"
        if (Test-Path $catalogPath) {
            $catalog = Get-Content $catalogPath | ConvertFrom-Json
            Write-Host "`n📊 Catalog Statistics" -ForegroundColor Blue
            Write-Host "Last Updated: $($catalog.last_updated)" -ForegroundColor Gray
            Write-Host "Total Servers: $($catalog.total_servers)" -ForegroundColor Green
            Write-Host "Sources: $($catalog.sources -join ', ')" -ForegroundColor Cyan
        } else {
            Write-Host "No catalog found. Run option 1 to create one." -ForegroundColor Yellow
        }
    }
    default { exit 0 }
}
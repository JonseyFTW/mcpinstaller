# MCP Server Setup Wizard - Guided Installation Experience
# Provides step-by-step guidance for first-time users

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Wizard state
$Global:WizardState = @{
    CurrentStep = 0
    UserProfile = @{}
    SelectedServers = @()
    SelectedIDEs = @()
    CompletedSteps = @()
}

function Show-WelcomeStep {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "MCP Server Setup Wizard - Welcome"
    $form.Size = New-Object System.Drawing.Size(600, 500)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    
    # Main panel with gradient background
    $mainPanel = New-Object System.Windows.Forms.Panel
    $mainPanel.Dock = "Fill"
    $mainPanel.BackColor = [System.Drawing.Color]::FromArgb(240, 248, 255)
    $form.Controls.Add($mainPanel)
    
    # Welcome header
    $headerLabel = New-Object System.Windows.Forms.Label
    $headerLabel.Text = "[>] Welcome to MCP Server Installer!"
    $headerLabel.Font = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
    $headerLabel.ForeColor = [System.Drawing.Color]::FromArgb(25, 118, 210)
    $headerLabel.TextAlign = "MiddleCenter"
    $headerLabel.Location = New-Object System.Drawing.Point(20, 30)
    $headerLabel.Size = New-Object System.Drawing.Size(560, 40)
    $mainPanel.Controls.Add($headerLabel)
    
    # Description
    $descLabel = New-Object System.Windows.Forms.Label
    $descLabel.Text = @"
This wizard will help you set up Model Context Protocol (MCP) servers for your development environment.

MCP servers enhance AI assistants like Claude with specialized capabilities:

[+] Development Tools - File operations, Git integration, terminal access
[=] Database Access - PostgreSQL, MongoDB, and more
[~] Web Services - GitHub, REST APIs, web scraping
[i] Documentation - Context-aware help and references
[D] DevOps - Docker, Kubernetes, CI/CD integration

We'll guide you through:
1. Detecting your development environment
2. Recommending suitable MCP servers
3. Installing and configuring everything automatically

Ready to enhance your AI development experience?
"@
    $descLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $descLabel.Location = New-Object System.Drawing.Point(40, 90)
    $descLabel.Size = New-Object System.Drawing.Size(520, 280)
    $mainPanel.Controls.Add($descLabel)
    
    # Buttons
    $nextButton = New-Object System.Windows.Forms.Button
    $nextButton.Text = "Get Started >>"
    $nextButton.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $nextButton.BackColor = [System.Drawing.Color]::FromArgb(76, 175, 80)
    $nextButton.ForeColor = [System.Drawing.Color]::White
    $nextButton.FlatStyle = "Flat"
    $nextButton.Location = New-Object System.Drawing.Point(450, 400)
    $nextButton.Size = New-Object System.Drawing.Size(120, 35)
    $nextButton.Add_Click({
        $Global:WizardState.CurrentStep = 1
        $form.DialogResult = "OK"
        $form.Close()
    })
    $mainPanel.Controls.Add($nextButton)
    
    $skipButton = New-Object System.Windows.Forms.Button
    $skipButton.Text = "Skip Wizard"
    $skipButton.Location = New-Object System.Drawing.Point(320, 400)
    $skipButton.Size = New-Object System.Drawing.Size(100, 35)
    $skipButton.Add_Click({
        $Global:WizardState.CurrentStep = -1
        $form.DialogResult = "Cancel"
        $form.Close()
    })
    $mainPanel.Controls.Add($skipButton)
    
    $result = $form.ShowDialog()
    $form.Dispose()
    
    return $result
}

function Show-EnvironmentDetectionStep {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Environment Detection"
    $form.Size = New-Object System.Drawing.Size(700, 600)
    $form.StartPosition = "CenterScreen"
    
    # Progress indicator
    $progressLabel = New-Object System.Windows.Forms.Label
    $progressLabel.Text = "Step 1 of 4: Detecting Your Development Environment"
    $progressLabel.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $progressLabel.Location = New-Object System.Drawing.Point(20, 20)
    $progressLabel.Size = New-Object System.Drawing.Size(650, 30)
    $form.Controls.Add($progressLabel)
    
    # Detection results
    $resultsPanel = New-Object System.Windows.Forms.Panel
    $resultsPanel.Location = New-Object System.Drawing.Point(20, 60)
    $resultsPanel.Size = New-Object System.Drawing.Size(650, 400)
    $resultsPanel.BorderStyle = "FixedSingle"
    $resultsPanel.AutoScroll = $true
    $form.Controls.Add($resultsPanel)
    
    $statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.Text = "[?] Scanning your system..."
    $statusLabel.Location = New-Object System.Drawing.Point(10, 10)
    $statusLabel.Size = New-Object System.Drawing.Size(620, 30)
    $statusLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    $resultsPanel.Controls.Add($statusLabel)
    
    # Start detection
    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 500
    $detectionStep = 0
    
    $timer.Add_Tick({
        switch ($detectionStep) {
            0 {
                $statusLabel.Text = "[?] Checking installed IDEs..."
                $Global:WizardState.UserProfile.IDEs = Detect-UserIDEs
                $detectionStep++
            }
            1 {
                $statusLabel.Text = "[?] Analyzing development tools..."
                $Global:WizardState.UserProfile.DevTools = Detect-DevTools
                $detectionStep++
            }
            2 {
                $statusLabel.Text = "[?] Scanning project directories..."
                $Global:WizardState.UserProfile.Projects = Detect-ProjectTypes
                $detectionStep++
            }
            3 {
                $statusLabel.Text = "[+] Detection complete!"
                $timer.Stop()
                Show-DetectionResults -Panel $resultsPanel
                Enable-NextButton
            }
        }
    })
    
    # Navigation buttons
    $nextButton = New-Object System.Windows.Forms.Button
    $nextButton.Text = "Next >>"
    $nextButton.Location = New-Object System.Drawing.Point(580, 520)
    $nextButton.Size = New-Object System.Drawing.Size(90, 30)
    $nextButton.Enabled = $false
    $nextButton.Add_Click({
        $Global:WizardState.CurrentStep = 2
        $form.DialogResult = "OK"
        $form.Close()
    })
    $form.Controls.Add($nextButton)
    
    $backButton = New-Object System.Windows.Forms.Button
    $backButton.Text = "<< Back"
    $backButton.Location = New-Object System.Drawing.Point(480, 520)
    $backButton.Size = New-Object System.Drawing.Size(90, 30)
    $backButton.Add_Click({
        $Global:WizardState.CurrentStep = 0
        $form.DialogResult = "Retry"
        $form.Close()
    })
    $form.Controls.Add($backButton)
    
    function Enable-NextButton {
        $nextButton.Enabled = $true
        $nextButton.BackColor = [System.Drawing.Color]::FromArgb(76, 175, 80)
        $nextButton.ForeColor = [System.Drawing.Color]::White
    }
    
    $timer.Start()
    $result = $form.ShowDialog()
    $timer.Stop()
    $form.Dispose()
    
    return $result
}

function Detect-UserIDEs {
    $ides = @{}
    
    # Check VS Code
    $vscodeResult = Test-VSCodeInstalled
    if ($vscodeResult.installed) {
        $ides["vscode"] = @{
            name = "Visual Studio Code"
            path = $vscodeResult.path
            extensions = Test-VSCodeExtensions
        }
    }
    
    # Check other IDEs
    $otherIDEs = @{
        "Claude Desktop" = @(
            "$env:APPDATA\Claude\claude_desktop_config.json",
            "$env:LOCALAPPDATA\Programs\Claude\Claude.exe"
        )
        "Cursor" = @(
            "$env:USERPROFILE\.cursor\mcp.json", 
            "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe"
        )
        "Windsurf" = @(
            "$env:APPDATA\Windsurf\User\settings.json",
            "$env:LOCALAPPDATA\Programs\Windsurf\Windsurf.exe"
        )
    }
    
    foreach ($ide in $otherIDEs.GetEnumerator()) {
        foreach ($path in $ide.Value) {
            $expandedPath = [System.Environment]::ExpandEnvironmentVariables($path)
            if (Test-Path $expandedPath) {
                $ides[$ide.Key.ToLower().Replace(" ", "")] = @{
                    name = $ide.Key
                    path = $expandedPath
                }
                break
            }
        }
    }
    
    return $ides
}

function Detect-DevTools {
    $tools = @{}
    
    # Check common dev tools
    $toolChecks = @{
        "node" = { node --version 2>$null }
        "python" = { python --version 2>$null }
        "git" = { git --version 2>$null }
        "docker" = { docker --version 2>$null }
        "npm" = { npm --version 2>$null }
        "pip" = { pip --version 2>$null }
    }
    
    foreach ($tool in $toolChecks.GetEnumerator()) {
        try {
            $version = & $tool.Value
            if ($version) {
                $tools[$tool.Key] = $version
            }
        } catch {
            # Tool not found
        }
    }
    
    return $tools
}

function Detect-ProjectTypes {
    $projects = @{}
    $commonDirs = @("C:\Projects", "C:\Dev", "C:\Code", "$env:USERPROFILE\Documents", "$env:USERPROFILE\Desktop")
    
    foreach ($dir in $commonDirs) {
        if (Test-Path $dir) {
            $subdirs = Get-ChildItem $dir -Directory -ErrorAction SilentlyContinue | Select-Object -First 10
            foreach ($subdir in $subdirs) {
                # Check for project indicators
                $projectType = @()
                
                if (Test-Path (Join-Path $subdir.FullName "package.json")) { $projectType += "Node.js" }
                if (Test-Path (Join-Path $subdir.FullName "requirements.txt")) { $projectType += "Python" }
                if (Test-Path (Join-Path $subdir.FullName "Dockerfile")) { $projectType += "Docker" }
                if (Test-Path (Join-Path $subdir.FullName ".git")) { $projectType += "Git" }
                if (Test-Path (Join-Path $subdir.FullName "*.sln")) { $projectType += ".NET" }
                
                if ($projectType.Count -gt 0) {
                    $projects[$subdir.Name] = $projectType
                }
            }
        }
    }
    
    return $projects
}

function Show-DetectionResults {
    param($Panel)
    
    $Panel.Controls.Clear()
    
    $y = 10
    
    # Show IDEs
    $ideLabel = New-Object System.Windows.Forms.Label
    $ideLabel.Text = "[!] Detected IDEs:"
    $ideLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $ideLabel.Location = New-Object System.Drawing.Point(10, $y)
    $ideLabel.Size = New-Object System.Drawing.Size(200, 25)
    $Panel.Controls.Add($ideLabel)
    $y += 30
    
    foreach ($ide in $Global:WizardState.UserProfile.IDEs.GetEnumerator()) {
        $ideItem = New-Object System.Windows.Forms.Label
        $ideItem.Text = "  [+] $($ide.Value.name)"
        $ideItem.Location = New-Object System.Drawing.Point(20, $y)
        $ideItem.Size = New-Object System.Drawing.Size(600, 20)
        $Panel.Controls.Add($ideItem)
        $y += 25
    }
    
    $y += 10
    
    # Show Dev Tools
    $toolLabel = New-Object System.Windows.Forms.Label
    $toolLabel.Text = "[+] Development Tools:"
    $toolLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $toolLabel.Location = New-Object System.Drawing.Point(10, $y)
    $toolLabel.Size = New-Object System.Drawing.Size(200, 25)
    $Panel.Controls.Add($toolLabel)
    $y += 30
    
    foreach ($tool in $Global:WizardState.UserProfile.DevTools.GetEnumerator()) {
        $toolItem = New-Object System.Windows.Forms.Label
        $toolItem.Text = "  [+] $($tool.Key): $($tool.Value)"
        $toolItem.Location = New-Object System.Drawing.Point(20, $y)
        $toolItem.Size = New-Object System.Drawing.Size(600, 20)
        $Panel.Controls.Add($toolItem)
        $y += 25
    }
    
    $y += 10
    
    # Show Projects
    $projLabel = New-Object System.Windows.Forms.Label
    $projLabel.Text = "[#] Project Types Found:"
    $projLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $projLabel.Location = New-Object System.Drawing.Point(10, $y)
    $projLabel.Size = New-Object System.Drawing.Size(200, 25)
    $Panel.Controls.Add($projLabel)
    $y += 30
    
    $projectTypes = @{}
    foreach ($project in $Global:WizardState.UserProfile.Projects.GetEnumerator()) {
        foreach ($type in $project.Value) {
            if (-not $projectTypes.ContainsKey($type)) { $projectTypes[$type] = 0 }
            $projectTypes[$type] = $projectTypes[$type] + 1
        }
    }
    
    foreach ($type in $projectTypes.GetEnumerator()) {
        $typeItem = New-Object System.Windows.Forms.Label
        $typeItem.Text = "  [#] $($type.Key) ($($type.Value) projects)"
        $typeItem.Location = New-Object System.Drawing.Point(20, $y)
        $typeItem.Size = New-Object System.Drawing.Size(600, 20)
        $Panel.Controls.Add($typeItem)
        $y += 25
    }
}

function Show-RecommendationsStep {
    # Generate smart recommendations based on detected environment
    $recommendations = Generate-SmartRecommendations
    
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Server Recommendations"
    $form.Size = New-Object System.Drawing.Size(800, 700)
    $form.StartPosition = "CenterScreen"
    
    # Progress indicator
    $progressLabel = New-Object System.Windows.Forms.Label
    $progressLabel.Text = "Step 2 of 4: Smart Server Recommendations"
    $progressLabel.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $progressLabel.Location = New-Object System.Drawing.Point(20, 20)
    $progressLabel.Size = New-Object System.Drawing.Size(750, 30)
    $form.Controls.Add($progressLabel)
    
    # Recommendations panel
    $recsPanel = New-Object System.Windows.Forms.Panel
    $recsPanel.Location = New-Object System.Drawing.Point(20, 60)
    $recsPanel.Size = New-Object System.Drawing.Size(750, 500)
    $recsPanel.BorderStyle = "FixedSingle"
    $recsPanel.AutoScroll = $true
    $form.Controls.Add($recsPanel)
    
    Show-Recommendations -Panel $recsPanel -Recommendations $recommendations
    
    # Navigation
    $nextButton = New-Object System.Windows.Forms.Button
    $nextButton.Text = "Install Selected >>"
    $nextButton.Location = New-Object System.Drawing.Point(650, 600)
    $nextButton.Size = New-Object System.Drawing.Size(120, 30)
    $nextButton.BackColor = [System.Drawing.Color]::FromArgb(76, 175, 80)
    $nextButton.ForeColor = [System.Drawing.Color]::White
    $nextButton.Add_Click({
        $Global:WizardState.CurrentStep = 3
        $form.DialogResult = "OK"
        $form.Close()
    })
    $form.Controls.Add($nextButton)
    
    $result = $form.ShowDialog()
    $form.Dispose()
    
    return $result
}

function Generate-SmartRecommendations {
    $recommendations = @{
        essential = @()
        recommended = @()
        optional = @()
    }
    
    # Essential servers for everyone
    $recommendations.essential += @{
        name = "Filesystem Operations"
        id = "filesystem"
        reason = "Essential for file management in any development environment"
        category = "Core"
    }
    
    # Based on detected IDEs
    if ($Global:WizardState.UserProfile.IDEs.Count -gt 0) {
        $recommendations.essential += @{
            name = "Context7 Documentation"
            id = "context7"
            reason = "Provides real-time documentation for your IDE"
            category = "Documentation"
        }
    }
    
    # Based on detected tools
    if ($Global:WizardState.UserProfile.DevTools.ContainsKey("git")) {
        $recommendations.recommended += @{
            name = "Git Operations"
            id = "git"
            reason = "You have Git installed - this adds advanced Git capabilities"
            category = "Development"
        }
    }
    
    if ($Global:WizardState.UserProfile.DevTools.ContainsKey("docker")) {
        $recommendations.recommended += @{
            name = "Docker Management"
            id = "docker-mcp"
            reason = "You have Docker installed - manage containers from your AI assistant"
            category = "DevOps"
        }
    }
    
    # Based on project types
    $projectTypes = @()
    foreach ($project in $Global:WizardState.UserProfile.Projects.GetEnumerator()) {
        $projectTypes += $project.Value
    }
    
    if ($projectTypes -contains "Node.js") {
        $recommendations.recommended += @{
            name = "Browser Tools MCP"
            id = "browser-tools"
            reason = "Perfect for web development projects"
            category = "Development"
        }
    }
    
    if ($projectTypes -contains "Python") {
        $recommendations.optional += @{
            name = "MCP Memory Service"
            id = "memory-service"
            reason = "Great for AI/ML projects with persistent memory"
            category = "Memory"
        }
    }
    
    return $recommendations
}

function Show-Recommendations {
    param($Panel, $Recommendations)
    
    $Panel.Controls.Clear()
    $y = 10
    
    foreach ($category in @("essential", "recommended", "optional")) {
        if ($Recommendations.$category.Count -eq 0) { continue }
        
        $categoryLabel = New-Object System.Windows.Forms.Label
        $categoryLabel.Text = switch ($category) {
            "essential" { "[!] Essential Servers (Highly Recommended)" }
            "recommended" { "[i] Recommended Servers (Based on Your Setup)" }
            "optional" { "[+] Optional Servers (Nice to Have)" }
        }
        $categoryLabel.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
        $categoryLabel.Location = New-Object System.Drawing.Point(10, $y)
        $categoryLabel.Size = New-Object System.Drawing.Size(700, 25)
        $Panel.Controls.Add($categoryLabel)
        $y += 35
        
        foreach ($server in $Recommendations.$category) {
            $checkbox = New-Object System.Windows.Forms.CheckBox
            $checkbox.Text = "$($server.name)"
            $checkbox.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
            $checkbox.Location = New-Object System.Drawing.Point(20, $y)
            $checkbox.Size = New-Object System.Drawing.Size(300, 25)
            $checkbox.Checked = ($category -eq "essential")
            $checkbox.Tag = $server.id
            $Panel.Controls.Add($checkbox)
            
            $reasonLabel = New-Object System.Windows.Forms.Label
            $reasonLabel.Text = $server.reason
            $reasonLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
            $reasonLabel.ForeColor = [System.Drawing.Color]::FromArgb(100, 100, 100)
            $reasonLabel.Location = New-Object System.Drawing.Point(40, $y + 25)
            $reasonLabel.Size = New-Object System.Drawing.Size(650, 20)
            $Panel.Controls.Add($reasonLabel)
            
            $y += 50
        }
        
        $y += 10
    }
}

# Main wizard execution
function Start-SetupWizard {
    Write-Host "[*] Starting MCP Setup Wizard..." -ForegroundColor Blue
    
    $Global:WizardState.CurrentStep = 0
    
    while ($Global:WizardState.CurrentStep -ge 0) {
        switch ($Global:WizardState.CurrentStep) {
            0 {
                $result = Show-WelcomeStep
                if ($result -ne "OK") { break }
            }
            1 {
                $result = Show-EnvironmentDetectionStep
                if ($result -ne "OK") { 
                    if ($result -eq "Retry") { $Global:WizardState.CurrentStep = 0 }
                    continue 
                }
            }
            2 {
                $result = Show-RecommendationsStep
                if ($result -ne "OK") { break }
            }
            3 {
                # Launch main installer with pre-selected options
                Write-Host "[>] Launching main installer with your selections..." -ForegroundColor Green
                & "$PSScriptRoot\MCP-Auto-Installer.ps1"
                $Global:WizardState.CurrentStep = -1
            }
        }
    }
    
    if ($Global:WizardState.CurrentStep -eq -1) {
        Write-Host "[i] Wizard skipped - launching advanced installer..." -ForegroundColor Yellow
        & "$PSScriptRoot\MCP-Auto-Installer.ps1"
    }
}

# Auto-start if run directly
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    Start-SetupWizard
}
# MCP Server Creator - Template-based server configuration generator
# Makes it easy to add new MCP servers to the installer

param(
    [string]$TemplateName = "",
    [switch]$ListTemplates = $false,
    [switch]$Interactive = $false,
    [string]$OutputFile = ""
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Global:Templates = $null
$Global:CreatedServer = $null

function Load-Templates {
    $templatesPath = Join-Path $PSScriptRoot "Server-Templates.json"
    
    if (-not (Test-Path $templatesPath)) {
        Write-Host "❌ Server templates file not found: $templatesPath" -ForegroundColor Red
        return $null
    }
    
    try {
        $Global:Templates = Get-Content $templatesPath | ConvertFrom-Json
        return $Global:Templates
    } catch {
        Write-Host "❌ Failed to load templates: $_" -ForegroundColor Red
        return $null
    }
}

function Show-TemplateList {
    if (-not $Global:Templates) {
        Write-Host "❌ No templates loaded" -ForegroundColor Red
        return
    }
    
    Write-Host "`n🎯 Available MCP Server Templates" -ForegroundColor Blue
    Write-Host "==================================" -ForegroundColor Blue
    
    foreach ($template in $Global:Templates.templates.PSObject.Properties) {
        $templateData = $template.Value
        Write-Host "`n📋 $($template.Name)" -ForegroundColor Cyan
        Write-Host "   Name: $($templateData.name)" -ForegroundColor White
        Write-Host "   Description: $($templateData.description)" -ForegroundColor Gray
        Write-Host "   Type: $($templateData.template.type)" -ForegroundColor Yellow
    }
    
    Write-Host "`n💡 Usage: .\Create-MCPServer.ps1 -TemplateName <template-name>" -ForegroundColor Green
}

function Show-TemplateSelector {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Select MCP Server Template"
    $form.Size = New-Object System.Drawing.Size(600, 500)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    
    # Header
    $headerLabel = New-Object System.Windows.Forms.Label
    $headerLabel.Text = "🎯 Choose a Template for Your MCP Server"
    $headerLabel.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
    $headerLabel.ForeColor = [System.Drawing.Color]::FromArgb(25, 118, 210)
    $headerLabel.TextAlign = "MiddleCenter"
    $headerLabel.Location = New-Object System.Drawing.Point(20, 20)
    $headerLabel.Size = New-Object System.Drawing.Size(560, 30)
    $form.Controls.Add($headerLabel)
    
    # Template list
    $listBox = New-Object System.Windows.Forms.ListBox
    $listBox.Location = New-Object System.Drawing.Point(20, 70)
    $listBox.Size = New-Object System.Drawing.Size(350, 300)
    $listBox.Font = New-Object System.Drawing.Font("Segoe UI", 10)
    
    foreach ($template in $Global:Templates.templates.PSObject.Properties) {
        $listBox.Items.Add($template.Name) | Out-Null
    }
    
    $form.Controls.Add($listBox)
    
    # Description panel
    $descPanel = New-Object System.Windows.Forms.Panel
    $descPanel.Location = New-Object System.Drawing.Point(390, 70)
    $descPanel.Size = New-Object System.Drawing.Size(180, 300)
    $descPanel.BorderStyle = "FixedSingle"
    $form.Controls.Add($descPanel)
    
    $descLabel = New-Object System.Windows.Forms.Label
    $descLabel.Text = "Select a template to see details"
    $descLabel.Location = New-Object System.Drawing.Point(10, 10)
    $descLabel.Size = New-Object System.Drawing.Size(160, 280)
    $descLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $descLabel.ForeColor = [System.Drawing.Color]::Gray
    $descPanel.Controls.Add($descLabel)
    
    # Update description when selection changes
    $listBox.Add_SelectedIndexChanged({
        if ($listBox.SelectedIndex -ge 0) {
            $selectedTemplate = $Global:Templates.templates.($listBox.SelectedItem)
            $descLabel.Text = "$($selectedTemplate.name)`n`n$($selectedTemplate.description)`n`nType: $($selectedTemplate.template.type)"
            $descLabel.ForeColor = [System.Drawing.Color]::Black
        }
    })
    
    # Buttons
    $selectButton = New-Object System.Windows.Forms.Button
    $selectButton.Text = "Select Template"
    $selectButton.Location = New-Object System.Drawing.Point(450, 400)
    $selectButton.Size = New-Object System.Drawing.Size(120, 30)
    $selectButton.BackColor = [System.Drawing.Color]::FromArgb(76, 175, 80)
    $selectButton.ForeColor = [System.Drawing.Color]::White
    $selectButton.Add_Click({
        if ($listBox.SelectedIndex -ge 0) {
            $form.Tag = $listBox.SelectedItem
            $form.DialogResult = "OK"
            $form.Close()
        }
    })
    $form.Controls.Add($selectButton)
    
    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Text = "Cancel"
    $cancelButton.Location = New-Object System.Drawing.Point(320, 400)
    $cancelButton.Size = New-Object System.Drawing.Size(100, 30)
    $cancelButton.Add_Click({
        $form.DialogResult = "Cancel"
        $form.Close()
    })
    $form.Controls.Add($cancelButton)
    
    $result = $form.ShowDialog()
    $selectedTemplate = $form.Tag
    $form.Dispose()
    
    if ($result -eq "OK") {
        return $selectedTemplate
    } else {
        return $null
    }
}

function Get-TemplateValues {
    param(
        [string]$TemplateName,
        [object]$TemplateData
    )
    
    $values = @{}
    $prompts = $TemplateData.prompts
    
    if ($Interactive) {
        # GUI-based input
        $values = Get-TemplateValuesGUI -TemplateName $TemplateName -Prompts $prompts
    } else {
        # Console-based input
        $values = Get-TemplateValuesConsole -Prompts $prompts
    }
    
    return $values
}

function Get-TemplateValuesConsole {
    param([array]$Prompts)
    
    $values = @{}
    
    Write-Host "`n📝 Please provide the following information:" -ForegroundColor Cyan
    
    foreach ($prompt in $Prompts) {
        # Skip conditional prompts if condition not met
        if ($prompt.condition -and -not $values.ContainsKey($prompt.condition)) {
            continue
        }
        
        $promptText = $prompt.prompt
        if ($prompt.default) {
            $promptText += " (default: $($prompt.default))"
        }
        if ($prompt.optional) {
            $promptText += " (optional)"
        }
        
        # Show options if available
        if ($prompt.options) {
            Write-Host "`nOptions: $($prompt.options -join ', ')" -ForegroundColor Yellow
        }
        
        do {
            $value = Read-Host $promptText
            
            # Use default if empty and default exists
            if ([string]::IsNullOrEmpty($value) -and $prompt.default) {
                $value = $prompt.default
            }
            
            # Skip if optional and empty
            if ([string]::IsNullOrEmpty($value) -and $prompt.optional) {
                break
            }
            
            # Validate if pattern exists
            if ($prompt.validation -and $value -notmatch $prompt.validation) {
                Write-Host "❌ Invalid format. Please try again." -ForegroundColor Red
                continue
            }
            
            # Validate options
            if ($prompt.options -and $value -notin $prompt.options) {
                Write-Host "❌ Please choose from: $($prompt.options -join ', ')" -ForegroundColor Red
                continue
            }
            
            break
        } while ($true)
        
        if (-not [string]::IsNullOrEmpty($value)) {
            $values[$prompt.key] = $value
        }
    }
    
    return $values
}

function Get-TemplateValuesGUI {
    param(
        [string]$TemplateName,
        [array]$Prompts
    )
    
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Configure MCP Server - $TemplateName"
    $form.Size = New-Object System.Drawing.Size(500, 600)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    
    # Scrollable panel
    $scrollPanel = New-Object System.Windows.Forms.Panel
    $scrollPanel.Location = New-Object System.Drawing.Point(10, 10)
    $scrollPanel.Size = New-Object System.Drawing.Size(460, 500)
    $scrollPanel.AutoScroll = $true
    $scrollPanel.BorderStyle = "FixedSingle"
    $form.Controls.Add($scrollPanel)
    
    $controls = @{}
    $y = 10
    
    foreach ($prompt in $Prompts) {
        # Label
        $label = New-Object System.Windows.Forms.Label
        $label.Text = $prompt.prompt
        $label.Location = New-Object System.Drawing.Point(10, $y)
        $label.Size = New-Object System.Drawing.Size(420, 20)
        $label.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $scrollPanel.Controls.Add($label)
        $y += 25
        
        # Input control
        if ($prompt.options) {
            # ComboBox for options
            $combo = New-Object System.Windows.Forms.ComboBox
            $combo.Location = New-Object System.Drawing.Point(10, $y)
            $combo.Size = New-Object System.Drawing.Size(420, 25)
            $combo.DropDownStyle = "DropDownList"
            $combo.Items.AddRange($prompt.options)
            if ($prompt.default) {
                $combo.SelectedItem = $prompt.default
            }
            $scrollPanel.Controls.Add($combo)
            $controls[$prompt.key] = $combo
        } else {
            # TextBox for free text
            $textBox = New-Object System.Windows.Forms.TextBox
            $textBox.Location = New-Object System.Drawing.Point(10, $y)
            $textBox.Size = New-Object System.Drawing.Size(420, 25)
            if ($prompt.default) {
                $textBox.Text = $prompt.default
            }
            $scrollPanel.Controls.Add($textBox)
            $controls[$prompt.key] = $textBox
        }
        
        $y += 35
        
        # Show validation info
        if ($prompt.validation) {
            $validationLabel = New-Object System.Windows.Forms.Label
            $validationLabel.Text = "Format: $($prompt.validation)"
            $validationLabel.Location = New-Object System.Drawing.Point(10, $y)
            $validationLabel.Size = New-Object System.Drawing.Size(420, 15)
            $validationLabel.Font = New-Object System.Drawing.Font("Segoe UI", 8)
            $validationLabel.ForeColor = [System.Drawing.Color]::Gray
            $scrollPanel.Controls.Add($validationLabel)
            $y += 20
        }
        
        $y += 10
    }
    
    # Buttons
    $createButton = New-Object System.Windows.Forms.Button
    $createButton.Text = "Create Server"
    $createButton.Location = New-Object System.Drawing.Point(350, 530)
    $createButton.Size = New-Object System.Drawing.Size(120, 30)
    $createButton.BackColor = [System.Drawing.Color]::FromArgb(76, 175, 80)
    $createButton.ForeColor = [System.Drawing.Color]::White
    $createButton.Add_Click({
        $form.Tag = "OK"
        $form.Close()
    })
    $form.Controls.Add($createButton)
    
    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Text = "Cancel"
    $cancelButton.Location = New-Object System.Drawing.Point(220, 530)
    $cancelButton.Size = New-Object System.Drawing.Size(100, 30)
    $cancelButton.Add_Click({
        $form.Tag = "Cancel"
        $form.Close()
    })
    $form.Controls.Add($cancelButton)
    
    $result = $form.ShowDialog()
    
    $values = @{}
    if ($form.Tag -eq "OK") {
        foreach ($control in $controls.GetEnumerator()) {
            if ($control.Value -is [System.Windows.Forms.ComboBox]) {
                if ($control.Value.SelectedItem) {
                    $values[$control.Key] = $control.Value.SelectedItem.ToString()
                }
            } else {
                if (-not [string]::IsNullOrEmpty($control.Value.Text)) {
                    $values[$control.Key] = $control.Value.Text
                }
            }
        }
    }
    
    $form.Dispose()
    return $values
}

function Expand-Template {
    param(
        [object]$Template,
        [hashtable]$Values
    )
    
    # Convert template to JSON for easier string replacement
    $templateJson = $Template | ConvertTo-Json -Depth 10
    
    # Replace placeholders
    foreach ($value in $Values.GetEnumerator()) {
        $placeholder = "`$`{$($value.Key)"
        $templateJson = $templateJson -replace [regex]::Escape($placeholder) + "[^}]*}", $value.Value
    }
    
    # Handle default values and prompts
    $templateJson = $templateJson -replace '\$\{([^:}]+):([^}]+)\}', '$2'  # Use default values
    $templateJson = $templateJson -replace '\$\{PROMPT:[^}]+\}', '${PROMPT:Enter value}'  # Keep prompts
    
    # Convert back to object
    try {
        $expandedTemplate = $templateJson | ConvertFrom-Json
        return $expandedTemplate
    } catch {
        Write-Host "❌ Failed to expand template: $_" -ForegroundColor Red
        return $null
    }
}

function Save-ServerConfiguration {
    param(
        [object]$ServerConfig,
        [string]$OutputFile
    )
    
    if ([string]::IsNullOrEmpty($OutputFile)) {
        $OutputFile = "new-mcp-server-$($ServerConfig.id).json"
    }
    
    try {
        $ServerConfig | ConvertTo-Json -Depth 10 | Set-Content $OutputFile -Encoding UTF8
        Write-Host "✅ Server configuration saved to: $OutputFile" -ForegroundColor Green
        
        # Ask if user wants to add to main installer
        if ($Interactive) {
            $result = [System.Windows.Forms.MessageBox]::Show(
                "Server configuration created successfully!`n`nWould you like to add this server to the main installer catalog?",
                "Add to Installer",
                [System.Windows.Forms.MessageBoxButtons]::YesNo,
                [System.Windows.Forms.MessageBoxIcon]::Question
            )
            
            if ($result -eq "Yes") {
                Add-ToMainCatalog -ServerConfig $ServerConfig
            }
        } else {
            $response = Read-Host "Add this server to the main installer catalog? (y/n)"
            if ($response -eq 'y') {
                Add-ToMainCatalog -ServerConfig $ServerConfig
            }
        }
        
        return $true
    } catch {
        Write-Host "❌ Failed to save configuration: $_" -ForegroundColor Red
        return $false
    }
}

function Add-ToMainCatalog {
    param([object]$ServerConfig)
    
    $catalogPath = Join-Path $PSScriptRoot "mcp-servers-config.json"
    
    try {
        # Load existing catalog
        $catalog = Get-Content $catalogPath | ConvertFrom-Json
        
        # Check for duplicates
        $existing = $catalog.servers | Where-Object { $_.id -eq $ServerConfig.id }
        if ($existing) {
            Write-Host "⚠️ Server with ID '$($ServerConfig.id)' already exists" -ForegroundColor Yellow
            return $false
        }
        
        # Add new server
        $catalog.servers += $ServerConfig
        
        # Save updated catalog
        $catalog | ConvertTo-Json -Depth 10 | Set-Content $catalogPath -Encoding UTF8
        
        Write-Host "✅ Server added to main installer catalog!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to add to main catalog: $_" -ForegroundColor Red
        return $false
    }
}

function Show-ServerPreview {
    param([object]$ServerConfig)
    
    Write-Host "`n📋 Server Configuration Preview" -ForegroundColor Blue
    Write-Host "===============================" -ForegroundColor Blue
    Write-Host "ID: $($ServerConfig.id)" -ForegroundColor Cyan
    Write-Host "Name: $($ServerConfig.name)" -ForegroundColor White
    Write-Host "Description: $($ServerConfig.description)" -ForegroundColor Gray
    Write-Host "Category: $($ServerConfig.category)" -ForegroundColor Yellow
    Write-Host "Type: $($ServerConfig.type)" -ForegroundColor Yellow
    
    if ($ServerConfig.installation) {
        Write-Host "`nInstallation:" -ForegroundColor Cyan
        Write-Host "  Command: $($ServerConfig.installation.command)" -ForegroundColor White
        Write-Host "  Args: $($ServerConfig.installation.args -join ' ')" -ForegroundColor White
        
        if ($ServerConfig.installation.env) {
            Write-Host "  Environment:" -ForegroundColor White
            foreach ($env in $ServerConfig.installation.env.PSObject.Properties) {
                Write-Host "    $($env.Name): $($env.Value)" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host "`nSupported IDEs: $($ServerConfig.supported_ides -join ', ')" -ForegroundColor Cyan
    Write-Host "Prerequisites: $($ServerConfig.prerequisites -join ', ')" -ForegroundColor Cyan
    Write-Host "Requires Docker: $($ServerConfig.requires_docker)" -ForegroundColor Cyan
}

# Main execution
Write-Host "🛠️ MCP Server Creator" -ForegroundColor Blue

# Load templates
if (-not (Load-Templates)) {
    exit 1
}

if ($ListTemplates) {
    Show-TemplateList
    exit 0
}

# Select template
if ([string]::IsNullOrEmpty($TemplateName)) {
    if ($Interactive) {
        $TemplateName = Show-TemplateSelector
        if (-not $TemplateName) {
            Write-Host "👋 Cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "❌ Template name required. Use -ListTemplates to see available templates." -ForegroundColor Red
        exit 1
    }
}

# Validate template
if (-not $Global:Templates.templates.$TemplateName) {
    Write-Host "❌ Template '$TemplateName' not found. Use -ListTemplates to see available templates." -ForegroundColor Red
    exit 1
}

$templateData = $Global:Templates.templates.$TemplateName

Write-Host "`n🎯 Using template: $($templateData.name)" -ForegroundColor Green
Write-Host "Description: $($templateData.description)" -ForegroundColor Gray

# Get values from user
$values = Get-TemplateValues -TemplateName $TemplateName -TemplateData $templateData

if ($values.Count -eq 0) {
    Write-Host "❌ No values provided. Exiting." -ForegroundColor Red
    exit 1
}

# Expand template
$serverConfig = Expand-Template -Template $templateData.template -Values $values

if (-not $serverConfig) {
    exit 1
}

# Show preview
Show-ServerPreview -ServerConfig $serverConfig

# Save configuration
if (Save-ServerConfiguration -ServerConfig $serverConfig -OutputFile $OutputFile) {
    Write-Host "`n🎉 MCP Server configuration created successfully!" -ForegroundColor Green
    Write-Host "You can now use this server in the MCP installer." -ForegroundColor Cyan
} else {
    exit 1
}
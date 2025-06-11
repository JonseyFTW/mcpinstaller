# Quick syntax test for main PowerShell files
try {
    # Test System-Checker.ps1
    $content = Get-Content "System-Checker.ps1" -Raw
    $tokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseInput($content, [ref]$tokens, [ref]$parseErrors)
    
    if ($parseErrors.Count -gt 0) {
        Write-Host "[X] System-Checker.ps1 has $($parseErrors.Count) syntax errors:" -ForegroundColor Red
        foreach ($error in $parseErrors) {
            Write-Host "  Line $($error.Extent.StartLineNumber): $($error.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "[+] System-Checker.ps1 syntax is valid" -ForegroundColor Green
    }
    
    # Test Setup-Wizard.ps1
    $content = Get-Content "Setup-Wizard.ps1" -Raw
    $tokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseInput($content, [ref]$tokens, [ref]$parseErrors)
    
    if ($parseErrors.Count -gt 0) {
        Write-Host "[X] Setup-Wizard.ps1 has $($parseErrors.Count) syntax errors:" -ForegroundColor Red
        foreach ($error in $parseErrors) {
            Write-Host "  Line $($error.Extent.StartLineNumber): $($error.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "[+] Setup-Wizard.ps1 syntax is valid" -ForegroundColor Green
    }
    
} catch {
    Write-Host "[!] Error testing syntax: $($_.Exception.Message)" -ForegroundColor Yellow
}
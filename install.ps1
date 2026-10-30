# Multi-Agent Installer for improve and improve-all
# Supports Antigravity, Claude Code, Cursor, and Continue.dev with slash command preview (/improve, /improve-all)
param (
    [ValidateSet("Antigravity", "Claude", "Cursor", "Continue", "All")]
    [string]$Target = "All",
    [switch]$Workspace
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$UserHome = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
$CurrentDir = Get-Location

function Install-SkillFiles($DestinationDir, $SkillName) {
    if (Test-Path $DestinationDir) {
        Remove-Item -Recurse -Force $DestinationDir
    }
    New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null
    Copy-Item -Recurse -Path (Join-Path $ScriptDir "references") -Destination $DestinationDir
    Copy-Item -Recurse -Path (Join-Path $ScriptDir "scripts") -Destination $DestinationDir
    $Pycache = Join-Path $DestinationDir "scripts\__pycache__"
    if (Test-Path $Pycache) { Remove-Item -Recurse -Force $Pycache }
    if (Test-Path (Join-Path $ScriptDir "LICENSE")) {
        Copy-Item -Path (Join-Path $ScriptDir "LICENSE") -Destination $DestinationDir
    }
    if ($SkillName -eq "improve-all") {
        Copy-Item -Force (Join-Path $ScriptDir "skills\improve-all\SKILL.md") (Join-Path $DestinationDir "SKILL.md")
    } else {
        Copy-Item -Force (Join-Path $ScriptDir "skills\improve\SKILL.md") (Join-Path $DestinationDir "SKILL.md")
    }
}

function Install-Antigravity() {
    Write-Host "[+] Installing for Antigravity..." -ForegroundColor Cyan
    $BaseDir = if ($Workspace) { Join-Path $CurrentDir ".agents\skills" } else { Join-Path $UserHome ".gemini\config\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $BaseDir $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered skill: $Dest" -ForegroundColor Green
    }
}

function Install-Claude() {
    Write-Host "[+] Installing for Claude Code..." -ForegroundColor Cyan
    # 1. Claude Skills
    $SkillBase = if ($Workspace) { Join-Path $CurrentDir ".claude\skills" } else { Join-Path $UserHome ".claude\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $SkillBase $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered Claude Skill: $Dest" -ForegroundColor Green
    }
    # 2. Claude Commands (/ autocomplete preview)
    $CmdBase = if ($Workspace) { Join-Path $CurrentDir ".claude\commands" } else { Join-Path $UserHome ".claude\commands" }
    New-Item -ItemType Directory -Path $CmdBase -Force | Out-Null
    Copy-Item -Force (Join-Path $ScriptDir "integrations\claude\commands\improve.md") (Join-Path $CmdBase "improve.md")
    Copy-Item -Force (Join-Path $ScriptDir "integrations\claude\commands\improve-all.md") (Join-Path $CmdBase "improve-all.md")
    Write-Host "    ✓ Registered Claude Slash Commands in: $CmdBase" -ForegroundColor Green
}

function Install-Cursor() {
    Write-Host "[+] Installing for Cursor IDE..." -ForegroundColor Cyan
    $CmdBase = if ($Workspace) { Join-Path $CurrentDir ".cursor\commands" } else { Join-Path $UserHome ".cursor\commands" }
    New-Item -ItemType Directory -Path $CmdBase -Force | Out-Null
    Copy-Item -Force (Join-Path $ScriptDir "integrations\cursor\commands\improve.md") (Join-Path $CmdBase "improve.md")
    Copy-Item -Force (Join-Path $ScriptDir "integrations\cursor\commands\improve-all.md") (Join-Path $CmdBase "improve-all.md")
    Write-Host "    ✓ Registered Cursor Slash Commands in: $CmdBase" -ForegroundColor Green
}

function Install-Continue() {
    Write-Host "[+] Installing for Continue.dev..." -ForegroundColor Cyan
    $ConfigDir = if ($Workspace) { Join-Path $CurrentDir ".continue" } else { Join-Path $UserHome ".continue" }
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    $ConfigFile = Join-Path $ConfigDir "config.json"
    
    $SourceCommands = (Get-Content (Join-Path $ScriptDir "integrations\continue\config.json") -Raw | ConvertFrom-Json).customCommands
    
    if (Test-Path $ConfigFile) {
        try {
            $ExistingJson = Get-Content $ConfigFile -Raw | ConvertFrom-Json
            if (-not $ExistingJson.customCommands) {
                $ExistingJson | Add-Member -MemberType NoteProperty -Name "customCommands" -Value @()
            }
            # Remove existing improve / improve-all
            $Filtered = @($ExistingJson.customCommands | Where-Object { $_.name -ne "improve" -and $_.name -ne "improve-all" })
            $Filtered += $SourceCommands
            $ExistingJson.customCommands = $Filtered
            $ExistingJson | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile -Encoding UTF8
            Write-Host "    ✓ Merged into: $ConfigFile" -ForegroundColor Green
        } catch {
            Copy-Item -Force (Join-Path $ScriptDir "integrations\continue\config.json") $ConfigFile
            Write-Host "    ✓ Created: $ConfigFile" -ForegroundColor Green
        }
    } else {
        Copy-Item -Force (Join-Path $ScriptDir "integrations\continue\config.json") $ConfigFile
        Write-Host "    ✓ Created: $ConfigFile" -ForegroundColor Green
    }
}

# Execution
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host "Codebase Audit & Improve: Multi-Agent Installer" -ForegroundColor Yellow
Write-Host "Target: $Target | Mode: $(if ($Workspace) { 'Workspace' } else { 'Global' })" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Yellow

if ($Target -eq "All" -or $Target -eq "Antigravity") { Install-Antigravity }
if ($Target -eq "All" -or $Target -eq "Claude")      { Install-Claude }
if ($Target -eq "All" -or $Target -eq "Cursor")      { Install-Cursor }
if ($Target -eq "All" -or $Target -eq "Continue")    { Install-Continue }

Write-Host "`nAll selected slash commands and skills have been successfully installed!" -ForegroundColor Green
Write-Host "You can now type '/' in Antigravity, Claude Code, Cursor, or Continue to preview and autocomplete /improve and /improve-all." -ForegroundColor Yellow

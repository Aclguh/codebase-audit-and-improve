# Multi-Agent Installer for improve and improve-all
# Supports Antigravity, Claude Code, Cursor, Continue.dev, DeepSeek Harness (dsh), and OpenAI Codex
# Deduplicated & clean: ensures each agent sees exactly ONE /improve and ONE /improve-all entry
param (
    [ValidateSet("Antigravity", "Claude", "Cursor", "Continue", "DeepSeek", "Codex", "All")]
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

function Cleanup-Legacy-Duplicates() {
    # Remove redundant legacy commands that cause duplicate slash commands in Claude Code
    $LegacyClaudeCmd = Join-Path $UserHome ".claude\commands"
    if (Test-Path (Join-Path $LegacyClaudeCmd "improve.md")) { Remove-Item -Force (Join-Path $LegacyClaudeCmd "improve.md") }
    if (Test-Path (Join-Path $LegacyClaudeCmd "improve-all.md")) { Remove-Item -Force (Join-Path $LegacyClaudeCmd "improve-all.md") }
    if ((Test-Path $LegacyClaudeCmd) -and (Get-ChildItem $LegacyClaudeCmd).Count -eq 0) {
        Remove-Item -Recurse -Force $LegacyClaudeCmd -ErrorAction SilentlyContinue
    }
    
    # Remove global ~/.cursor/commands (which Claude Code auto-scans and duplicates)
    $LegacyCursorCmd = Join-Path $UserHome ".cursor\commands"
    if (Test-Path (Join-Path $LegacyCursorCmd "improve.md")) { Remove-Item -Force (Join-Path $LegacyCursorCmd "improve.md") }
    if (Test-Path (Join-Path $LegacyCursorCmd "improve-all.md")) { Remove-Item -Force (Join-Path $LegacyCursorCmd "improve-all.md") }
    if ((Test-Path $LegacyCursorCmd) -and (Get-ChildItem $LegacyCursorCmd).Count -eq 0) {
        Remove-Item -Recurse -Force $LegacyCursorCmd -ErrorAction SilentlyContinue
    }
}

function Install-Antigravity() {
    Write-Host "[+] Installing for Antigravity..." -ForegroundColor Cyan
    $BaseDir = if ($Workspace) { Join-Path $CurrentDir ".agents\skills" } else { Join-Path $UserHome ".gemini\config\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $BaseDir $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered Antigravity Skill: $Dest" -ForegroundColor Green
    }
}

function Install-Claude() {
    Write-Host "[+] Installing for Claude Code..." -ForegroundColor Cyan
    $SkillBase = if ($Workspace) { Join-Path $CurrentDir ".claude\skills" } else { Join-Path $UserHome ".claude\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $SkillBase $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered Claude Skill: $Dest" -ForegroundColor Green
    }
}

function Install-Cursor() {
    Write-Host "[+] Installing for Cursor IDE..." -ForegroundColor Cyan
    if ($Workspace) {
        $CmdBase = Join-Path $CurrentDir ".cursor\commands"
        New-Item -ItemType Directory -Path $CmdBase -Force | Out-Null
        Copy-Item -Force (Join-Path $ScriptDir "templates\cursor\improve.md") (Join-Path $CmdBase "improve.md")
        Copy-Item -Force (Join-Path $ScriptDir "templates\cursor\improve-all.md") (Join-Path $CmdBase "improve-all.md")
        Write-Host "    ✓ Registered Workspace Cursor Commands in: $CmdBase" -ForegroundColor Green
    } else {
        # Global Cursor rules
        $RulesBase = Join-Path $UserHome ".cursor\rules"
        New-Item -ItemType Directory -Path $RulesBase -Force | Out-Null
        Copy-Item -Force (Join-Path $ScriptDir "templates\cursor\improve.md") (Join-Path $RulesBase "improve.mdc")
        Copy-Item -Force (Join-Path $ScriptDir "templates\cursor\improve-all.md") (Join-Path $RulesBase "improve-all.mdc")
        Write-Host "    ✓ Registered Global Cursor Rules in: $RulesBase" -ForegroundColor Green
    }
}

function Install-Continue() {
    Write-Host "[+] Installing for Continue.dev..." -ForegroundColor Cyan
    $ConfigDir = if ($Workspace) { Join-Path $CurrentDir ".continue" } else { Join-Path $UserHome ".continue" }
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    $ConfigFile = Join-Path $ConfigDir "config.json"
    
    $SourceCommands = (Get-Content (Join-Path $ScriptDir "templates\continue\config.json") -Raw | ConvertFrom-Json).customCommands
    
    if (Test-Path $ConfigFile) {
        try {
            $ExistingJson = Get-Content $ConfigFile -Raw | ConvertFrom-Json
            if (-not $ExistingJson.customCommands) {
                $ExistingJson | Add-Member -MemberType NoteProperty -Name "customCommands" -Value @()
            }
            $Filtered = @($ExistingJson.customCommands | Where-Object { $_.name -ne "improve" -and $_.name -ne "improve-all" })
            $Filtered += $SourceCommands
            $ExistingJson.customCommands = $Filtered
            $ExistingJson | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile -Encoding UTF8
            Write-Host "    ✓ Merged into: $ConfigFile" -ForegroundColor Green
        } catch {
            Copy-Item -Force (Join-Path $ScriptDir "templates\continue\config.json") $ConfigFile
            Write-Host "    ✓ Created: $ConfigFile" -ForegroundColor Green
        }
    } else {
        Copy-Item -Force (Join-Path $ScriptDir "templates\continue\config.json") $ConfigFile
        Write-Host "    ✓ Created: $ConfigFile" -ForegroundColor Green
    }
}

function Install-DeepSeek() {
    Write-Host "[+] Installing for DeepSeek Harness (dsh)..." -ForegroundColor Cyan
    $BaseDir = if ($Workspace) { Join-Path $CurrentDir ".agents\skills" } else { Join-Path $UserHome ".agents\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $BaseDir $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered DeepSeek Harness Skill: $Dest" -ForegroundColor Green
    }
}

function Install-Codex() {
    Write-Host "[+] Installing for OpenAI Codex..." -ForegroundColor Cyan
    $BaseDir = if ($Workspace) { Join-Path $CurrentDir ".codex\skills" } else { Join-Path $UserHome ".codex\skills" }
    foreach ($Name in @("improve", "improve-all")) {
        $Dest = Join-Path $BaseDir $Name
        Install-SkillFiles $Dest $Name
        Write-Host "    ✓ Registered Codex Skill: $Dest" -ForegroundColor Green
    }
}

# Cleanup duplicates first
Cleanup-Legacy-Duplicates

# Execution
Write-Host "=================================================" -ForegroundColor Yellow
Write-Host "Codebase Audit & Improve: Multi-Agent Installer" -ForegroundColor Yellow
Write-Host "Target: $Target | Mode: $(if ($Workspace) { 'Workspace' } else { 'Global' })" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Yellow

if ($Target -eq "All" -or $Target -eq "Antigravity") { Install-Antigravity }
if ($Target -eq "All" -or $Target -eq "Claude")      { Install-Claude }
if ($Target -eq "All" -or $Target -eq "Cursor")      { Install-Cursor }
if ($Target -eq "All" -or $Target -eq "Continue")    { Install-Continue }
if ($Target -eq "All" -or $Target -eq "DeepSeek")    { Install-DeepSeek }
if ($Target -eq "All" -or $Target -eq "Codex")       { Install-Codex }

Write-Host "`nAll selected slash commands and skills have been cleanly installed without duplicates!" -ForegroundColor Green
Write-Host "Ready for Antigravity, Claude Code, Cursor, Continue, DeepSeek Harness, and Codex." -ForegroundColor Yellow

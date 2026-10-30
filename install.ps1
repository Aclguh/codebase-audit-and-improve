# Windows Quick Installer for codebase-audit-and-improve skill
param (
    [switch]$Workspace
)

$SkillName = "codebase-audit-and-improve"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Workspace) {
    $TargetDir = Join-Path (Get-Location) ".agents\skills\$SkillName"
} else {
    $UserHome = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
    $TargetDir = Join-Path $UserHome ".gemini\config\skills\$SkillName"
}

Write-Host "Installing $SkillName into: $TargetDir" -ForegroundColor Cyan

if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}

New-Item -ItemType Directory -Path (Split-Path -Parent $TargetDir) -Force | Out-Null
Copy-Item -Recurse -Path $ScriptDir -Destination $TargetDir -Exclude ".git"

Write-Host "✓ Successfully installed $SkillName!" -ForegroundColor Green
Write-Host "Restart your agent session or reload workspace to activate." -ForegroundColor Yellow

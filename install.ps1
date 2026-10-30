# Windows Quick Installer for improve and improve-all skills
param (
    [switch]$Workspace
)

$Skills = @("improve", "improve-all")
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Workspace) {
    $BaseDir = Join-Path (Get-Location) ".agents\skills"
} else {
    $UserHome = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
    $BaseDir = Join-Path $UserHome ".gemini\config\skills"
}

foreach ($SkillName in $Skills) {
    $TargetDir = Join-Path $BaseDir $SkillName
    Write-Host "Installing $SkillName into: $TargetDir" -ForegroundColor Cyan

    if (Test-Path $TargetDir) {
        Remove-Item -Recurse -Force $TargetDir
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $TargetDir) -Force | Out-Null
    Copy-Item -Recurse -Path $ScriptDir -Destination $TargetDir -Exclude ".git"

    if ($SkillName -eq "improve-all") {
        Copy-Item -Force (Join-Path $ScriptDir "skills\improve-all\SKILL.md") (Join-Path $TargetDir "SKILL.md")
    } else {
        Copy-Item -Force (Join-Path $ScriptDir "skills\improve\SKILL.md") (Join-Path $TargetDir "SKILL.md")
    }
}

Write-Host "Successfully installed improve and improve-all!" -ForegroundColor Green
Write-Host "Restart your agent session or reload workspace to activate (/improve and /improve-all)." -ForegroundColor Yellow

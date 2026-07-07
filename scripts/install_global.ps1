<#
.SYNOPSIS
Links the local skills and rules to the global AGY directory on Windows.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$RequirementsPath = Join-Path -Path $RepoRoot -ChildPath "requirements.txt"

Write-Host "Installing Python dependencies..."
if (Get-Command pip -ErrorAction SilentlyContinue) {
    try {
        $process = Start-Process -FilePath pip -ArgumentList "install", "-r", "`"$RequirementsPath`"" -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -ne 0) {
            Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
            Write-Host "Please download and install Python and pip from https://www.python.org/downloads/ and try again." -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
        Write-Host "Please download and install Python and pip from https://www.python.org/downloads/ and try again." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Error: pip not found." -ForegroundColor Red
    Write-Host "Please download and install Python and pip from https://www.python.org/downloads/ and try again." -ForegroundColor Yellow
    exit 1
}

$AgyDir = Join-Path -Path $env:USERPROFILE -ChildPath ".gemini\antigravity-cli"
$SkillsDir = Join-Path -Path $AgyDir -ChildPath "skills"
$RulesDir = Join-Path -Path $AgyDir -ChildPath "rules"

if (-not (Test-Path -Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir | Out-Null
}
if (-not (Test-Path -Path $RulesDir)) {
    New-Item -ItemType Directory -Path $RulesDir | Out-Null
}

$SourceSkills = Join-Path -Path $RepoRoot -ChildPath ".agents\skills"
$SourceRules = Join-Path -Path $RepoRoot -ChildPath ".agents\rules"

Write-Host "Linking skills to global AGY configuration"
if (Test-Path -Path $SourceSkills) {
    Get-ChildItem -Path $SourceSkills -Directory | ForEach-Object {
        $Target = Join-Path -Path $SkillsDir -ChildPath $_.Name
        if (Test-Path -Path $Target) {
            Remove-Item -Path $Target -Recurse -Force
        }
        New-Item -ItemType Junction -Path $Target -Value $_.FullName | Out-Null
    }
}

Write-Host "Linking rules to global AGY configuration"
if (Test-Path -Path $SourceRules) {
    Get-ChildItem -Path $SourceRules -File | ForEach-Object {
        $Target = Join-Path -Path $RulesDir -ChildPath $_.Name
        if (Test-Path -Path $Target) {
            Remove-Item -Path $Target -Force
        }
        New-Item -ItemType HardLink -Path $Target -Value $_.FullName | Out-Null
    }
}

Write-Host "Integration complete. Your AI Knowledge Library is now globally accessible."

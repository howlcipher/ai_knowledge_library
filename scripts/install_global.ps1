<#
.SYNOPSIS
Links the local skills and rules to the global Gemini (AGY) and Claude Code directories on Windows.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "Installing Python dependencies..."
if (Get-Command pip -ErrorAction SilentlyContinue) {
    try {
        $process = Start-Process -FilePath pip -ArgumentList "install", "`"$RepoRoot`"" -Wait -PassThru -NoNewWindow
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

$SourceSkills = Join-Path -Path $RepoRoot -ChildPath ".agents\skills"
$SourceSkillCommands = Join-Path -Path $RepoRoot -ChildPath ".agents\skill_commands"
$SourceRules = Join-Path -Path $RepoRoot -ChildPath ".agents\rules"

function Link-Skills {
    param([string]$SourceDir, [string]$TargetDir)

    if (-not (Test-Path -Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir | Out-Null
    }
    if (Test-Path -Path $SourceDir) {
        Get-ChildItem -Path $SourceDir -Directory | ForEach-Object {
            $Target = Join-Path -Path $TargetDir -ChildPath $_.Name
            if (Test-Path -Path $Target) {
                Remove-Item -Path $Target -Recurse -Force
            }
            New-Item -ItemType Junction -Path $Target -Value $_.FullName | Out-Null
        }
    }
}

# --- Gemini / Antigravity (AGY) integration ---
$AgyDir = Join-Path -Path $env:USERPROFILE -ChildPath ".gemini\antigravity-cli"
$RulesDir = Join-Path -Path $AgyDir -ChildPath "rules"

Write-Host "Linking skills to global AGY configuration"
Link-Skills -SourceDir $SourceSkills -TargetDir (Join-Path -Path $AgyDir -ChildPath "skills")

if (-not (Test-Path -Path $RulesDir)) {
    New-Item -ItemType Directory -Path $RulesDir | Out-Null
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

# --- Claude Code integration ---
$ClaudeDir = Join-Path -Path $env:USERPROFILE -ChildPath ".claude"

Write-Host "Linking skills to global Claude Code configuration"
Link-Skills -SourceDir $SourceSkills -TargetDir (Join-Path -Path $ClaudeDir -ChildPath "skills")

Write-Host "Linking command skills (/work_next_item, /resume_task, /groom_backlogs) to global Claude Code configuration"
Link-Skills -SourceDir $SourceSkillCommands -TargetDir (Join-Path -Path $ClaudeDir -ChildPath "skills")

Write-Host "Registering library rulebook in global Claude memory"
$ClaudeMemory = Join-Path -Path $ClaudeDir -ChildPath "CLAUDE.md"
$MarkerStart = "<!-- ai_knowledge_library:start -->"
$MarkerEnd = "<!-- ai_knowledge_library:end -->"
$ImportLine = "@" + (Join-Path -Path $RepoRoot -ChildPath "AGENTS.md")
$Block = "$MarkerStart`n$ImportLine`n$MarkerEnd"

if (Test-Path -Path $ClaudeMemory) {
    $Content = Get-Content -Path $ClaudeMemory -Raw
    if ($Content -match [regex]::Escape($MarkerStart)) {
        $Pattern = [regex]::Escape($MarkerStart) + "[\s\S]*?" + [regex]::Escape($MarkerEnd)
        $Content = [regex]::Replace($Content, $Pattern, $Block)
        Set-Content -Path $ClaudeMemory -Value $Content
    } else {
        Add-Content -Path $ClaudeMemory -Value "`n$Block"
    }
} else {
    Set-Content -Path $ClaudeMemory -Value $Block
}

Write-Host "Integration complete. Your AI Knowledge Library is now globally accessible to Gemini and Claude."

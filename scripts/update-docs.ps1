param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$false)]
    [string]$ReleaseDate = (Get-Date -Format "yyyy-MM-dd"),
    
    [Parameter(Mandatory=$false)]
    [switch]$UpdateManual,
    
    [Parameter(Mandatory=$false)]
    [switch]$UpdateChangelog,
    
    [Parameter(Mandatory=$false)]
    [string]$ChangeType = "fix",
    
    [Parameter(Mandatory=$false)]
    [string[]]$Changes = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoCommit
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

Write-Host "Starting document update for version: $Version" -ForegroundColor Cyan

# Update CHANGELOG.md
if ($UpdateChangelog -or -not $UpdateManual) {
    Write-Host "Updating CHANGELOG.md..." -ForegroundColor Yellow
    
    $ChangelogPath = Join-Path $ProjectRoot "CHANGELOG.md"
    $Changelog = Get-Content $ChangelogPath -Raw -Encoding UTF8
    
    if ($Changelog -match "## \[$Version\]") {
        Write-Host "Warning: Version $Version already exists" -ForegroundColor Yellow
    } else {
        $TypeMap = @{
            "feat" = "### New Features"
            "fix" = "### Bug Fixes"
            "perf" = "### Performance Improvements"
            "refactor" = "### Code Refactoring"
            "docs" = "### Documentation"
        }
        
        $NewEntry = "## [$Version] - $ReleaseDate`n`n"
        if ($TypeMap.ContainsKey($ChangeType)) {
            $NewEntry += "$($TypeMap[$ChangeType])`n`n"
        }
        
        if ($Changes.Count -gt 0) {
            foreach ($change in $Changes) {
                $NewEntry += "- $change`n"
            }
        } else {
            $NewEntry += "- See git commit history`n"
        }
        
        $NewEntry += "`n---`n`n"
        
        $Pattern = "(## \[Unreleased\].*?---`n`n)"
        if ($Changelog -match $Pattern) {
            $Changelog = $Changelog -replace $Pattern, "`$1$NewEntry"
        } else {
            $Changelog = "# Changelog`n`n$NewEntry" + $Changelog
        }
        
        $Changelog | Set-Content $ChangelogPath -Encoding UTF8 -NoNewline
        Write-Host "CHANGELOG.md updated successfully" -ForegroundColor Green
    }
}

# Update USAGE_MANUAL.md
if ($UpdateManual) {
    Write-Host "Updating USAGE_MANUAL.md..." -ForegroundColor Yellow
    
    $ManualPath = Join-Path $ProjectRoot "USAGE_MANUAL.md"
    $Manual = Get-Content $ManualPath -Raw -Encoding UTF8
    
    if ($Manual -match "## Current Version") {
        $Manual = $Manual -replace "## Current Version\s*\*\*v[0-9.]+\*\*", "## Current Version`n`n**$Version** ($ReleaseDate)"
    } else {
        $VersionInfo = "`n### Current Version`n`n**$Version** ($ReleaseDate)`n"
        $Manual = $Manual -replace "(## System Overview.*?### Core Features)", "`$1$VersionInfo"
    }
    
    if ($Changes.Count -gt 0 -and $ChangeType -eq "feat") {
        $NewFeatures = "`n#### v$Version New Features`n`n"
        foreach ($change in $Changes) {
            $NewFeatures += "- $change`n"
        }
        $NewFeatures += "`n"
        $Manual = $Manual -replace "(## Feature Usage Guide)", "`$1$NewFeatures"
    }
    
    $Manual | Set-Content $ManualPath -Encoding UTF8 -NoNewline
    Write-Host "USAGE_MANUAL.md updated successfully" -ForegroundColor Green
}

# Auto commit
if ($AutoCommit) {
    Write-Host "Committing changes to Git..." -ForegroundColor Yellow
    git add CHANGELOG.md USAGE_MANUAL.md
    git commit -m "docs: update documents to version $Version"
    Write-Host "Git commit completed" -ForegroundColor Green
}

Write-Host "`nDocument update completed!" -ForegroundColor Green
Write-Host "Version: $Version" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Rebuild Docker image: docker-compose up -d --build" -ForegroundColor White
Write-Host "  2. Push Docker image: docker push boscotom/bosco-tsang:$Version" -ForegroundColor White
Write-Host "  3. Create Git tag: git tag $Version && git push origin $Version" -ForegroundColor White

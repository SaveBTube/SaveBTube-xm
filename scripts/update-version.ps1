# ===========================================
# Bosco Tsang - 版本号自动更新脚本 (PowerShell)
# 遵循语义化版本规范
# ===========================================

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "=======================================" -ForegroundColor Blue
Write-Host "  Bosco Tsang - 版本更新工具" -ForegroundColor Blue
Write-Host "=======================================" -ForegroundColor Blue
Write-Host ""

# 获取当前版本号（从 main.py）
$mainPyPath = "backend\main.py"
if (Test-Path $mainPyPath) {
    $content = Get-Content $mainPyPath -Raw
    if ($content -match 'version="(\d+\.\d+\.\d+)"') {
        $CURRENT_VERSION = $matches[1]
    } else {
        $CURRENT_VERSION = "0.3.0"
    }
} else {
    $CURRENT_VERSION = "0.3.0"
}

# 解析版本号
$MAJOR, $MINOR, $PATCH = $CURRENT_VERSION -split '\.' | ForEach-Object { [int]$_ }

Write-Host "当前版本: v$CURRENT_VERSION" -ForegroundColor Green
Write-Host ""

# 显示更新类型选项
Write-Host "请选择更新类型：" -ForegroundColor Yellow
Write-Host "  1. 修订号 (PATCH) - Bug 修复 (0.3.0 → 0.3.1)" -ForegroundColor Green
Write-Host "  2. 次版本号 (MINOR) - 新功能 (0.3.0 → 0.4.0)" -ForegroundColor Blue
Write-Host "  3. 主版本号 (MAJOR) - 破坏性变更 (0.3.0 → 1.0.0)" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "输入选项 (1/2/3)"

switch ($choice) {
    "1" {
        $PATCH++
        $UPDATE_TYPE = "PATCH"
    }
    "2" {
        $MINOR++
        $PATCH = 0
        $UPDATE_TYPE = "MINOR"
    }
    "3" {
        $MAJOR++
        $MINOR = 0
        $PATCH = 0
        $UPDATE_TYPE = "MAJOR"
    }
    default {
        Write-Host "❌ 无效选项" -ForegroundColor Red
        exit 1
    }
}

$NEW_VERSION = "$MAJOR.$MINOR.$PATCH"

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "  版本更新确认" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "更新类型: $UPDATE_TYPE" -ForegroundColor Yellow
Write-Host "版本变更: v$CURRENT_VERSION → v$NEW_VERSION" -ForegroundColor Green
Write-Host ""

# 确认更新
$confirm = Read-Host "是否继续？(y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔄 开始更新版本..." -ForegroundColor Green
Write-Host ""

# 1. 更新 backend/main.py 中的版本号
Write-Host "[1/3] 更新 backend/main.py..." -ForegroundColor Blue
if (Test-Path $mainPyPath) {
    $content = Get-Content $mainPyPath -Raw
    $content = $content -replace "version=`"$CURRENT_VERSION`"", "version=`"$NEW_VERSION`""
    $content | Set-Content $mainPyPath -NoNewline
    Write-Host "  ✓ backend/main.py 已更新" -ForegroundColor Green
} else {
    Write-Host "  ⚠ backend/main.py 不存在，跳过" -ForegroundColor Yellow
}

# 2. 更新前端 package.json 中的版本号
Write-Host "[2/3] 更新 frontend/package.json..." -ForegroundColor Blue
$packageJsonPath = "frontend\package.json"
if (Test-Path $packageJsonPath) {
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $packageJson.version = $NEW_VERSION
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
    Write-Host "  ✓ frontend/package.json 已更新" -ForegroundColor Green
} else {
    Write-Host "  ⚠ frontend/package.json 不存在，跳过" -ForegroundColor Yellow
}

# 3. 更新 CHANGELOG.md
Write-Host "[3/3] 更新 CHANGELOG.md..." -ForegroundColor Blue
$changelogPath = "CHANGELOG.md"
if (Test-Path $changelogPath) {
    $TODAY = Get-Date -Format "yyyy-MM-dd"
    $changelog = Get-Content $changelogPath -Raw
    
    # 检查是否已有该版本的标题
    if ($changelog -match "\[v$NEW_VERSION\]") {
        Write-Host "  ⚠ CHANGELOG.md 中已存在 v$NEW_VERSION 标题" -ForegroundColor Yellow
    } else {
        # 在 "[未发布]" 后添加新版本标题
        $changelog = $changelog -replace "## \[未发布\]", "## [未发布]`n`n## [v$NEW_VERSION] - $TODAY"
        $changelog | Set-Content $changelogPath -NoNewline
        Write-Host "  ✓ CHANGELOG.md 已添加 v$NEW_VERSION 标题" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ CHANGELOG.md 不存在，跳过" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "  ✅ 版本更新完成！" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# 显示后续步骤
Write-Host "📝 后续步骤：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. 更新 CHANGELOG.md 中的变更内容"
Write-Host "  2. 提交更改:"
Write-Host "     git add ." -ForegroundColor Blue
Write-Host "     git commit -m `"chore: 版本更新至 v$NEW_VERSION`"" -ForegroundColor Blue
Write-Host "  3. 打标签:"
Write-Host "     git tag v$NEW_VERSION" -ForegroundColor Blue
Write-Host "     git push origin v$NEW_VERSION" -ForegroundColor Blue
Write-Host "  4. 推送代码:"
Write-Host "     git push origin main" -ForegroundColor Blue
Write-Host ""
Write-Host "新版本: v$NEW_VERSION" -ForegroundColor Green

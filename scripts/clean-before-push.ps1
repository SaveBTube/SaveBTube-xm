# ===========================================
# Bosco Tsang - 推送前清理脚本 (PowerShell)
# 过滤敏感信息，确保安全推送
# ===========================================

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "=======================================" -ForegroundColor Blue
Write-Host "  Bosco Tsang - 推送前清理工具" -ForegroundColor Blue
Write-Host "=======================================" -ForegroundColor Blue
Write-Host ""

# 确认操作
Write-Host "⚠️  此操作将清除以下敏感信息：" -ForegroundColor Yellow
Write-Host "  • Cookies 文件内容"
Write-Host "  • 日志文件内容"
Write-Host "  • 测试下载文件"
Write-Host "  • 临时文件"
Write-Host "  • Python 缓存"
Write-Host ""

$confirm = Read-Host "是否继续？(y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🧹 开始清理..." -ForegroundColor Green
Write-Host ""

# 1. 清除 Cookies 文件
Write-Host "[1/6] 清除 Cookies 文件..." -ForegroundColor Blue
if (Test-Path "cookies") {
    Get-ChildItem -Path "cookies" -Filter "*.txt" -File | ForEach-Object {
        Clear-Content -Path $_.FullName
    }
    Write-Host "  ✓ Cookies 文件已清空" -ForegroundColor Green
} else {
    Write-Host "  ⚠ cookies 目录不存在，跳过" -ForegroundColor Yellow
}

# 2. 清除日志文件
Write-Host "[2/6] 清除日志文件..." -ForegroundColor Blue
if (Test-Path "logs") {
    Get-ChildItem -Path "logs" -Filter "*.log" -File | ForEach-Object {
        Clear-Content -Path $_.FullName
    }
    Write-Host "  ✓ 日志文件已清空" -ForegroundColor Green
} else {
    Write-Host "  ⚠ logs 目录不存在，跳过" -ForegroundColor Yellow
}

# 3. 清除测试下载文件
Write-Host "[3/6] 清除测试下载文件..." -ForegroundColor Blue
if (Test-Path "downloads") {
    Get-ChildItem -Path "downloads" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "  ✓ 测试下载文件已删除" -ForegroundColor Green
} else {
    Write-Host "  ⚠ downloads 目录不存在，跳过" -ForegroundColor Yellow
}

# 4. 清除临时文件
Write-Host "[4/6] 清除临时文件..." -ForegroundColor Blue
$tempFiles = Get-ChildItem -Path $env:TEMP -Filter "xtwitter_cookies.txt" -ErrorAction SilentlyContinue
if ($tempFiles) {
    $tempFiles | Remove-Item -Force
}
Write-Host "  ✓ 临时文件已清除" -ForegroundColor Green

# 5. 清除 Python 缓存
Write-Host "[5/6] 清除 Python 缓存..." -ForegroundColor Blue
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Python 缓存已清除" -ForegroundColor Green

# 6. 清除 Node 缓存
Write-Host "[6/6] 清除 Node 缓存..." -ForegroundColor Blue
$nodeCache = "frontend\node_modules\.cache"
if (Test-Path $nodeCache) {
    Remove-Item -Path $nodeCache -Recurse -Force
    Write-Host "  ✓ Node 缓存已清除" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Node 缓存不存在，跳过" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "  ✅ 清理完成！" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# 显示清理后的状态
Write-Host "📊 清理后状态：" -ForegroundColor Blue
Write-Host ""

# 检查 Cookies 文件
if (Test-Path "cookies") {
    $cookieCount = (Get-ChildItem -Path "cookies" -Filter "*.txt" -File).Count
    $cookieSize = (Get-ChildItem -Path "cookies" -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $cookieSizeMB = [math]::Round($cookieSize / 1MB, 2)
    Write-Host "  Cookies: $cookieCount 个文件, 大小: ${cookieSizeMB} MB"
}

# 检查日志文件
if (Test-Path "logs") {
    $logCount = (Get-ChildItem -Path "logs" -Filter "*.log" -File).Count
    $logSize = (Get-ChildItem -Path "logs" -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $logSizeMB = [math]::Round($logSize / 1MB, 2)
    Write-Host "  日志: $logCount 个文件, 大小: ${logSizeMB} MB"
}

# 检查下载文件
if (Test-Path "downloads") {
    $downloadCount = (Get-ChildItem -Path "downloads" -Recurse -File -ErrorAction SilentlyContinue).Count
    $downloadSize = (Get-ChildItem -Path "downloads" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $downloadSizeMB = [math]::Round($downloadSize / 1MB, 2)
    Write-Host "  下载: $downloadCount 个文件, 大小: ${downloadSizeMB} MB"
}

Write-Host ""
Write-Host "⚠️  提醒：" -ForegroundColor Yellow
Write-Host "  • 请检查 .env 文件是否包含敏感信息"
Write-Host "  • 请确认 .gitignore 已正确配置"
Write-Host "  • 建议使用 git status 检查变更"
Write-Host ""
Write-Host "现在可以安全地提交和推送代码了！" -ForegroundColor Green

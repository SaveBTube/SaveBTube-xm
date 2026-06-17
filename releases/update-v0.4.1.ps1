# Update documents for v0.4.1 - iOS Shortcuts One-Click Installation
# 修复快捷指令安装问题，实现一键安装功能

$changes = @(
    "Fix Shortcuts config download 404 error",
    "Add one-click Shortcuts installation page",
    "Implement auto-fill server address",
    "Add API Key form input with validation",
    "Use iOS URL Scheme for direct installation",
    "Optimize mobile UI for installation page"
)

.\scripts\update-docs.ps1 -Version "v0.4.1" -ChangeType "fix" -Changes $changes -UpdateManual

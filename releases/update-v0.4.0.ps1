# Update documents for v0.4.0 - iOS Shortcuts Feature
cd "H:\docker开发文档\BoscoTsang"

$changes = @(
    "Add iOS Shortcuts download feature",
    "Integrate Shortcuts into plugin management page",
    "Add Shortcuts installation page",
    "Add Shortcuts download API",
    "Add Shortcuts documentation"
)

.\scripts\update-docs.ps1 -Version "v0.4.0" -ChangeType "feat" -Changes $changes -UpdateManual

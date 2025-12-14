# PowerShell script to fix trailing whitespace in all project files
# Run this script from the project root directory

Write-Host "Fixing trailing whitespace in all files..." -ForegroundColor Cyan

$extensions = @("*.js", "*.css", "*.py", "*.html", "*.json", "*.yaml", "*.yml", "*.md")
$directories = @("frontend\src", "static", "templates", "store", "config")

$fixedCount = 0

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        foreach ($ext in $extensions) {
            Get-ChildItem -Path $dir -Recurse -Include $ext -ErrorAction SilentlyContinue | ForEach-Object {
                try {
                    $content = Get-Content $_.FullName -Raw -ErrorAction Stop
                    if ($content) {
                        $newContent = $content -replace '[ \t]+(\r?\n)', '$1'
                        if ($content -ne $newContent) {
                            [System.IO.File]::WriteAllText($_.FullName, $newContent)
                            $fixedCount++
                            Write-Host "  Fixed: $($_.FullName)" -ForegroundColor Green
                        }
                    }
                } catch {
                    Write-Host "  Skipped: $($_.FullName)" -ForegroundColor Yellow
                }
            }
        }
    }
}

Write-Host "`nDone! Fixed $fixedCount files." -ForegroundColor Cyan
Write-Host "Run 'trunk check' to verify remaining issues." -ForegroundColor White

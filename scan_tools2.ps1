$files = Get-ChildItem -Path "$env:USERPROFILE\.claude\projects\" -Recurse -Filter "*.jsonl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 50 -ExpandProperty FullName

Write-Host "Found $($files.Count) jsonl files"

$allToolNames = @{}
$totalToolUses = 0

foreach ($file in $files) {
    $lines = Get-Content -Path $file -Encoding UTF8
    foreach ($line in $lines) {
        try {
            $obj = $line | ConvertFrom-Json
        } catch {
            continue
        }

        if ($null -eq $obj.message) { continue }
        if ($null -eq $obj.message.content) { continue }

        $content = $obj.message.content

        foreach ($item in $content) {
            if ($item.type -ne "tool_use") { continue }
            $totalToolUses++
            $toolName = $item.name

            if ($allToolNames.ContainsKey($toolName)) {
                $allToolNames[$toolName]++
            } else {
                $allToolNames[$toolName] = 1
            }
        }
    }
}

Write-Host ""
Write-Host "Total tool_use items: $totalToolUses"
Write-Host ""
Write-Host "=== ALL TOOL NAMES ==="
$allToolNames.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
    "{0,6}  {1}" -f $_.Value, $_.Key
}

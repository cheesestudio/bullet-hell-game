# Find all .jsonl files, sort by LastWriteTime descending, take 50 most recent
$files = Get-ChildItem -Path "$env:USERPROFILE\.claude\projects\" -Recurse -Filter "*.jsonl" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 50 -ExpandProperty FullName

Write-Host "Found $($files.Count) jsonl files to scan"

$bashCounts = @{}
$mcpCounts = @{}
$totalToolUses = 0
$totalLines = 0
$totalAssistantMessages = 0

foreach ($file in $files) {
    $lines = Get-Content -Path $file -Encoding UTF8
    foreach ($line in $lines) {
        $totalLines++
        try {
            $obj = $line | ConvertFrom-Json
        } catch {
            continue
        }

        # Look for assistant messages with content arrays
        if ($null -eq $obj.message) { continue }
        if ($null -eq $obj.message.content) { continue }
        if ($obj.type -ne "assistant") { continue }

        $totalAssistantMessages++
        $content = $obj.message.content

        foreach ($item in $content) {
            if ($item.type -ne "tool_use") { continue }
            $totalToolUses++
            $toolName = $item.name

            if ($toolName -eq "Bash") {
                $command = $item.input.command
                if ($null -eq $command) { continue }

                # Parse the leading command
                $cmd = $command.Trim()

                # Split on && and ; and |, take the first segment
                # First normalize: split on &&, ;, or |
                $segments = $cmd -split '\s*(&&|\|)\s*'
                $firstSegment = $segments[0].Trim()

                # Also handle pipes by splitting on | and taking first part
                $firstSegment = ($firstSegment -split '\|')[0].Trim()

                # Remove env var prefixes like VAR=val
                # Match leading env assignments
                while ($firstSegment -match '^\s*[A-Za-z_][A-Za-z0-9_]*=') {
                    $firstSegment = ($firstSegment -replace '^\s*[A-Za-z_][A-Za-z0-9_]*=[^\s]*\s*', '').Trim()
                }

                # Extract command + first subcommand
                $parts = $firstSegment -split '\s+'
                $parts = $parts | Where-Object { $_ -ne '' }

                if ($parts.Count -eq 0) { continue }

                $baseCmd = $parts[0]

                # For well-known tools that take subcommands, record command + subcommand
                $multiLevelCommands = @('git', 'gh', 'npm', 'npx', 'docker', 'pip', 'cargo', 'kubectl', 'aws', 'gcloud', 'az', 'dotnet', 'yarn', 'pnpm', 'go', 'flutter', 'adb', 'cmake', 'make', 'systemctl', 'journalctl', 'apt', 'apt-get', 'yum', 'dnf', 'brew', 'choco', 'scoop', 'node', 'python', 'python3', 'rails', 'rake', 'bundle', 'gem', 'terraform', 'ansible', 'helm', 'mvn', 'gradle', 'nuget', 'meson', 'ninja')

                if ($multiLevelCommands -contains $baseCmd -and $parts.Count -ge 2) {
                    $key = "$baseCmd $($parts[1])"
                } else {
                    $key = $baseCmd
                }

                if ($bashCounts.ContainsKey($key)) {
                    $bashCounts[$key]++
                } else {
                    $bashCounts[$key] = 1
                }
            }
            elseif ($toolName -like "mcp__*") {
                if ($mcpCounts.ContainsKey($toolName)) {
                    $mcpCounts[$toolName]++
                } else {
                    $mcpCounts[$toolName] = 1
                }
            }
        }
    }
}

Write-Host ""
Write-Host "=== SCAN SUMMARY ==="
Write-Host "Files scanned: $($files.Count)"
Write-Host "Lines parsed: $totalLines"
Write-Host "Assistant messages: $totalAssistantMessages"
Write-Host "Total tool_use items: $totalToolUses"
Write-Host ""

Write-Host "=== BASH COMMANDS (sorted by count desc) ==="
$bashCounts.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
    "{0,6}  {1}" -f $_.Value, $_.Key
}

Write-Host ""
Write-Host "=== MCP TOOLS (sorted by count desc) ==="
$mcpCounts.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
    "{0,6}  {1}" -f $_.Value, $_.Key
}
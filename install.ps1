param(
    [string]$Destination = $(if ($env:CODEX_HOME) {
        Join-Path $env:CODEX_HOME "skills\novel-writing-engine"
    } else {
        Join-Path $HOME ".codex\skills\novel-writing-engine"
    }),
    [switch]$Update
)

$ErrorActionPreference = "Stop"
$source = [System.IO.Path]::GetFullPath($PSScriptRoot)
$destinationPath = [System.IO.Path]::GetFullPath($Destination)

if ($destinationPath -eq $source -or $destinationPath.StartsWith($source + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Error "Destination must not be the source directory or a directory inside it."
    exit 3
}

if (Test-Path -LiteralPath $destinationPath) {
    if (-not $Update) {
        Write-Error "Destination already exists: $destinationPath. Use -Update to copy updated files without deleting existing files."
        exit 2
    }
} else {
    New-Item -ItemType Directory -Path $destinationPath | Out-Null
}

Get-ChildItem -LiteralPath $source -Force |
    Where-Object { $_.Name -notin @(".git", "work", "__pycache__") } |
    ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $destinationPath -Recurse -Force
    }

Write-Output "Installed novel-writing-engine to $destinationPath"

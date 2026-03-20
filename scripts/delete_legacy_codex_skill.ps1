param(
    [Parameter(Mandatory = $true)]
    [string]$LegacyPath
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $LegacyPath)) {
    Write-Output "LEGACY_MISSING=$LegacyPath"
    exit 0
}

Remove-Item -LiteralPath $LegacyPath -Recurse -Force
Write-Output "LEGACY_DELETED=$LegacyPath"

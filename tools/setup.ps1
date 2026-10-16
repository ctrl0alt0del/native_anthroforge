param([switch]$SkipQtSdk)
. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Invoke-Checked uv @('python', 'install', (Get-Content .python-version).Trim())
    Invoke-Checked uv @('sync', '--locked', '--all-extras', '--group', 'qt-sdk')
    if (-not $SkipQtSdk) { & "$PSScriptRoot\qt-sdk.ps1" }
    & "$PSScriptRoot\build-native.ps1"
} finally { Pop-Location }


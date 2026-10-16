param([string]$Preset = 'windows-dev', [string]$AddonSource = '')
. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    $configure = @('run', '--no-sync', 'cmake', '--preset', $Preset)
    if ($env:AF_QT_SDK) { $configure += "-DCMAKE_PREFIX_PATH=$env:AF_QT_SDK" }
    if ($AddonSource) { $configure += "-DAF_ADDON_SOURCE=$AddonSource" }
    Invoke-Checked uv $configure
    Invoke-Checked uv @('run', '--no-sync', 'cmake', '--build', '--preset', $Preset)
    Invoke-Checked uv @('run', '--no-sync', 'ctest', '--preset', $Preset)
} finally { Pop-Location }


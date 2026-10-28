param([string]$Preset = 'windows-dev', [string]$AddonSource = '', [string]$BuildDirectory = '')
. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    $configure = @('run', '--no-sync', 'cmake', '--preset', $Preset)
    if ($env:AF_QT_SDK) { $configure += "-DCMAKE_PREFIX_PATH=$env:AF_QT_SDK" }
    if ($AddonSource) { $configure += "-DAF_ADDON_SOURCE=$AddonSource" }
    if ($BuildDirectory) { $configure += @('-B', $BuildDirectory) }
    Invoke-Checked uv $configure
    if ($BuildDirectory) {
        Invoke-Checked uv @('run', '--no-sync', 'cmake', '--build', $BuildDirectory)
        Invoke-Checked uv @('run', '--no-sync', 'ctest', '--test-dir', $BuildDirectory, '--output-on-failure')
        $env:ANTHROFORGE_NATIVE_LIBRARY = Join-Path $BuildDirectory 'bin/af_native.dll'
    } else {
        Invoke-Checked uv @('run', '--no-sync', 'cmake', '--build', '--preset', $Preset)
        Invoke-Checked uv @('run', '--no-sync', 'ctest', '--preset', $Preset)
    }
} finally { Pop-Location }


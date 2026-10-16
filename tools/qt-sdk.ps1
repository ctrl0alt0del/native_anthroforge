. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    $config = '.tools\qt\6.12.0\msvc2022_64\lib\cmake\Qt6Quick3D\Qt6Quick3DConfig.cmake'
    if (-not (Test-Path -LiteralPath $config)) {
        Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/install_qt.py')
    }
} finally { Pop-Location }


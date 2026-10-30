param([string]$BuildDirectory = '')
. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Invoke-Checked uv @('lock', '--check')
    Invoke-Checked uv @('run', '--no-sync', 'ruff', 'check', 'src', 'tests', 'tools')
    Invoke-Checked uv @('run', '--no-sync', 'ruff', 'format', '--check', 'src', 'tests', 'tools')
    Invoke-Checked uv @('run', '--no-sync', 'mypy')
    & "$PSScriptRoot\build-native.ps1" -BuildDirectory $BuildDirectory
    & "$PSScriptRoot\check-native-style.ps1" -BuildDirectory $BuildDirectory
    & "$PSScriptRoot\check-script-style.ps1"
    $qmlCheck = @('run', '--no-sync', 'python', 'tools/check_qml.py')
    if ($BuildDirectory) { $qmlCheck += @('--native', $BuildDirectory) }
    Invoke-Checked uv $qmlCheck
    Invoke-Checked uv @('run', '--no-sync', 'python', '-m', 'pytest')
    Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/check_numerics.py')
    Invoke-Checked uv @('run', '--no-sync', 'anthroforge', 'doctor', '--require-native')
} finally { Pop-Location }

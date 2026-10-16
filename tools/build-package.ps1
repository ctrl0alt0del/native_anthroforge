. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Invoke-Checked uv @('build')
    Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/check_wheel.py')
} finally { Pop-Location }

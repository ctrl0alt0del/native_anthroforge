. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Invoke-Checked uv @('run', '--no-sync', 'anthroforge-desktop', '--smoke-test', '--screenshot', 'build/desktop-smoke.png')
} finally { Pop-Location }

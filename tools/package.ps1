. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    if (-not $env:NUITKA_CACHE_DIR) { $env:NUITKA_CACHE_DIR = Join-Path $env:USERPROFILE '.anthroforge-build-cache' }
    Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/package_release.py')
    $spec = Join-Path $ProjectRoot 'build\package-input\pysidedeploy.spec'
    Invoke-Checked uv @('run', '--no-sync', 'pyside6-deploy', '-c', $spec, '--force', '--no-install', '--keep-deployment-files')
    Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/package_release.py', '--finish')
} finally { Pop-Location }

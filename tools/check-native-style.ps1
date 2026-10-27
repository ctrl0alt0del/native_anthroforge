param([string]$BuildDirectory = '')
. "$PSScriptRoot\common.ps1"
if (-not $BuildDirectory) { $BuildDirectory = 'build/dev' }
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    foreach ($source in Get-ChildItem native -Recurse -Filter '*.cpp' | Where-Object { $_.FullName -notmatch '\\vendor\\' }) {
        Invoke-Checked clang-tidy @($source.FullName, '-p', $BuildDirectory, '--quiet')
    }
} finally { Pop-Location }

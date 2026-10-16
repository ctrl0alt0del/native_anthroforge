. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    foreach ($source in Get-ChildItem native -Recurse -Filter '*.cpp' | Where-Object { $_.FullName -notmatch '\\vendor\\' }) {
        Invoke-Checked clang-tidy @($source.FullName, '-p', 'build/dev', '--quiet')
    }
} finally { Pop-Location }

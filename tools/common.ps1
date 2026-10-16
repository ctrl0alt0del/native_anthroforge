$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:UV_PYTHON_INSTALL_DIR = Join-Path $ProjectRoot '.tools\python'

function Invoke-Checked {
    param([string]$File, [string[]]$Arguments)
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$File failed with exit code $LASTEXITCODE" }
}

function Find-VisualStudio {
    param([string]$Component)
    $finder = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
    return & $finder -latest -products '*' -requires $Component -property installationPath
}

function Import-NativeEnvironment {
    $install = Find-VisualStudio 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64'
    if (-not $install) { throw 'Install Visual Studio C++ tools and LLVM/clang-cl.' }
    $vcvars = Join-Path $install 'VC\Auxiliary\Build\vcvars64.bat'
    $lines = & cmd.exe /d /s /c ('call "{0}" >nul && set' -f $vcvars)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot initialize Visual Studio environment.' }
    foreach ($line in $lines) {
        if ($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
    }
    $llvm = Find-VisualStudio 'Microsoft.VisualStudio.Component.VC.Llvm.Clang'
    $clang = Join-Path $llvm 'VC\Tools\Llvm\x64\bin'
    if (-not (Test-Path -LiteralPath (Join-Path $clang 'clang-cl.exe'))) { throw 'Install the Visual Studio LLVM component.' }
    $env:PATH = "$clang;$env:PATH"
}


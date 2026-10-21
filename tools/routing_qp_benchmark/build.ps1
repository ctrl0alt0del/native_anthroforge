. "$PSScriptRoot/../common.ps1"
Push-Location $ProjectRoot
try {
    Import-NativeEnvironment
    Invoke-Checked uv @('run', '--no-sync', 'python', 'tools/routing_qp_benchmark/prepare.py')
    $stage = Join-Path $ProjectRoot 'build/routing-piqp/source'
    Invoke-Checked cmake @('-S', 'tools/routing_qp_benchmark', '-B', 'build/routing-piqp/native',
        '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_COMPILER=clang-cl',
        "-DAF_ROOT=$ProjectRoot", "-DAF_STAGE=$stage")
    Invoke-Checked cmake @('--build', 'build/routing-piqp/native', '-j', '2')
} finally { Pop-Location }

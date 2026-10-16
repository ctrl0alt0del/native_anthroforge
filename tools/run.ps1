. "$PSScriptRoot\common.ps1"
Push-Location $ProjectRoot
try { Invoke-Checked uv (@('run', '--no-sync', 'anthroforge-desktop') + $args) }
finally { Pop-Location }


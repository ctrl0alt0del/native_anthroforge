. "$PSScriptRoot\common.ps1"
foreach ($file in Get-ChildItem $PSScriptRoot -Filter '*.ps1') {
    $tokens = $null
    $parseErrors = $null
    $tree = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors) { throw ($parseErrors | Out-String) }
    $functions = $tree.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)
    foreach ($function in $functions) {
        $length = $function.Extent.EndLineNumber - $function.Extent.StartLineNumber + 1
        if ($length -gt 15) { throw "$($file.Name): $($function.Name) exceeds 15 lines ($length)." }
    }
}
Write-Output 'PowerShell parsing and function limits passed.'

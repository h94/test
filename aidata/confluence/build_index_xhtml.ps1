# 由 _index.md 產生 _index.xhtml（Confluence Storage Format）
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
node md_to_xhtml.mjs
Write-Host 'Done: _index.xhtml'

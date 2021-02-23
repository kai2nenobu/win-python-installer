
[CmdletBinding()]
Param(
  [Parameter(Position=0)]
  [string]$Ref='master',
  [string]$OutDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $OutDirectory) {
  $OutDirectory = Join-Path $PWD 'dist'
}

# Clone source
git clone --depth 1 --branch $Ref 'https://github.com/python/cpython.git' cpython
if ($LASTEXITCODE -gt 0) { exit $LASTEXITCODE }

# Monkey patch for python 3.6.x
if ($Ref.StartsWith('3.6') -or $Ref.StartsWith('v3.6')) {
  'Monkey Patch for python 3.6.x'
  $file = 'cpython\Doc\make.bat'
  ((Get-Content -Path $file -Raw) -replace '-m pip install sphinx','-m pip install sphinx==2.2.0') `
    | Set-Content -Path $file
}

# Build installer
cmd /c cpython\Tools\msi\buildrelease.bat -x64 --skip-pgo --skip-nuget --skip-zip -o $OutDirectory
if ($LASTEXITCODE -gt 0) { exit $LASTEXITCODE }

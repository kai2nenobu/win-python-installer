
[CmdletBinding()]
Param(
  [Parameter(Position=0)]
  [string]$Ref='main',
  [string]$OutDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $OutDirectory) {
  $OutDirectory = Join-Path $PWD 'dist'
}

$BuildOptions = @('-x64','--skip-nuget','--skip-zip','-o',"$OutDirectory")

# Clone source
git clone --depth 1 --branch $Ref 'https://github.com/python/cpython.git' cpython
if ($LASTEXITCODE -gt 0) { exit $LASTEXITCODE }

# Special operations for version 3.6.x
if ($Ref.StartsWith('3.6') -or $Ref.StartsWith('v3.6')) {
  'Skip PGO compile for python 3.6.x'
  $BuildOptions += '--skip-pgo'
}

# Special operations for version 3.8.12
if ($Ref -eq 'v3.8.12') {
  # https://github.com/python/cpython/commit/8c3a10e58b12608c3759fee684e7aa399facae2a
  'Apply a patch to find libffi correctly.'
  Push-Location cpython
  curl.exe -sSL https://github.com/python/cpython/commit/8c3a10e58b12608c3759fee684e7aa399facae2a.patch `
    | git -c user.name=dummy -c 'user.email=dummy@example.com' am
  Pop-Location
}

'Install documentation dependencies'  # https://bugs.python.org/issue45618
if ($Ref -match '^v?3\.[67]') {
  python -m pip install sphinx==2.2.0 docutils==0.17.1 blurb python-docs-theme
} else {
  python -m pip install -r ./Docs/requirements.txt
}

# Avoid a build error for version 3.7 and 3.8 (ref. https://github.com/kai2nenobu/win-python-installer/issues/6)
if ($Ref -match '^v?3\.[78]') {
  'Avoid Windows 11 SDK in branch 3.7 and 3.8'
  Push-Location cpython
  git -c user.name=dummy -c 'user.email=dummy@example.com' am ..\patch\avoid_win11_sdk.patch
  Pop-Location
}

# Build installer

cmd /c cpython\Tools\msi\buildrelease.bat @BuildOptions
if ($LASTEXITCODE -gt 0) { exit $LASTEXITCODE }

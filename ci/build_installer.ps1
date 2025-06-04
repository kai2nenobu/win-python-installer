
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

# Avoid a build error for version 3.7 (ref. https://github.com/kai2nenobu/win-python-installer/issues/6)
if ($Ref -match '^v?3\.7') {
  'Avoid Windows 11 SDK in branch 3.7'
  Push-Location cpython
  git -c user.name=dummy -c 'user.email=dummy@example.com' am ..\patch\avoid_win11_sdk.patch
  Pop-Location
}

# Install visual studio components for MSVC v140 on version 3.9
if ($Ref -match '^v?3\.9') {
  # https://github.com/actions/runner-images/issues/9701
  'Install visual studio components for MSVC v140'
  $InstallerPath = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe'
  $InstallPath = 'C:\Program Files\Microsoft Visual Studio\2022\Enterprise'
  $componentsToRemove= @(
    'Microsoft.VisualStudio.Component.VC.140' # MSVC v140 - VS 2015 C++ build tools (v14.00)
  )
  [string]$workloadArgs = $componentsToRemove | ForEach-Object {" --add " +  $_}
  $Arguments = ('/c', "`"$InstallerPath`"", 'modify', '--installPath', "`"$InstallPath`"",$workloadArgs, '--quiet', '--norestart', '--nocache')
  # should be run twice
  $process = Start-Process -FilePath cmd.exe -ArgumentList $Arguments -Wait -PassThru -WindowStyle Hidden
  $process = Start-Process -FilePath cmd.exe -ArgumentList $Arguments -Wait -PassThru -WindowStyle Hidden
}

# Build installer
cmd /c cpython\Tools\msi\buildrelease.bat @BuildOptions
if ($LASTEXITCODE -gt 0) { exit $LASTEXITCODE }

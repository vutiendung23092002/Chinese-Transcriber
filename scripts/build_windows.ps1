param([string]$Python = '', [switch]$SkipModels)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if(-not $Python){
    if(Test-Path -LiteralPath '.tools\python311\python.exe'){$Python=Join-Path $projectRoot '.tools\python311\python.exe'}
    else{$Python=Join-Path $projectRoot '.venv\Scripts\python.exe'}
}
& $Python scripts\create_icon.py
if($LASTEXITCODE -ne 0){throw 'Icon generation failed'}
& $Python -m PyInstaller --noconfirm packaging\ChineseTranscriber.spec
if($LASTEXITCODE -ne 0){throw 'PyInstaller failed'}
& $Python scripts\prepare_distribution.py $(if($SkipModels){'--skip-models'})
if($LASTEXITCODE -ne 0){throw 'Distribution preparation failed'}
if(Test-Path -LiteralPath '.tools\python311\python311.zip'){
    & $Python scripts\prepare_python_fallback.py
    if($LASTEXITCODE -ne 0){throw 'Official Python launcher preparation failed'}
    & $Python scripts\prepare_distribution.py $(if($SkipModels){'--skip-models'})
}

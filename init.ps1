#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$exit = 0

function Ok($m)   { Write-Host "[OK]    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[FAIL]  $m" -ForegroundColor Red }

# >>> PERFIL: Python / FastAPI / pytest <<<
# Usa el venv del proyecto; si no existe, cae al python del PATH
$PythonExe = if (Test-Path 'venv\Scripts\python.exe') { 'venv\Scripts\python.exe' } else { 'python' }
$TestCommand = "$PythonExe -m pytest -q"

Write-Host "-- 1. Archivos base del arnes --------------------------"
$base = @('AGENTS.md','feature_list.json','progress/current.md',
          'docs/architecture.md','docs/conventions.md',
          'docs/verification.md','CHECKPOINTS.md')
foreach ($f in $base) {
  if (Test-Path $f) { Ok "Existe $f" } else { Fail "Falta $f"; $exit = 1 }
}

Write-Host ""
Write-Host "-- 2. Validando feature_list.json y specs --------------"
try {
  $data  = Get-Content 'feature_list.json' -Raw -Encoding UTF8 | ConvertFrom-Json
  $valid = @('pending','spec_ready','in_progress','done','blocked')
  $need  = @('spec_ready','in_progress','done')
  $inProgress = @($data.features | Where-Object { $_.status -eq 'in_progress' })
  if ($inProgress.Count -gt 1) {
    Fail "Hay $($inProgress.Count) features in_progress (maximo 1)"; $exit = 1
  }
  $specErrors = @()
  foreach ($f in $data.features) {
    if ($valid -notcontains $f.status) {
      Fail "Estado invalido en feature $($f.id): $($f.status)"; $exit = 1
    }
    $isSdd = $false
    if ($f.PSObject.Properties.Name -contains 'sdd') { $isSdd = [bool]$f.sdd }
    if ($isSdd -and ($need -contains $f.status)) {
      $dir = Join-Path 'specs' $f.name
      foreach ($n in @('requirements.md','design.md','tasks.md')) {
        if (-not (Test-Path (Join-Path $dir $n))) {
          $specErrors += "feature $($f.id) ($($f.name)) en $($f.status) sin $dir/$n"
        }
      }
    }
  }
  if ($specErrors.Count -gt 0) {
    foreach ($e in $specErrors) { Fail $e }
    $exit = 1
  } else {
    Ok "feature_list.json valido ($($data.features.Count) features)"
    Ok "Specs presentes para features sdd no-pending"
  }
} catch {
  Fail "feature_list.json o specs invalidos: $($_.Exception.Message)"
  $exit = 1
}

Write-Host ""
Write-Host "-- 3. Ejecutando tests ---------------------------------"
Write-Host "    > $TestCommand"
cmd /c $TestCommand
if ($LASTEXITCODE -ne 0) { Fail "Tests rojos (exit $LASTEXITCODE)"; $exit = 1 }
else { Ok "Tests verdes" }

Write-Host ""
Write-Host "-- 4. Resumen ------------------------------------------"
if ($exit -eq 0) { Ok "Entorno listo. Puedes trabajar." }
else { Fail "Entorno NO listo. Resuelve los errores antes de avanzar." }
exit $exit

$ErrorActionPreference = 'Stop'
$worldRoot = Join-Path $PSScriptRoot 'world_support'
$worldCompiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
function Build-WorldExecutable([string]$name, [string[]]$sources, [string[]]$options) {
    $absoluteSources = @($sources | ForEach-Object { Join-Path $worldRoot $_ })
    & $worldCompiler /nologo /optimize+ /target:exe "/out:$(Join-Path $worldRoot $name)" @options @absoluteSources
    if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $name" }
}
$searchSources = @(Get-ChildItem -LiteralPath (Join-Path $worldRoot 'native\solver') -Filter '*.cs' | ForEach-Object { 'native\solver\' + $_.Name }) + @('native\rules\ColorRules.cs')
Build-WorldExecutable 'FastOriginalSolver.exe' $searchSources @('/reference:System.Web.Extensions.dll')
Build-WorldExecutable 'EnergySearch.exe' @('native\planner\EnergySearch.cs','native\rules\ColorRules.cs','native\rules\EnergyRules.cs') @('/main:EnergySearch','/reference:System.Web.Extensions.dll')
$ui = @('/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll','/reference:System.Web.Extensions.dll')
Build-WorldExecutable 'SheepClicker.Diagnostics.exe' @('native\clicker\SheepClicker.cs') $ui
Build-WorldExecutable 'SolverPlayback.exe' @('native\clicker\SheepClicker.cs','native\clicker\SolverPlayback.cs','native\planner\RollingPlanner.cs','native\rules\ColorRules.cs','native\rules\EnergyRules.cs') ($ui + @('/main:SolverPlayback'))
Write-Host 'World support build complete.'

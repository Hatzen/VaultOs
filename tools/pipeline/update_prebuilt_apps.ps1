<#
.SYNOPSIS
    VaultOs Prebuilt Apps Release Pipeline (Windows PowerShell)
.DESCRIPTION
    Compiles CustomOtterControl and ParAnnoying as Android release APKs
    and stages them into android_vendor_vaultos/apps/.
    Reads local path overrides from <repo_root>/.env or environment variables.
#>
param(
    [string]$CustomOtterDir,
    [string]$ParAnnoyingDir,
    [string]$VendorVaultOsDir,
    [switch]$SkipCustomOtter,
    [switch]$SkipParAnnoying
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path
$WorkspaceRoot = (Resolve-Path (Join-Path $RepoRoot "..")).Path

# Load .env from repo root if present (without overriding explicit env vars)
$DotEnv = Join-Path $RepoRoot ".env"
if (Test-Path $DotEnv) {
    Get-Content $DotEnv | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            $k = $matches[1].Trim()
            $v = $matches[2].Trim().Trim('"').Trim("'")
            if (-not [Environment]::GetEnvironmentVariable($k, "Process")) {
                [Environment]::SetEnvironmentVariable($k, $v, "Process")
            }
        }
    }
}

function Resolve-RepoPath([string]$ParamValue, [string]$EnvKey, [string]$DefaultRelToRepo) {
    $raw = if ($ParamValue) { $ParamValue } elseif ([Environment]::GetEnvironmentVariable($EnvKey, "Process")) { [Environment]::GetEnvironmentVariable($EnvKey, "Process") } else { $DefaultRelToRepo }
    if ([System.IO.Path]::IsPathRooted($raw)) { return $raw }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $raw))
}

$CustomOtterDir = Resolve-RepoPath $CustomOtterDir "CUSTOM_OTTER_DIR" "..\..\AndroidStudioProjects\CustomOtterControl"
$ParAnnoyingDir = Resolve-RepoPath $ParAnnoyingDir "PARANNOYING_DIR" "..\..\StudioProjects\ParAnnoying"
$VendorVaultOsDir = Resolve-RepoPath $VendorVaultOsDir "VENDOR_VAULTOS_DIR" "..\android_vendor_vaultos"

function Build-And-Stage {
    param(
        [string]$Name,
        [string]$ProjectDir,
        [string]$GradleTask,
        [string]$BuiltApkRelPath,
        [string]$DestApkPath,
        [string[]]$ObsoleteFiles = @()
    )

    if (-not (Test-Path $ProjectDir)) {
        throw "[$Name] Project directory not found: $ProjectDir (configure .env from .env.example)"
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Building $Name ($GradleTask)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    Push-Location $ProjectDir
    try {
        & .\gradlew.bat $GradleTask --no-daemon
        if ($LASTEXITCODE -ne 0) {
            throw "[$Name] Gradle build failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }

    $BuiltApk = Join-Path $ProjectDir $BuiltApkRelPath
    if (-not (Test-Path $BuiltApk)) {
        throw "[$Name] Expected APK not found after build: $BuiltApk"
    }

    $DestDir = Split-Path -Parent $DestApkPath
    if (-not (Test-Path $DestDir)) {
        New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
    }

    foreach ($Obs in $ObsoleteFiles) {
        $ObsPath = Join-Path $DestDir $Obs
        if (Test-Path $ObsPath) {
            Write-Host "Removing obsolete artifact: $ObsPath" -ForegroundColor Yellow
            Remove-Item -Force $ObsPath
        }
    }

    Copy-Item -Path $BuiltApk -Destination $DestApkPath -Force

    $Hash = (Get-FileHash -Path $DestApkPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $SizeMB = [Math]::Round((Get-Item $DestApkPath).Length / 1MB, 2)
    Write-Host "[$Name] Staged -> $DestApkPath ($SizeMB MB, sha256: $Hash)" -ForegroundColor Green
}

if (-not $SkipCustomOtter) {
    Build-And-Stage `
        -Name "CustomOtterControl" `
        -ProjectDir $CustomOtterDir `
        -GradleTask ":app:assembleRelease" `
        -BuiltApkRelPath "app\build\outputs\apk\release\app-release.apk" `
        -DestApkPath (Join-Path $VendorVaultOsDir "apps\CustomOtterControl\app-release.apk") `
        -ObsoleteFiles @("app-debug.apk", "app-release-unsigned.apk")
}

if (-not $SkipParAnnoying) {
    Build-And-Stage `
        -Name "ParAnnoying" `
        -ProjectDir $ParAnnoyingDir `
        -GradleTask ":app:assembleProdRelease" `
        -BuiltApkRelPath "app\build\outputs\apk\prod\release\app-prod-release.apk" `
        -DestApkPath (Join-Path $VendorVaultOsDir "apps\Parannoying\app-prod-release.apk")
}

Write-Host ""
Write-Host "Pipeline complete. Remember to commit and push android_vendor_vaultos!" -ForegroundColor Green

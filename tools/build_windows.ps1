param([switch]$SkipAdbDownload)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "El ejecutable Windows debe compilarse en Windows."
}

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Falló $Program (código $LASTEXITCODE)."
    }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Invoke-Checked -Program "python" -Arguments @("-m", "venv", ".venv")
}
$python = (Resolve-Path ".venv\Scripts\python.exe").Path
Invoke-Checked -Program $python -Arguments @("-m", "pip", "install", "-r", "requirements.txt")
$previousPlatform = $env:QT_QPA_PLATFORM
try {
    $env:QT_QPA_PLATFORM = "windows"
    Invoke-Checked -Program $python -Arguments @("-m", "compileall", "-q", "config", "core", "database", "integrations", "services", "ui", "tools", "tests", "main.py")
    Invoke-Checked -Program $python -Arguments @("-m", "unittest", "discover", "-s", "tests", "-v")
    Invoke-Checked -Program $python -Arguments @("tools/audit_ui.py", "--output", "artifacts/ui")
} finally {
    if ($null -eq $previousPlatform) {
        Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
    } else {
        $env:QT_QPA_PLATFORM = $previousPlatform
    }
}

$buildAssets = Join-Path (Get-Location) ".cache\build-assets"
New-Item -ItemType Directory -Force -Path $buildAssets | Out-Null
Invoke-Checked -Program $python -Arguments @("tools/prepare_icon.py")
$icon = (Resolve-Path "ui\assets\abcell-pro.ico").Path

$platformTools = Join-Path $buildAssets "platform_tools"
New-Item -ItemType Directory -Force -Path $platformTools | Out-Null
$candidates = @((Join-Path (Get-Location) "platform_tools"))
if ($env:ANDROID_HOME) { $candidates += (Join-Path $env:ANDROID_HOME "platform-tools") }
if ($env:ANDROID_SDK_ROOT) { $candidates += (Join-Path $env:ANDROID_SDK_ROOT "platform-tools") }
$adb = Get-Command adb.exe -ErrorAction SilentlyContinue
if ($adb) { $candidates += (Split-Path $adb.Source -Parent) }
foreach ($candidate in $candidates) {
    if (Test-Path (Join-Path $candidate "adb.exe")) {
        foreach ($file in @("adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll")) {
            Copy-Item (Join-Path $candidate $file) $platformTools -Force
        }
        break
    }
}
if (-not (Test-Path (Join-Path $platformTools "adb.exe"))) {
    if ($SkipAdbDownload) { throw "No se encontró ADB. Instala platform-tools o permite la descarga." }
    $zip = Join-Path $buildAssets "platform-tools.zip"
    $expanded = Join-Path $buildAssets "download"
    Invoke-WebRequest "https://dl.google.com/android/repository/platform-tools-latest-windows.zip" -OutFile $zip
    Expand-Archive $zip -DestinationPath $expanded -Force
    foreach ($file in @("adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll")) {
        Copy-Item (Join-Path $expanded "platform-tools\$file") $platformTools -Force
    }
}
foreach ($file in @("adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll")) {
    if (-not (Test-Path (Join-Path $platformTools $file))) { throw "Falta el recurso ADB: $file" }
}

$arguments = @("-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--noconsole",
               "--icon", $icon, "--version-file", "config/windows_version_info.txt", "--name", "ABCell Pro")
foreach ($module in @("config.settings", "config.assets", "core.catalog_data", "database.db_manager",
                      "services.workshop_service", "integrations.adb_manager", "integrations.printer_58mm",
                      "integrations.ticket_image", "integrations.whatsapp_center", "ui.theme", "ui.icons",
                      "ui.layouts", "ui.main_window", "PySide6.QtSvg")) {
    $arguments += @("--hidden-import", $module)
}
foreach ($folder in @("config", "core", "database", "services", "integrations", "ui")) {
    $arguments += @("--add-data", "$folder;$folder")
}
$arguments += @("--add-data", "$icon;ui/assets", "--add-data", "$platformTools;platform_tools", "main.py")
Invoke-Checked -Program $python -Arguments $arguments
Write-Host "Compilación terminada: dist\ABCell Pro.exe"
Write-Host "Verificación de botones: artifacts\ui\BUTTON_CHECKLIST.md"

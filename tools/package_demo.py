"""Crea una distribución de código demo por lista permitida, nunca copia la app completa."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SHARED = ("ui/__init__.py", "ui/theme.py", "ui/icons.py", "ui/layouts.py", "ui/table_sizing.py",
          "ui/assets/abcell-pro.ico", "ui/assets/abcell-pro.jpg", "ui/assets/chevron-down.svg")
DEMO = ("offline_demo/__init__.py", "offline_demo/main.py", "offline_demo/trial.py",
        "offline_demo/store.py", "offline_demo/window.py", "offline_demo/windows_version_info.txt")
TESTS = ("tests/test_demo_trial.py", "tests/test_demo_ui.py")

BUILD_SCRIPT = r'''$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($env:OS -ne "Windows_NT") { throw "Compila el ejecutable en Windows." }
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno." }
}
$python = ".venv\Scripts\python.exe"
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Falló instalar dependencias." }
$previousPlatform = $env:QT_QPA_PLATFORM
try {
    $env:QT_QPA_PLATFORM = "windows"
    & $python -m unittest discover -s tests -p "test_demo_*.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Fallaron las pruebas demo." }
} finally {
    if ($null -eq $previousPlatform) { Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue }
    else { $env:QT_QPA_PLATFORM = $previousPlatform }
}
& $python -m PyInstaller --noconfirm --clean --onefile --noconsole --name "ABCell Pro Demo" --icon "ui/assets/abcell-pro.ico" --version-file "offline_demo/windows_version_info.txt" --hidden-import PySide6.QtSvg --add-data "ui/assets;ui/assets" main.py
if ($LASTEXITCODE -ne 0) { throw "Falló compilar la demo." }
Write-Host "Ejecutable: dist/ABCell Pro Demo.exe"
'''

STANDALONE_WORKFLOW = '''name: Compilar ABCell Pro Demo
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Pruebas y compilación demo
        shell: pwsh
        run: ./build_windows.ps1
      - uses: actions/upload-artifact@v4
        with:
          name: ABCell-Pro-Demo-Windows
          path: dist/ABCell Pro Demo.exe
'''


def stage(destination: Path, root=ROOT):
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("La carpeta destino debe estar vacía; no se borran archivos existentes.")
    destination.mkdir(parents=True, exist_ok=True)
    for relative in (*SHARED, *DEMO, *TESTS):
        source, target = root / relative, destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / "README.md").write_text((root / "offline_demo/README.md").read_text(encoding="utf-8"), encoding="utf-8")
    (destination / "main.py").write_text('from offline_demo.main import main\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', encoding="utf-8")
    (destination / "requirements.txt").write_text("PySide6>=6.7.0\npyinstaller>=6.0.0\n", encoding="utf-8")
    (destination / "build_windows.ps1").write_text(BUILD_SCRIPT, encoding="utf-8")
    (destination / ".gitignore").write_text(".venv/\n__pycache__/\n*.py[cod]\nbuild/\ndist/\n*.spec\n*.log\ntrial.json\n*.sqlite3\n", encoding="utf-8")
    workflow = destination / ".github/workflows/build-demo.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(STANDALONE_WORKFLOW, encoding="utf-8")
    manifest = {str(file.relative_to(destination)).replace("\\", "/"): hashlib.sha256(file.read_bytes()).hexdigest()
                for file in sorted(destination.rglob("*")) if file.is_file()}
    (destination / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def archive(source: Path, target: Path):
    # Únicamente los archivos de MANIFEST; ni cachés, datos ni compilaciones.
    manifest = json.loads((source / "MANIFEST.json").read_text(encoding="utf-8"))
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as output:
        for relative in sorted([*manifest, "MANIFEST.json"]):
            output.write(source / relative, "ABCell-Pro-Demo/" + relative)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    print("Archivos demo:", len(stage(args.output)))
    if args.zip:
        archive(args.output, args.zip)
        print(args.zip)

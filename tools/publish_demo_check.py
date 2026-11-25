"""Diagnósticos y miniaturas demo accesibles en el Check, solo para CI."""
import base64
import io
from pathlib import Path
from tools.publish_ui_check import publish

if __name__ == "__main__":
    root = Path("artifacts/ui")
    log = root / "tests.log"
    checklist = root / "BUTTON_CHECKLIST.md"
    publish("Diagnóstico DEMO Windows", log.read_text(encoding="utf-8", errors="replace") if log.exists() else "No se generó log.",
            checklist.read_text(encoding="utf-8") if checklist.exists() else "Sin checklist.")
    from PIL import Image
    for path in sorted(root.glob("demo-page-*.png")):
        with Image.open(path) as image:
            image.thumbnail((1366, 900))
            buffer = io.BytesIO()
            image.convert("RGB").save(buffer, format="WEBP", quality=60)
        encoded = base64.b64encode(buffer.getvalue()).decode()
        if len(encoded) < 64000:
            publish("Vista DEMO " + path.stem, "Captura automática: " + path.name, encoded)

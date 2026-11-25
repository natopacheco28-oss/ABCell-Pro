"""Publica diagnóstico y miniaturas en Checks; solo se ejecuta en CI."""
import base64
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def publish(name, summary, text=""):
    body = json.dumps({
        "name": name, "head_sha": os.environ["SHA"], "status": "completed",
        "conclusion": "neutral", "output": {
            "title": name, "summary": summary[:64000], "text": text[:64000],
        },
    }).encode()
    request = Request(
        f"https://api.github.com/repos/{os.environ['REPO']}/check-runs",
        data=body, headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                            "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
    )
    with urlopen(request) as response:
        print("Publicado check", json.load(response)["id"], name)


if __name__ == "__main__":
    root = Path("artifacts/ui")
    log = root / "audit.log"
    report = root / "BUTTON_CHECKLIST.md"
    summary = (log.read_text(errors="replace") if log.exists() else "Sin log de auditoría")
    text = report.read_text() if report.exists() else "La auditoría no llegó a generar el inventario."
    publish("Diagnóstico UI escala " + os.environ["SCALE"], summary, text)
    if os.environ["SCALE"] == "1":
        from PIL import Image
        for path in sorted(root.glob("*.png")):
            with Image.open(path) as image:
                image.thumbnail((1366, 900))
                data = io.BytesIO()
                image.convert("RGB").save(data, format="WEBP", quality=55)
            encoded = base64.b64encode(data.getvalue()).decode()
            if len(encoded) < 64000:
                publish("Vista UI " + path.stem, "Miniatura WebP de auditoría: " + path.name, encoded)

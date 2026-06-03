from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
OUT_ZIP = ROOT / 'screenshots_all.zip'
SCREENSHOT_DIR = ROOT / 'screenshots'
PRES_DIR = ROOT / 'Presentation-and-Documentation'

with zipfile.ZipFile(OUT_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    if SCREENSHOT_DIR.exists():
        for p in sorted(SCREENSHOT_DIR.rglob('*.png')):
            z.write(p, p.relative_to(ROOT))
    # include presentation screenshots and model image
    for p in sorted(PRES_DIR.glob('*.png')):
        z.write(p, p.relative_to(ROOT))

print('Created', OUT_ZIP)

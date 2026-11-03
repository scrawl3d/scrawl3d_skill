"""Builds dist/scrawl3d-skill.zip for claude.ai (Settings > Capabilities > Skills).
The zip holds the scrawl3d/ folder with SKILL.md at its top. Run after changing the skill:
    python build-zip.py
"""
import os, zipfile

SRC, OUT = 'skills/scrawl3d', 'dist/scrawl3d-skill.zip'
os.makedirs('dist', exist_ok=True)
files = sorted(os.path.join(d, f) for d, _, fs in os.walk(SRC) for f in fs)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files:
        name = 'scrawl3d/' + os.path.relpath(p, SRC).replace(os.sep, '/')
        # Fixed timestamp: the same skill gives the same zip, so git only sees real changes.
        info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, open(p, 'rb').read())
print(OUT, [n for n in zipfile.ZipFile(OUT).namelist()])

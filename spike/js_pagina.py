"""JS que uma página baixa: scripts referenciados no HTML e os imports estáticos deles, recursivo."""

import gzip
import re
import sys
from pathlib import Path

import brotli

dist, pagina = Path(sys.argv[1]), Path(sys.argv[2])
html = pagina.read_text(encoding="utf-8")
fila = set(re.findall(r'"(/_astro/[^"]+\.js)"', html)) | set(re.findall(r'"(/_next/static/[^"]+\.js)"', html))
vistos = set()
while fila:
    u = fila.pop()
    if u in vistos:
        continue
    vistos.add(u)
    src = (dist / u.lstrip("/")).read_text(encoding="utf-8")
    base = u.rsplit("/", 1)[0]
    for imp in re.findall(r'(?:from|import)\s*\(?\s*"(\./[^"]+\.js)"', src):
        fila.add(base + "/" + imp[2:])
tg = tb = 0
for u in sorted(vistos):
    b = (dist / u.lstrip("/")).read_bytes()
    g, r = len(gzip.compress(b, 9)), len(brotli.compress(b, quality=11))
    tg += g
    tb += r
    print(f"{u}  {len(b)} bruto  {g} gzip  {r} brotli")
inline = sum(len(s) for s in re.findall(r"<script[^>]*>(.*?)</script>", html, re.S))
print(f"TOTAL arquivos={len(vistos)} gzip={tg} brotli={tb}; script embutido no HTML={inline} bytes brutos")

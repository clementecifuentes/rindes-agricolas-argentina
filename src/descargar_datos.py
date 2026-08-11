"""
Descarga las Estimaciones Agrícolas oficiales de la Secretaría de
Agricultura, Ganadería y Pesca (Argentina): superficie, producción y
rendimiento por cultivo, campaña y departamento desde 1969.

Fuente: https://datos.magyp.gob.ar/dataset/estimaciones-agricolas

Uso:
    python src/descargar_datos.py
"""

import sys

# La consola de Windows usa cp1252 y rompe con acentos y flechas
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

import requests

URL = ("https://datos.magyp.gob.ar/dataset/9e1e77ba-267e-4eaa-a59f-3296e86b5f36/"
       "resource/95d066e6-8a0f-4a80-b59d-6f28f88eacd5/download/"
       "estimaciones-agricolas-2026-03.csv")


def descargar(destino: str = "data/estimaciones.csv") -> None:
    ruta = Path(destino)
    ruta.parent.mkdir(exist_ok=True)
    if ruta.exists():
        print(f"{ruta} ya existe, se omite")
        return
    print("descargando estimaciones agrícolas (~15 MB)...")
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    ruta.write_bytes(r.content)
    print(f"Listo: {ruta} ({len(r.content) / 1e6:.1f} MB)")


if __name__ == "__main__":
    try:
        descargar()
    except requests.RequestException as exc:
        sys.exit(f"Error de descarga: {exc}")

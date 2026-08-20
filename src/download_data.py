"""
Download the official Crop Estimates dataset published by the Argentine
Secretariat of Agriculture, Livestock and Fisheries: area, production and
yield by crop, season and department since 1969.

Source: https://datos.magyp.gob.ar/dataset/estimaciones-agricolas

Usage:
    python src/download_data.py
"""

import sys
from pathlib import Path

import requests

URL = ("https://datos.magyp.gob.ar/dataset/9e1e77ba-267e-4eaa-a59f-3296e86b5f36/"
       "resource/95d066e6-8a0f-4a80-b59d-6f28f88eacd5/download/"
       "estimaciones-agricolas-2026-03.csv")


def download(destination: str = "data/crop_estimates.csv") -> None:
    """Fetch the dataset unless it is already on disk."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"{path} already present, skipped")
        return
    print("downloading crop estimates (~15 MB)...")
    response = requests.get(URL, timeout=300)
    response.raise_for_status()
    path.write_bytes(response.content)
    print(f"Done: {path} ({len(response.content) / 1e6:.1f} MB)")


if __name__ == "__main__":
    try:
        download()
    except requests.RequestException as exc:
        sys.exit(f"Download failed: {exc}")

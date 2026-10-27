#!/usr/bin/env python3
"""Génère le fond d'écran d'Aube (paquet de fond d'écran Plasma).

Fond #0D0D12, lueur de lever de soleil floutée en bas (#F2622E, puis #FFC48A
au centre) et lueur indigo #3B2A8F en haut à gauche (voir DESIGN.md).
La version sombre reprend les mêmes formes, plus sourdes (#7A2A12, #2A1F6E).

Usage : make-wallpaper.py <dossier du paquet>
Produit contents/images/3840x2160.png (mode clair),
contents/images_dark/3840x2160.png (mode sombre) et contents/screenshot.png.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 3840, 2160

VARIANTS = {
    "images": {
        "fond": "#0D0D12",
        "soleil": "#F2622E",
        "coeur": "#FFC48A",
        "indigo": "#3B2A8F",
        "intensite": 1.0,
    },
    "images_dark": {
        "fond": "#0A0A0D",
        "soleil": "#7A2A12",
        "coeur": "#A8461E",
        "indigo": "#2A1F6E",
        "intensite": 0.9,
    },
}


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def render(v):
    aspect = W / H
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    u = x / H  # unités de hauteur, pour des lueurs rondes
    t = y / H

    img = np.broadcast_to(rgb(v["fond"]), (H, W, 3)).copy()

    # Lueur indigo, en haut à gauche.
    d = np.hypot(u - 0.10 * aspect, t + 0.05)
    a = (1 - smoothstep(0, 1.15, d)) ** 1.6 * 0.85
    img += (rgb(v["indigo"]) - img) * a[..., None]

    # Lever de soleil : ellipse centrée sous le bord du bas.
    d = np.hypot((u - 0.5 * aspect) / 1.5, (t - 1.15) / 0.95)
    coeur = np.clip(1 - d / 0.55, 0, 1) ** 1.3
    couleur = rgb(v["soleil"]) + (rgb(v["coeur"]) - rgb(v["soleil"])) * coeur[..., None]
    a = np.clip(1 - d, 0, 1) ** 1.15 * v["intensite"]
    img += (couleur - img) * a[..., None]

    # Tramage léger contre les bandes de couleur.
    rng = np.random.default_rng(0)
    img += (rng.random(img.shape, dtype=np.float32) - 0.5) / 255
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


def main():
    out = Path(sys.argv[1]) / "contents"
    for folder, v in VARIANTS.items():
        (out / folder).mkdir(parents=True, exist_ok=True)
        image = render(v)
        image.save(out / folder / f"{W}x{H}.png", optimize=True)
        if folder == "images":
            image.resize((400, 225), Image.LANCZOS).save(out / "screenshot.png")


if __name__ == "__main__":
    main()

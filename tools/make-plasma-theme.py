#!/usr/bin/env python3
"""Génère le thème Plasma « Aube » : la coque en verre (voir DESIGN.md).

Seuls les éléments qui changent sont fournis ; pour tout le reste, Plasma
se rabat sur Breeze (« default »).

- Dock et barre du haut : verre sombre rgba(28,28,32,0.62), filet blanc 12 %.
  Cadre « south » à coins de 28 px pour le dock (pilule presque complète),
  cadre par défaut à petits coins pour la barre du haut de 34 px.
- Boutons de tâches : cercles de 48 px, cercle blanc translucide derrière
  l'appli active.
- Fenêtres surgissantes (lanceur, calendrier, zone de notification) : verre,
  coins de 20 px.

Plasma découpe chaque fond en 9 morceaux (coins, bords, centre) qu'il
étire selon la taille. Chaque morceau est un élément SVG avec un id précis.

Usage : make-plasma-theme.py <dossier du thème>
"""
import sys
from pathlib import Path

GLASS = "#1C1C20"   # rgb(28,28,32)
WHITE = "#FFFFFF"
ACCENT = "#FF7A3D"


def corner(name, x, y, r, inset):
    """Quart de cercle (remplissage) et arc du filet, pour un coin."""
    a = r - inset
    if name == "topleft":
        fill = f"M{x},{y + r} A{r},{r} 0 0 1 {x + r},{y} L{x + r},{y + r} Z"
        line = f"M{x + inset},{y + r} A{a},{a} 0 0 1 {x + r},{y + inset}"
    elif name == "topright":
        fill = f"M{x},{y} A{r},{r} 0 0 1 {x + r},{y + r} L{x},{y + r} Z"
        line = f"M{x},{y + inset} A{a},{a} 0 0 1 {x + r - inset},{y + r}"
    elif name == "bottomright":
        fill = f"M{x + r},{y} A{r},{r} 0 0 1 {x},{y + r} L{x},{y} Z"
        line = f"M{x + r - inset},{y} A{a},{a} 0 0 1 {x},{y + r - inset}"
    else:  # bottomleft
        fill = f"M{x + r},{y + r} A{r},{r} 0 0 1 {x},{y} L{x + r},{y} Z"
        line = f"M{x + r},{y + r - inset} A{a},{a} 0 0 1 {x + inset},{y}"
    return fill, line


def edge(name, x, y, r, inset):
    """Bord : rectangle de remplissage et ligne du filet côté extérieur."""
    fill = f"M{x},{y} h{r} v{r} h{-r} Z"
    line = {
        "top": f"M{x},{y + inset} h{r}",
        "bottom": f"M{x},{y + r - inset} h{r}",
        "left": f"M{x + inset},{y} v{r}",
        "right": f"M{x + r - inset},{y} v{r}",
    }[name]
    return fill, line


GRID = {
    "topleft": (0, 0), "top": (1, 0), "topright": (2, 0),
    "left": (0, 1), "center": (1, 1), "right": (2, 1),
    "bottomleft": (0, 2), "bottom": (1, 2), "bottomright": (2, 2),
}


def frame(prefix, ox, oy, r, color, opacity, line_opacity=0.0, mask=False):
    """Les 9 morceaux d'un cadre aux coins arrondis de rayon r."""
    p = f"{prefix}-" if prefix else ""
    out = []
    for name, (cx, cy) in GRID.items():
        x, y = ox + cx * r, oy + cy * r
        if name == "center":
            fill, line = f"M{x},{y} h{r} v{r} h{-r} Z", None
        elif name in ("top", "bottom", "left", "right"):
            fill, line = edge(name, x, y, r, 0.5)
        else:
            fill, line = corner(name, x, y, r, 0.5)
        if mask:
            out.append(f'<path id="{p}{name}" d="{fill}" fill="#000"/>')
            continue
        parts = [f'<path d="{fill}" fill="{color}" fill-opacity="{opacity}"/>']
        if line and line_opacity:
            parts.append(f'<path d="{line}" fill="none" stroke="{WHITE}" '
                         f'stroke-opacity="{line_opacity}" stroke-width="1"/>')
        out.append(f'<g id="{p}{name}">{"".join(parts)}</g>')
    return out


def margins(prefix, ox, oy, top, bottom, left, right):
    """Marges intérieures : Plasma lit la taille de ces rectangles invisibles."""
    p = f"{prefix}-" if prefix else ""
    return [
        f'<rect id="{p}hint-top-margin" x="{ox}" y="{oy}" width="1" height="{top}" fill="none"/>',
        f'<rect id="{p}hint-bottom-margin" x="{ox + 2}" y="{oy}" width="1" height="{bottom}" fill="none"/>',
        f'<rect id="{p}hint-left-margin" x="{ox + 4}" y="{oy}" width="{left}" height="1" fill="none"/>',
        f'<rect id="{p}hint-right-margin" x="{ox + 4}" y="{oy + 2}" width="{right}" height="1" fill="none"/>',
    ]


def stretch(prefix, ox, oy):
    """Étirer les bords au lieu de les répéter en mosaïque.

    Sans cet indice, Plasma répète les bords tous les r pixels, et chaque
    raccord se voit à travers le verre translucide.
    """
    p = f"{prefix}-" if prefix else ""
    return [f'<rect id="{p}hint-stretch-borders" x="{ox}" y="{oy}" width="1" height="1" fill="none"/>']


def svg(elements, width, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n'
            "<!-- Généré par tools/make-plasma-theme.py : ne pas modifier à la main. -->\n"
            + "\n".join(elements) + "\n</svg>\n")


def glass_frame(prefix, ox, r, opacity, m):
    """Un fond en verre complet : cadre, masque de flou, marges, étirement."""
    side = 3 * r
    els = frame(prefix, ox, 0, r, GLASS, opacity, line_opacity=0.12)
    # KSvg cherche le masque sous « mask-<préfixe>- » (ex. mask-south-center).
    els += frame(f"mask-{prefix}" if prefix else "mask", ox + side + 10, 0, r, None, None, mask=True)
    els += margins(prefix, ox, side + 10, m, m, m, m)
    els += stretch(prefix, ox + 10, side + 10)
    return els, ox + 2 * side + 20


def panel_background(opacity):
    """Dock et barre du haut.

    Plasma refuse qu'un panneau soit moins épais que ses bords du haut et du
    bas réunis, et il applique ce minimum à la création du panneau, avant de
    savoir où il sera placé : la hauteur forcée est alors enregistrée.
    - Fond par défaut (barre du haut) : petits coins de 4 px, donc aucun
      minimum gênant ; seuls le bas et son filet sont visibles.
    - Préfixe « south » (dock, en bas) : coins de 28 px. À 32 px (la moitié
      exacte des 64 px), les morceaux du milieu feraient 0 px de haut et le
      moindre arrondi laisserait des raccords visibles à travers le verre.
    - Marges « thick » : Plasma les ajoute à 4 px pour tous les panneaux,
      soit 8 px dans le dock (boutons de 48 px) et 6 px en haut.
    """
    els, x = glass_frame("", 0, 4, opacity, 4)
    south, x = glass_frame("south", x, 28, opacity, 4)
    els += south
    els.append(f'<rect id="thick-center" x="{x}" y="0" width="8" height="8" '
               f'fill="{GLASS}" fill-opacity="{opacity}"/>')
    els += margins("thick", x, 20, 4, 4, 4, 4)
    return svg(els, x + 20, 3 * 32 + 40)


def dialog_background(opacity):
    """Fenêtres surgissantes : coins de 20 px, marges de 12 px."""
    els, x = glass_frame("", 0, 20, opacity, 12)
    return svg(els, x, 3 * 20 + 40)


def tasks():
    """Boutons de tâches de 48 px aux coins de 22 px (presque des cercles,
    sans morceaux de 0 px au milieu), icône de 26 px."""
    r = 22
    states = {
        "normal": (WHITE, 0.0),
        "minimized": (WHITE, 0.0),
        "hover": (WHITE, 0.10),
        "focus": (WHITE, 0.16),      # cercle blanc translucide de la maquette
        "attention": (ACCENT, 0.35),
        "progress": (ACCENT, 0.30),
    }
    els = []
    for i, (state, (color, opacity)) in enumerate(states.items()):
        els += frame(state, i * (3 * r + 10), 0, r, color, opacity)
        els += stretch(state, i * (3 * r + 10) + 10, 3 * r + 10)
    els += margins("normal", 0, 3 * r + 10, 11, 11, 11, 11)
    els += stretch("", 20, 3 * r + 10)
    return svg(els, len(states) * (3 * r + 10), 3 * r + 40)


METADATA = """{
    "KPlugin": {
        "Authors": [
            {
                "Name": "Projet Aube"
            }
        ],
        "Description": "Coque en verre d'Aube",
        "Id": "aube",
        "License": "LGPL-2.1-or-later",
        "Name": "Aube",
        "Version": "0.1"
    },
    "X-Plasma-API": "5.0"
}
"""

PLASMARC = """[AdaptiveTransparency]
enabled=true

[ContrastEffect]
enabled=true
contrast=0.2
intensity=1.0
saturation=1.7

[BlurBehindEffect]
enabled=true
"""


def main():
    root = Path(sys.argv[1])
    files = {
        "metadata.json": METADATA,
        "plasmarc": PLASMARC,
        "widgets/panel-background.svg": panel_background(0.92),
        "translucent/widgets/panel-background.svg": panel_background(0.62),
        "widgets/tasks.svg": tasks(),
        "dialogs/background.svg": dialog_background(0.95),
        "translucent/dialogs/background.svg": dialog_background(0.72),
    }
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


if __name__ == "__main__":
    main()

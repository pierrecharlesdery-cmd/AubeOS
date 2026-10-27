#!/usr/bin/env python3
"""Génère les schémas de couleurs AubeDark.colors et AubeLight.colors.

Les jetons viennent de DESIGN.md. L'accent orange porte toujours du texte
foncé (#1C0D04), jamais blanc.

Usage : make-color-schemes.py <dossier de sortie>
"""
import sys
from pathlib import Path

ACCENT = "255,122,61"       # #FF7A3D
ON_ACCENT = "28,13,4"       # #1C0D04

SCHEMES = {
    "AubeDark": {
        "name": "Aube sombre",
        "fg": "250,250,250",           # #FAFAFA
        "fg_inactive": "161,161,170",  # #A1A1AA
        "fg_active": ACCENT,
        "link": ACCENT,
        "visited": "167,139,250",
        "negative": "239,83,80",
        "neutral": "245,180,60",
        "positive": "79,209,181",      # #4FD1B5
        "bg": {
            "Window": ("22,22,26", "30,30,35"),
            "View": ("15,15,19", "22,22,26"),
            "Button": ("38,38,44", "48,48,55"),
            "Header": ("15,15,19", "22,22,26"),
            "Header][Inactive": ("22,22,26", "15,15,19"),
            "Tooltip": ("28,28,32", "22,22,26"),
            "Complementary": ("7,7,10", "15,15,19"),  # #07070A
        },
        "wm": ("15,15,19", "15,15,19"),
    },
    "AubeLight": {
        "name": "Aube clair",
        "fg": "17,17,19",              # #111113
        "fg_inactive": "82,82,91",     # #52525B
        "fg_active": "194,74,16",      # accent assombri, lisible sur fond clair
        "link": "194,74,16",
        "visited": "110,70,190",
        "negative": "200,40,50",
        "neutral": "176,110,0",
        "positive": "22,128,100",
        "bg": {
            "Window": ("244,244,246", "236,236,239"),
            "View": ("250,250,251", "244,244,246"),   # #FAFAFB
            "Button": ("233,233,235", "222,222,226"),
            "Header": ("244,244,246", "236,236,239"),
            "Header][Inactive": ("250,250,251", "244,244,246"),
            "Tooltip": ("250,250,251", "244,244,246"),
            "Complementary": ("22,22,26", "30,30,35"),
        },
        "wm": ("244,244,246", "250,250,251"),
    },
}


def group(name, bg, alt, fg, fg_inactive, fg_active, s):
    return f"""[Colors:{name}]
BackgroundAlternate={alt}
BackgroundNormal={bg}
DecorationFocus={ACCENT}
DecorationHover={ACCENT}
ForegroundActive={fg_active}
ForegroundInactive={fg_inactive}
ForegroundLink={s['link']}
ForegroundNegative={s['negative']}
ForegroundNeutral={s['neutral']}
ForegroundNormal={fg}
ForegroundPositive={s['positive']}
ForegroundVisited={s['visited']}

"""


def scheme(scheme_id, s):
    out = """# Généré par tools/make-color-schemes.py : ne pas modifier à la main.

[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

"""
    for name, (bg, alt) in s["bg"].items():
        if name == "Complementary" and scheme_id == "AubeLight":
            # Zones complémentaires (écran de verrouillage, OSD) : toujours sombres.
            dark = SCHEMES["AubeDark"]
            out += group(name, bg, alt, dark["fg"], dark["fg_inactive"], ACCENT, dark)
        else:
            out += group(name, bg, alt, s["fg"], s["fg_inactive"], s["fg_active"], s)
    # Sélection : pilule accent, texte foncé.
    out += group("Selection", ACCENT, "230,100,45", ON_ACCENT, "80,40,20", ON_ACCENT,
                 {**s, "link": ON_ACCENT, "visited": ON_ACCENT})
    wm_bg, wm_inactive = s["wm"]
    out += f"""[General]
ColorScheme={scheme_id}
Name={s['name']}
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={wm_bg}
activeBlend={s['fg']}
activeForeground={s['fg']}
inactiveBackground={wm_inactive}
inactiveBlend={s['fg_inactive']}
inactiveForeground={s['fg_inactive']}
"""
    return out


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for scheme_id, s in SCHEMES.items():
        (out / f"{scheme_id}.colors").write_text(scheme(scheme_id, s))


if __name__ == "__main__":
    main()

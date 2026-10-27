#!/usr/bin/env bash
# Essai rapide du thème Plasma « aube » dans une VM, sans rebâtir l'image.
#
# Génère le thème sur ce poste, le copie dans ~/.local/share/plasma/desktoptheme
# de l'utilisateur de la VM (prioritaire sur celui de l'image) et l'applique
# à sa session Plasma ouverte.
#
# Usage :
#   tools/try-theme.sh aube@192.168.0.50          essayer le thème du dépôt
#   tools/try-theme.sh aube@192.168.0.50 --reset  revenir au thème de l'image
set -euo pipefail

cible="${1:?usage : tools/try-theme.sh utilisateur@ip [--reset]}"
dossier='.local/share/plasma/desktoptheme'
# plasma-apply-desktoptheme doit joindre la session Plasma de l'utilisateur,
# et tourner sans écran (en SSH, Qt s'arrête net s'il en cherche un).
session='export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus QT_QPA_PLATFORM=offscreen'

if [[ "${2:-}" == "--reset" ]]; then
    ssh "$cible" "rm -rf ~/$dossier/aube ~/$dossier/aube-test ~/.cache/ksvg* ~/.cache/plasma_theme_* ~/.cache/plasma-svgelements*; $session; plasma-apply-desktoptheme breeze-dark >/dev/null; plasma-apply-desktoptheme aube"
    exit
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
outils=$(dirname "$0")

python3 "$outils/make-plasma-theme.py" "$tmp/aube"
python3 "$outils/make-color-schemes.py" "$tmp/couleurs"
cp "$tmp/couleurs/AubeDark.colors" "$tmp/aube/colors"

# Vider aussi le cache des éléments SVG : sinon Plasma garde les tailles et
# les masques de la version précédente du thème.
ssh "$cible" "rm -rf ~/$dossier/aube ~/.cache/ksvg* ~/.cache/plasma_theme_* ~/.cache/plasma-svgelements* && mkdir -p ~/$dossier"
scp -rq "$tmp/aube" "$cible:$dossier/aube"
# Passer par un autre thème force Plasma à tout relire.
ssh "$cible" "$session; plasma-apply-desktoptheme breeze-dark >/dev/null; plasma-apply-desktoptheme aube"

# Aube — image bootc basée sur Fedora Kinoite (KDE Plasma)
#
# Build local :
#   podman build -t localhost/aube:latest .

# Version de Fedora : « latest » de Kinoite pointe sur la dernière stable (44).
ARG FEDORA_VERSION=44

# --- Étape 1 : générer les fichiers d'image de marque ------------------------
# Fond d'écran, schémas de couleurs et icônes PNG, à partir des sources de
# branding/ et tools/. Rien de binaire n'est stocké dans le dépôt.
FROM registry.fedoraproject.org/fedora:${FEDORA_VERSION} AS assets

RUN dnf -y install python3-numpy python3-pillow librsvg2-tools && \
    dnf clean all

COPY branding/ /src/branding/
COPY tools/ /src/tools/

RUN python3 /src/tools/make-wallpaper.py /out/usr/share/wallpapers/Aube && \
    python3 /src/tools/make-color-schemes.py /out/usr/share/color-schemes && \
    for s in 16 22 24 32 48 64 128 256 512; do \
        d=/out/usr/share/icons/hicolor/${s}x${s}/apps; mkdir -p "$d"; \
        rsvg-convert -w "$s" -h "$s" /src/branding/aube-icon.svg -o "$d/aube-logo.png"; \
    done

# --- Étape 2 : l'image Aube --------------------------------------------------
FROM quay.io/fedora/fedora-kinoite:${FEDORA_VERSION}

ARG FEDORA_VERSION
# Version d'Aube au format AA.MM ; calculée à la date du build si absente.
ARG AUBE_VERSION

LABEL org.opencontainers.image.title="Aube" \
      org.opencontainers.image.description="Aube — une distro Linux grand public basée sur Fedora Kinoite" \
      org.opencontainers.image.licenses="Apache-2.0"

# 1. Polices Geist et Geist Mono (OFL), empaquetées par Fedora.
RUN dnf -y install vercel-geist-fonts vercel-geist-mono-fonts && \
    dnf clean all

# 2. Codecs multimédia complets via RPM Fusion (free + nonfree).
#    - ffmpeg-free -> ffmpeg (H.264, H.265, AAC, etc.)
#    - greffons GStreamer complets
#    - openh264 de Cisco à la place du paquet vide noopenh264
#    - décodage matériel : pilote Intel complet (nonfree) et pont VA-API NVIDIA
#    Pas de mesa-va-drivers-freeworld : depuis Fedora 44, mesa-va-drivers est
#    fusionné dans mesa-dri-drivers et le swap retire mesa (et tout Plasma).
RUN dnf -y install \
        "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm" \
        "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm" && \
    dnf -y swap ffmpeg-free ffmpeg --allowerasing && \
    dnf -y swap noopenh264 openh264 && \
    dnf -y swap libva-intel-media-driver intel-media-driver && \
    dnf -y install \
        gstreamer1-plugins-bad-freeworld \
        gstreamer1-plugins-ugly \
        gstreamer1-plugin-openh264 \
        mozilla-openh264 \
        libva-nvidia-driver && \
    dnf clean all

# Garde-fou : le build échoue si un swap a retiré un paquet essentiel.
RUN rpm -q plasma-workspace mesa-dri-drivers dolphin firefox \
        ffmpeg ffmpeg-libs openh264 intel-media-driver \
        vercel-geist-fonts vercel-geist-mono-fonts

# 3. Flathub par défaut, à la place des Flatpaks de Fedora.
#    Remote « statique » : lu par Flatpak et Discover dès le premier démarrage.
RUN mkdir -p /etc/flatpak/remotes.d && \
    curl -fsSL https://dl.flathub.org/repo/flathub.flatpakrepo \
        -o /etc/flatpak/remotes.d/flathub.flatpakrepo && \
    systemctl disable flatpak-add-fedora-repos.service

# 4. Identité : Aube dans os-release (À propos, terminal, Plasma Setup).
#    ID et VERSION_ID restent « fedora » / 44 : bootc-image-builder et
#    toolbox s'en servent pour reconnaître la base.
RUN AUBE_VERSION="${AUBE_VERSION:-$(date -u +%y.%m)}" && \
    sed -i \
        -e "s|^NAME=.*|NAME=\"Aube\"|" \
        -e "s|^VERSION=.*|VERSION=\"${AUBE_VERSION} (Fedora ${FEDORA_VERSION})\"|" \
        -e "s|^PRETTY_NAME=.*|PRETTY_NAME=\"Aube ${AUBE_VERSION}\"|" \
        -e "s|^ANSI_COLOR=.*|ANSI_COLOR=\"38;2;255;122;61\"|" \
        -e "s|^LOGO=.*|LOGO=aube-logo|" \
        -e "s|^DEFAULT_HOSTNAME=.*|DEFAULT_HOSTNAME=\"aube\"|" \
        -e "s|^HOME_URL=.*|HOME_URL=\"https://github.com/pierrecharlesdery-cmd/AubeOS\"|" \
        -e "s|^BUG_REPORT_URL=.*|BUG_REPORT_URL=\"https://github.com/pierrecharlesdery-cmd/AubeOS/issues\"|" \
        /usr/lib/os-release && \
    printf 'IMAGE_ID=aube\nIMAGE_VERSION=%s\nBUILD_ID=%s\n' \
        "${AUBE_VERSION}" "$(date -u +%Y%m%d)" >> /usr/lib/os-release

# 5. Fichiers d'image de marque générés à l'étape 1.
COPY --from=assets /out/ /

# 6. Fichiers système (configuration Plasma, thème global Aube, fontconfig).
COPY system_files/ /

# Nettoyage et validation de l'image bootc.
RUN gtk-update-icon-cache -f -t /usr/share/icons/hicolor && \
    rm -rf /var/cache/* /var/log/* /var/lib/dnf /tmp/* /run/dnf && \
    bootc container lint

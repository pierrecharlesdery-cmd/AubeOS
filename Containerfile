# Aube — image bootc basée sur Fedora Kinoite (KDE Plasma)
#
# Build local :
#   podman build -t localhost/aube:latest .

# Version de Fedora : « latest » de Kinoite pointe sur la dernière stable (44).
ARG FEDORA_VERSION=44
FROM quay.io/fedora/fedora-kinoite:${FEDORA_VERSION}

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

# 3. Fichiers système (configuration Plasma, thème global Aube, fontconfig).
COPY system_files/ /

# Nettoyage et validation de l'image bootc.
RUN rm -rf /var/cache/* /var/log/* /var/lib/dnf /tmp/* /run/dnf && \
    bootc container lint

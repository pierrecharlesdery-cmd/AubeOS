# Aube

Aube est une distribution Linux grand public basée sur **Fedora Kinoite** (KDE Plasma), livrée comme image atomique **bootc**.
Le système est une image de conteneur : on la bâtit avec un `Containerfile`, on la publie sur `ghcr.io`, et les machines s'y mettent à jour avec retour arrière possible.

Le guide visuel est dans [DESIGN.md](DESIGN.md) et les maquettes dans [Docs/Mockups](Docs/Mockups).

## Contenu de l'image

- Base : `quay.io/fedora/fedora-kinoite:44` (dernière version stable)
- Polices **Geist** et **Geist Mono** (OFL), par défaut dans Plasma et via fontconfig
- Codecs multimédia complets (RPM Fusion) : `ffmpeg`, greffons GStreamer, `openh264`, pilote VA-API Intel complet, pont VA-API NVIDIA
- Thème global **Aube** (`org.aube.desktop`), mis par défaut dans `/etc/xdg` :
  - thème sombre (Breeze sombre pour l'instant)
  - barre des tâches flottante, centrée en bas, ajustée à son contenu

## Structure

```
Containerfile                 Recette de l'image
system_files/                 Copié tel quel à la racine de l'image
  etc/xdg/kdeglobals          Police, couleurs et thème global par défaut
  etc/xdg/plasmarc            Thème Plasma sombre
  etc/fonts/local.conf        Geist pour les applis hors Qt
  usr/share/plasma/look-and-feel/org.aube.desktop/
                              Thème global Aube et mise en page par défaut (layout.js)
.github/workflows/build.yml   Build et publication sur ghcr.io
```

Les réglages de `/etc/xdg` et le script de mise en page ne touchent que les **nouveaux** utilisateurs, au premier lancement de Plasma. Un compte existant garde sa configuration (`~/.config`).

## Bâtir localement

```bash
podman build -t localhost/aube:latest .
```

Le build se termine par `bootc container lint`, qui valide l'image, et par un garde-fou qui échoue si un paquet essentiel a disparu.

## Publication

À chaque poussée sur `main`, chaque jour à 6 h UTC et sur demande, GitHub Actions bâtit l'image et la publie :

```
ghcr.io/<propriétaire>/aube:latest
ghcr.io/<propriétaire>/aube:44
ghcr.io/<propriétaire>/aube:44-AAAAMMJJ
```

Après le premier build, rendez le paquet public dans GitHub (Packages → aube → Package settings) pour pouvoir le tirer sans authentification.

## Générer une image disque pour une VM

On utilise [bootc-image-builder](https://github.com/osbuild/bootc-image-builder). Il doit tourner en **root** (`sudo podman`) et lit l'image dans le stockage de root.

### 1. Mettre l'image dans le stockage de root

L'image bâtie sans sudo vit dans le stockage de votre utilisateur. On la copie :

```bash
podman save localhost/aube:latest | sudo podman load
```

(Ou, une fois l'image publiée : `sudo podman pull ghcr.io/<propriétaire>/aube:latest`.)

### 2. Créer `config.toml` (ignoré par git)

```toml
[[customizations.user]]
name = "aube"
password = "changez-moi"
key = "ssh-ed25519 AAAA... vous@machine"
groups = ["wheel"]
```

### 3. Lancer le build

qcow2 (disque prêt à démarrer) :

```bash
mkdir -p output
sudo podman run --rm -it --privileged --pull=newer \
  --security-opt label=type:unconfined_t \
  -v ./config.toml:/config.toml:ro \
  -v ./output:/output \
  -v /var/lib/containers/storage:/var/lib/containers/storage \
  quay.io/centos-bootc/bootc-image-builder:latest \
  --type qcow2 --rootfs btrfs \
  localhost/aube:latest
```

Résultat : `output/qcow2/disk.qcow2`. Pour un installateur, remplacez `--type qcow2` par `--type anaconda-iso` (résultat : `output/bootiso/install.iso`).

### 4. Importer dans Proxmox

Copiez le disque sur l'hôte Proxmox, puis (en adaptant l'ID `900` et le stockage `local-lvm`) :

```bash
scp output/qcow2/disk.qcow2 root@proxmox:/var/lib/vz/images/aube.qcow2
```

Sur l'hôte Proxmox :

```bash
qm create 900 --name aube --machine q35 --bios ovmf \
  --cores 4 --memory 8192 --cpu host \
  --net0 virtio,bridge=vmbr0 --vga virtio \
  --scsihw virtio-scsi-pci \
  --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0 \
  --scsi0 local-lvm:0,import-from=/var/lib/vz/images/aube.qcow2 \
  --boot order=scsi0 --agent enabled=1
qm disk resize 900 scsi0 +30G
qm start 900
```

Pour l'ISO : téléversez `install.iso` dans le stockage ISO de Proxmox, attachez-la en lecteur CD à une VM avec un disque vide, et démarrez dessus.

### 5. Mises à jour dans la VM

```bash
sudo bootc status
sudo bootc upgrade        # puis redémarrer
sudo bootc rollback       # revenir à l'image précédente
```

Un système installé depuis une image locale (`localhost/aube`) ne sait pas où trouver les mises à jour. Pointez-le une fois vers le registre :

```bash
sudo bootc switch ghcr.io/<propriétaire>/aube:latest
```

## Limites connues

- **Décodage vidéo matériel AMD (H.264/HEVC)** : depuis Fedora 44, `mesa-va-drivers` est intégré à `mesa-dri-drivers`, et `mesa-va-drivers-freeworld` de RPM Fusion retire mesa (et tout Plasma) à l'installation. On le laisse de côté pour l'instant ; le décodage logiciel fonctionne.
- Le thème est encore Breeze sombre : le schéma de couleurs, le thème Plasma et le style en pilules d'Aube viendront ensuite.

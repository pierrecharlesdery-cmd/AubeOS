# Aube — guide de design

Source de vérité visuelle du projet. Les maquettes de référence sont dans `docs/mockups/` (bureau, mode sombre, verrouillage, installateur, mises à jour). En cas de doute, la maquette a raison.

## Principes

1. **Moderne et calme.** Interface en noir et blanc, beaucoup d'espace et une seule couleur d'accent, utilisée avec parcimonie.
2. **Pilules partout.** Boutons, champs, filtres, navigation, barre des tâches et notifications ont des coins entièrement arrondis. Aucun bouton à coins carrés.
3. **Pas de crochets.** Les cases à cocher deviennent des interrupteurs en pilule, et les listes d'étapes cochées deviennent des barres de progression en pilules.
4. **Effet verre sur la « coque » seulement.** La barre des tâches, la barre du haut, le lanceur, les notifications et les barres latérales sont translucides. Le contenu des fenêtres reste lisible, presque opaque.
5. **Aucun cliché.** Pas de petites tuiles d'icônes pastel, pas d'emoji, pas de dégradés décoratifs dans l'interface (le fond d'écran est la seule exception).

## Typographie

| Rôle | Police | Graisse | Taille indicative |
|---|---|---|---|
| Interface (général) | Geist | 400 / 500 | 10 pt (~14 px) |
| Titres de fenêtres et de pages | Geist | 600, interlettrage serré (-1 à -2 px) | 28 à 52 px |
| Petit texte, métadonnées, heure de la barre du haut | Geist Mono | 400 | 9 à 10 pt |
| Horloge de l'écran de verrouillage | Geist | 600, interlettrage très serré (-10 px) | ~200 px |

Les deux polices sont sous licence OFL : on les intègre dans l'image.

## Couleurs

### Mode clair
| Jeton | Valeur | Usage |
|---|---|---|
| texte | `#111113` | Texte principal, boutons principaux (fond) |
| texte-secondaire | `#52525B` | Descriptions |
| texte-discret | `#71717A` | Métadonnées |
| surface-fenêtre | `rgba(250,250,251,0.86)` + flou | Fond des fenêtres |
| surface-latérale | `rgba(255,255,255,0.40)` | Barres latérales |
| contrôle-neutre | `rgba(17,17,19,0.07)` | Boutons secondaires, champ de recherche |
| filet | `rgba(17,17,19,0.08)` | Séparateurs |
| sélection | `#111113` avec texte `#FAFAFA` | Élément actif de la navigation (pilule noire) |

### Mode sombre
| Jeton | Valeur |
|---|---|
| fond | `#07070A` |
| surface-verre | `rgba(28,28,32,0.62)` + flou |
| texte | `#FAFAFA` |
| texte-secondaire | `#A1A1AA` |
| bordure | `rgba(255,255,255,0.12)` |

### Accent
- Par défaut : orange aube `#FF7A3D`, toujours avec du texte foncé `#1C0D04` par-dessus (jamais de texte blanc).
- Variantes offertes dans les paramètres : `#8B9CFF` (indigo), `#4FD1B5` (sarcelle), `#FF6B8A` (rose).
- Usages permis seulement : bouton du menu Aube, pastilles de nombre, curseur des interrupteurs, étape en cours, version en cours, réglages rapides actifs, icône de notification.

## Formes et dimensions

| Élément | Valeur |
|---|---|
| Boutons, champs, filtres, éléments de navigation | rayon 999 (pilule) |
| Fenêtres | rayon 28 px |
| Cartes | rayon 24 px |
| Hauteur des boutons | 36 à 48 px |
| Cibles cliquables | 44 px minimum |
| Icônes | contour, trait 1,75, monochromes, 20 à 22 px |
| Bordure des panneaux de verre | 1 px blanc, 12 à 55 % d'opacité |
| Flou | 30 à 40 px, saturation 160 à 180 % |
| Ombre des fenêtres | grande et douce (0 30 80 px, noir 35 %) |

## Composants clés

- **Barre du haut :** 34 px, translucide sombre. À gauche, le mot « aube » et le nom de l'appli active. À droite, le Wi-Fi, la batterie et l'heure en Geist Mono.
- **Barre des tâches :** pilule flottante centrée en bas, 64 px de haut, verre sombre. Boutons ronds de 48 px. Le bouton du menu Aube est un cercle de couleur accent. L'appli active a un cercle blanc translucide derrière son icône.
- **Notifications :** pilule sombre en haut au centre, avec une icône ronde accent, une phrase courte et un bouton pilule blanc.
- **Lanceur :** grande barre de recherche pilule (64 px) au centre, résultats en pilules, réglages rapides en pilules (accent quand actifs, contour quand inactifs).
- **Interrupteurs :** pilule noire de 56 × 34 px avec un rond accent, à la place des cases à cocher.
- **Écran de verrouillage :** date en Geist Mono majuscules, horloge géante, champ de mot de passe en pilule de verre avec l'avatar à gauche et un bouton rond accent à droite.

## Fond d'écran

Fond `#0D0D12` avec une lueur de lever de soleil floutée en bas (`#F2622E`, puis `#FFC48A` au centre) et une lueur indigo `#3B2A8F` en haut à gauche. Version sombre : mêmes formes, plus sourdes (`#7A2A12`, `#2A1F6E`). À générer en PNG 4K.

## Où ça vit dans Plasma

| Élément | Mécanisme |
|---|---|
| Couleurs | Schéma de couleurs `AubeLight.colors` et `AubeDark.colors` |
| Barre du haut, barre des tâches, notifications, lanceur | Thème Plasma (SVG) + mise en page par défaut (`layout.js`) |
| Boutons et champs en pilule dans les applis Qt | Fork du style Breeze, ou Kvantum en première étape |
| Coins de fenêtres de 28 px | Décoration de fenêtres + effet KWin de coins arrondis |
| Flou et translucidité | Effet de flou de KWin, activé par défaut |
| Écran de connexion et de verrouillage | Thème SDDM et thème de verrouillage en QML |
| Installateur | Habillage QML de Calamares |
| Applis GTK et Flatpak | Thème GTK assorti, plus sa version Flatpak |
| Tout regrouper | Thème global « Aube », mis par défaut dans `/etc/xdg` |

## Accessibilité

- Contraste de 4,5:1 minimum pour tout le texte, y compris sur le verre.
- Anneau de focus visible de 2 px pour la navigation au clavier.
- Respect des réglages « réduire la transparence » (verre remplacé par des surfaces opaques) et « réduire les animations ».

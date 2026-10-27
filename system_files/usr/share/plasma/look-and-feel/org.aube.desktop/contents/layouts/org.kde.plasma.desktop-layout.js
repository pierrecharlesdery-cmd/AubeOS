// Mise en page par défaut d'Aube, exécutée au premier démarrage de Plasma
// pour chaque nouvel utilisateur. Référence : Docs/Mockups/Bureau et logithèque.png

// --- Barre du haut : « aube » et l'appli active à gauche, état et heure à droite.
var topBar = new Panel;
topBar.location = "top";
topBar.height = 34;
topBar.floating = false;
topBar.lengthMode = "fill";
topBar.hiding = "none";

var mark = topBar.addWidget("org.kde.plasma.kickoff");
mark.currentConfigGroup = ["General"];
mark.writeConfig("icon", "aube-mark");
mark.writeConfig("menuLabel", "aube");

topBar.addWidget("org.kde.plasma.windowlist");
topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");

var clock = topBar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateDisplayFormat", 1);        // à côté de l'heure
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd d");   // « mar. 27 »
clock.writeConfig("use24hFormat", 2);             // toujours 24 h
clock.writeConfig("autoFontAndSize", false);
clock.writeConfig("fontFamily", "Geist Mono");
clock.writeConfig("fontWeight", 400);
clock.writeConfig("fontSize", 10);

// --- Dock : pilule flottante, centrée en bas, ajustée à son contenu.
var dock = new Panel;
dock.location = "bottom";
dock.height = 64;
dock.floating = true;
dock.alignment = "center";
dock.lengthMode = "fit";
dock.hiding = "none";

var launcher = dock.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "aube-launcher");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "preferred://filemanager",
    "preferred://browser",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
]);

// Fond d'écran Aube sur chaque bureau (version claire ou sombre selon le thème).
var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image";
    desktopsArray[j].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktopsArray[j].writeConfig("Image", "file:///usr/share/wallpapers/Aube/");
}

# Changelog — Game Support Tracker

Toutes les modifications notables de ce projet sont documentées ici.

---

v1.3 — What's new / Nouveautés
<details open>
<summary>En</summary>

### Bug Fixes

  - Status bar game counter : _steam_bases and _playnite_bases were incorrectly included in the game count displayed after loading the cache — now excluded
  - Context menu not translated : "Copy" and "Copy line" entries in the right-click menu were hardcoded in French regardless of the selected language — now use the translation system

### New

  - Owned games shown first in the changes panel : when changes are detected, games you own (Steam, Playnite, or manually marked) now appear at the top of the Latest Changes list

### Translations

  - col_owned and filter_owned labels are now properly translated in French (Possédé)
New translation keys added: copy, copy_line (right-click context menu)

</details>
<details>
<summary>Fr</summary>

### Corrections de bugs

  - Compteur de jeux dans la barre de statut : _steam_bases et _playnite_bases étaient incorrectement inclus dans le compteur de jeux affiché après le chargement du cache — désormais exclus
  - Menu contextuel non traduit : les entrées "Copier" et "Copier la ligne" du clic droit étaient codées en dur en français quelle que soit la langue sélectionnée — utilisent maintenant le système de traduction

### Ajout

  - Jeux possédés affichés en premier dans le panneau des changements : lors de la détection de changements, les jeux que vous possédez (Steam, Playnite, ou marqués manuellement) apparaissent maintenant en haut de la liste Derniers changements

### Traductions

  - Les labels col_owned et filter_owned sont maintenant correctement traduits en français (Possédé)
  - Nouvelles clés de traduction ajoutées : copy, copy_line (menu contextuel clic droit)

</details>

## [v1.2]

###  Ajouts
- **Intégration Playnite** : import de bibliothèque depuis un fichier de sauvegarde Playnite (`.zip`)
  - Détection automatique des jeux possédés via le format LiteDB interne (`library/games.db`)
  - Guide pas-à-pas intégré dans les paramètres pour créer la sauvegarde
  - Bouton de navigation pour sélectionner le fichier + bouton de suppression du cache
- **Jeux possédés manuellement (Edit Owned)** : nouveau mode d'édition dans la barre de filtres
  - Cocher/décocher directement les jeux dans la colonne *Owned* du tableau
  - La sélection est persistée dans les paramètres entre les sessions
- **Historique des changements** : sauvegarde des N dernières sessions de vérification
  - Section *History* collapsible en bas du panneau gauche
  - Nombre de sessions conservées configurable (1 à 50) dans les paramètres
- **Bouton Annuler** : possibilité d'interrompre proprement un check en cours
  - Les données partiellement récupérées sont conservées dans le cache
- **Onglet "All Games"** : vue unifiée qui agrège tous les onglets (*Playable Worlds*, *Core Verified*…) dans un seul tableau
- **License MIT** : ajout de la licence au projet
- **Fichiers de langue** : ajout des clés `cell_yes` / `cell_no` (Oui/Non) dans les fichiers YAML

###  Modifications
- **Bouton ⚙ repositionné** : déplacé à côté du titre (à gauche) au lieu d'être collé au bouton de vérification
- **Fenêtre Paramètres améliorée** :
  - Scrollable avec hauteur maximale dynamique (75 % de l'écran)
  - Entièrement redimensionnable
  - Labels avec retour à la ligne automatique lorsque le texte dépasse la largeur de la fenêtre
  - Zone de saisie des Steam IDs affichée en entier (hauteur adaptative)
  - Spinbox pour configurer le nombre de sessions d'historique conservées
  - Nouvelle section *Playnite* avec guide étape par étape
- **Bouton ▶ Changes fonctionnel** : masque/affiche le panneau gauche en mémorisant sa largeur
- **Panneau "Derniers changements" restructuré** : suppression du bouton flèche interne, ajout de la section *History* collapsible en bas du panneau
- **Détection d'acronymes améliorée** : filtre les mots courts, seuil à 3+ mots significatifs et 3+ caractères générés pour limiter les faux positifs
  - ex. : *Totally Accurate Battle Simulator* → `TABS`
- **Renommage du projet** : *Archipelago Game Tracker* → *Game Support Tracker*
- **`build.py`** : nettoyage des dossiers `__pycache__` avant compilation pour éviter l'inclusion de bytecode obsolète

## [v1.1]

###  Ajouts
- **Architecture modulaire** : le code principal a été découpé en plusieurs modules dédiés :
  - `cache.py` — gestion du cache et des paramètres
  - `config.py` — constantes globales (couleurs, URLs, statuts…)
  - `data.py` — récupération et parsing des données (Google Sheets, GitHub, PopTracker, Steam)
  - `ui/changes.py` — panneau "Derniers changements"
  - `ui/detail.py` — panneau de détail d'un jeu
  - `ui/settings.py` — fenêtre de paramètres
  - `ui/table.py` — tableau principal et barre de filtres
- **Internationalisation (i18n)** : support multilingue via des fichiers YAML (`lang/en.yaml`, `lang/fr.yaml`) et un module `lang/l18n.py`
  - Langues disponibles : 🇫🇷 Français, 🇬🇧 English
  - Changement de langue depuis les paramètres (redémarrage requis)
- **Colonne APWorld/Client** : nouvelle colonne dans le tableau affichant les liens directs vers les APWorlds ou clients custom d'un jeu
- **Intégration Steam** :
  - Connexion via clé API Steam et Steam ID(s) configurables dans les paramètres
  - Nouvelle colonne *Owned* dans le tableau indiquant les jeux possédés sur Steam
  - Filtre *Owned* pour n'afficher que les jeux possédés (ou non)
  - Support multi-comptes (famille Steam)
- **Vérification des releases GitHub** :
  - Option activable dans les paramètres
  - Récupère la dernière release GitHub de chaque jeu ayant un lien GitHub dans ses notes
  - Affiché dans le panneau de détail avec lien cliquable
  - Support du token GitHub pour dépasser la limite de 60 req/h
- **Fenêtre Paramètres** (⚙) :
  - Token GitHub + activation de la vérification des releases
  - Clé API Steam + Steam ID(s) + bouton de rafraîchissement
  - Sélection de la langue de l'interface
- **Panneau gauche rétractable** : le panneau "Derniers changements" peut être masqué/affiché via le bouton **▶ Changes** dans la barre de filtre
- **Logo** : icône `logo.ico` ajoutée à la fenêtre et à l'exécutable compilé
- **Script de build `build.py`** :
  - Compilation en `.exe` via PyInstaller en un clic
  - Sélection interactive du fichier source
  - Nettoyage automatique des anciens artefacts de build et des caches `__pycache__`
  - Inclus les dossiers `lang/`, `ui/` et `logo.ico` dans l'exécutable
- **Installeur Windows `installer.iss`** (Inno Setup) :
  - Génère `GameSupportTrackerSetup.exe` dans `dist/`
  - Proposé automatiquement à la fin du build (`build.py`)
  - Installation sans droits administrateur (dossier utilisateur)
  - Raccourci bureau optionnel, désinstallation propre

###  Modifications
- Interface principale remaniée : panneau gauche redimensionnable, mise en page générale améliorée
- Fenêtre principale redimensionnable (taille minimale : 1050×600)
- Le panneau de détail affiche maintenant séparément les liens APWorld/Client et les liens des notes
- `README.md` enrichi avec la documentation des paramètres, de l'installeur et du changelog

###  Corrections
- Correction du scroll dans le panneau des changements
- Correction de la normalisation des noms pour la détection PopTracker et Steam
- Correction du build pour inclure correctement les ressources de langue

---

## [1.0.2]

###  Ajouts
- Intégration PopTracker : détection automatique des packs PopTracker disponibles depuis le wiki Archipelago
- Nouveaux filtres dans la barre d'outils (statut, PopTracker)
- Panneau de détail d'un jeu avec liens cliquables dans les notes

---

## [1.0.1]

###  Modifications
- Correction de la gestion du chemin du cache
- Mise à jour de la documentation

---

## [1.0.0]

- Version initiale du projet


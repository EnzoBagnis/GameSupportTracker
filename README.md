# ⬡ Archipelago Game Tracker

> Surveille la liste communautaire des APWorlds Archipelago et te notifie des nouveaux jeux ajoutés, des changements de statut et des retraits.

---

## ⬇️ Téléchargement

**Aucune installation requise.**

Télécharge le `.exe` depuis la page [Releases](https://github.com/EnzoBagnis/ArchipelagoGameTracker/releases/latest) et lance-le directement.

---

## 🚀 Premier lancement

1. **Lance** `ArchipelagoTracker.exe`
2. Clique sur **⟳ Vérifier les mises à jour**
3. L'application récupère les données et les enregistre en cache — c'est ta référence de départ
4. Le panneau "Derniers changements" affiche `0 changement` → **c'est normal**, il n'y a rien à comparer encore !

À partir du **deuxième check**, tu verras uniquement ce qui a changé depuis la dernière vérification.

---

## 🖥️ Interface

| Zone | Description |
|---|---|
| **Panneau gauche** | Historique des changements détectés (ajouts ✅, retraits ❌, statuts 🔄) |
| **Onglets** | Basculer entre *Playable Worlds* et *Core Verified* |
| **Recherche** | Filtrer les jeux par nom, statut ou notes |
| **Filtre statut** | Afficher uniquement Stable, Unstable, In Review… |
| **Panneau de détail** | Cliquer sur un jeu pour voir ses notes et ses **liens cliquables** |

---

## 🎨 Statuts

| Statut | Signification |
|---|---|
| 🟢 **Stable** | Fonctionnel et testé, recommandé pour les multis |
| 🟠 **Unstable** | Jouable mais peut contenir des bugs |
| 🔵 **In Review** | Pull Request ouverte sur le repo officiel |
| 🔴 **Broken on Main** | Ne fonctionne plus avec Archipelago 0.6.2+ |
| 🟣 **APWorld Only** | Disponible uniquement en `.apworld` custom |
| 🟩 **Merged** | Mergé, sera dans la prochaine release officielle |

---

## ❓ FAQ

**Pourquoi 0 changement au premier lancement ?**
> Le premier check crée la référence. Les changements apparaissent à partir du second.

**Où est sauvegardé le cache ?**
> Dans `archipelago_cache.json`, automatiquement créé dans le même dossier que le `.exe`. Ne le supprime pas, sinon tu perds la comparaison.

**Besoin d'installer Python ou quoi que ce soit ?**
> Non. Le `.exe` est autonome, tout est inclus.

---

## 📊 Source des données

Les données proviennent du [Google Sheets communautaire Archipelago](https://docs.google.com/spreadsheets/d/1iuzDTOAvdoNe8Ne8i461qGNucg5OuEoF-Ikqs8aUQZw) maintenu par la communauté.

---

*Made for the [Archipelago Multiworld Randomizer](https://archipelago.gg) community.*

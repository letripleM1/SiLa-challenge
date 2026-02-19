# CSV Analyser — Visualisation Universelle

Application graphique autonome permettant de **charger n'importe quel fichier CSV**
et d'en explorer les données via un tableau de bord interactif complet.

Aucun fichier de données n'est requis au lancement : l'utilisateur choisit son CSV
directement depuis l'interface.

---

## Lancement

```bash
python csv_analyser.py
```

Un bouton **"Charger un CSV"** s'affiche au centre de l'écran au démarrage.

---

## Chargement d'un fichier CSV

- Cliquez sur **"Charger un CSV"** (bouton vert dans la sidebar ou au centre de l'accueil)
- Sélectionnez n'importe quel fichier `.csv` depuis l'explorateur de fichiers
- Le programme détecte automatiquement :
  - Les **colonnes numériques** (utilisées pour les graphiques et statistiques)
  - Les **colonnes catégorielles** (utilisées pour la coloration et le groupement)
- La sidebar se met à jour avec les infos du fichier chargé
- Toutes les pages deviennent disponibles immédiatement

**Compatibilité CSV :** séparateur virgule (`,`) standard.  
Pour les CSV avec point-virgule (`;`), modifiez la ligne `pd.read_csv(path)` en `pd.read_csv(path, sep=';')`.

---

## Interface graphique

### Sidebar gauche
- Bouton de chargement CSV (vert)
- Nom du fichier chargé + statut
- Menu de navigation (8 pages)
- Informations sur le dataset (lignes, colonnes, types)
- Légende des catégories colorées (si colonne catégorielle détectée)
- Bouton **Exporter Dashboard PNG** (dialogue de sauvegarde)

### Pages disponibles

| Page | Description |
|------|-------------|
| **Accueil** | Cartes récapitulatives, nom du fichier, colonnes détectées |
| **Dashboard complet** | 4 graphiques en 2×2 avec les premières variables détectées |
| **Histogramme** | Variable sélectionnable, couleur par catégorie optionnelle |
| **Scatter + Régression** | Axes X et Y sélectionnables, groupement par catégorie optionnel |
| **Heatmap Corrélation** | Toutes les variables numériques (max 10 affichées) |
| **Animation courbes** | Variable et groupement sélectionnables, Pause/Reprendre, export GIF |
| **Statistiques** | 3 onglets : Global / Tableau interactif / Par catégorie |
| **Aperçu données** | Tableau interactif des 200 premières lignes, scroll horizontal et vertical |

### Contrôles interactifs
Les pages **Histogramme**, **Scatter** et **Animation** disposent d'une barre de contrôle
permettant de choisir les colonnes à afficher, puis de cliquer sur **Afficher / Animer**
pour mettre à jour le graphique sans recharger la page.

---

## Fonctionnement avec différents types de CSV

Le programme s'adapte automatiquement à la structure du fichier :

- **CSV avec colonnes catégorielles** → palette de couleurs automatique, groupement disponible
- **CSV 100 % numérique** → graphiques sans groupement, catégorie désactivée
- **CSV large (nombreuses colonnes)** → heatmap limitée aux 10 premières variables numériques, aperçu scrollable
- **Valeurs manquantes** → gérées via `.dropna()` pour chaque calcul

---

## Page Statistiques — 3 onglets

**Global** — Pour chaque variable numérique :
Moyenne, Médiane, Écart-type, Min, Max, Q1, Q3, IQR, nombre de valeurs nulles

**Tableau interactif** — `ttk.Treeview` avec toutes les variables en lignes et
toutes les statistiques en colonnes, cliquable et scrollable

**Par catégorie** — `describe()` complet par groupe pour chaque colonne catégorielle détectée

---

## Export

| Action | Résultat |
|--------|---------|
| Bouton **Exporter Dashboard PNG** | Dialogue de sauvegarde → `.png` haute résolution |
| Bouton **Exporter GIF** (animation) | `export_animated.gif` dans le dossier courant |

---

## Prérequis

Python 3.8 ou supérieur avec tkinter (inclus par défaut sur Windows et macOS).

**Linux** :
```bash
sudo apt install python3-tk    # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora
```

Dépendances Python :
```bash
pip install pandas numpy matplotlib seaborn scipy pillow
```

---

## Dépendances

| Bibliothèque | Rôle |
|---|---|
| `tkinter` | Interface graphique native |
| `matplotlib` (TkAgg) | Graphiques embarqués |
| `seaborn` | Heatmap de corrélation |
| `pandas` | Lecture CSV, manipulation des données |
| `numpy` | Calculs vectoriels |
| `scipy` | Régression linéaire |
| `pillow` | Export GIF |
| `threading` | Export GIF non bloquant |

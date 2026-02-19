# Iris Dashboard — Visualisation Multi-Graphiques

Application graphique complète construite sur le dataset **Iris** de R.A. Fisher (1936).  
Interface `tkinter` avec graphiques `matplotlib` intégrés, navigation par menu lateral,
animation interactive et export PNG/GIF.

---

## Contenu du projet

```
iris-dashboard/
├── iris_dashboard.py   # Application principale (GUI + graphiques)
├── iris.csv            # Dataset Iris (150 observations)
└── README.md           # Documentation
```

Fichiers générés à l'utilisation :

```
iris_dashboard.png      # Export PNG du dashboard complet
iris_histogramme.png    # Histogramme seul
iris_scatter.png        # Scatter plot + régression
iris_heatmap.png        # Heatmap de corrélation
iris_animated.gif       # Animation des courbes pétales
```

---

## Lancement

```bash
python iris_dashboard.py
```

L'interface graphique s'ouvre automatiquement. `iris.csv` doit être dans le même dossier.

---

## Interface graphique (tkinter)

L'application utilise une architecture à **sidebar + zone de contenu** :

### Sidebar gauche
- Logo et titre de l'application
- Boutons de navigation avec effets hover/actif
- Informations sur le dataset (150 obs., 4 variables, 3 espèces)
- Légende des espèces avec indicateurs colorés
- Bouton **Exporter PNG** (dialogue de sauvegarde)

### Zone de contenu principale
- En-tête dynamique (titre + sous-titre de la page courante)
- Contenu principal adaptatif selon la page sélectionnée
- Barre de statut inférieure

### Navigation
| Page | Contenu |
|------|---------|
| **Accueil** | Cartes récapitulatives, présentation des espèces |
| **Dashboard complet** | 4 graphiques matplotlib en 2×2, barre d'outils intégrée |
| **Histogramme** | Distribution des sépales, lignes de moyenne annotées |
| **Scatter + Régression** | Nuage de points, droite de régression, R², p-value |
| **Heatmap Corrélation** | Matrice de corrélation de Pearson colorisée |
| **Animation courbes** | Tracé animé progressif, bouton Pause, export GIF en thread |
| **Statistiques** | 3 onglets : Global / Par espèce / Tableau interactif |

---

## Page Statistiques — 3 onglets

**Global** — Toutes variables, toutes espèces confondues :
- Moyenne, Médiane, Écart-type, Min, Max, Q1, Q3, IQR

**Par espèce** — `describe()` par espèce (*setosa*, *versicolor*, *virginica*)

**Tableau récapitulatif** — `ttk.Treeview` interactif avec toutes les statistiques,
lignes colorées par espèce

---

## Fonctionnalités techniques

- Graphiques `matplotlib` embarqués dans tkinter via `FigureCanvasTkAgg`
- Barre d'outils `NavigationToolbar2Tk` (zoom, pan, sauvegarde)
- Export GIF exécuté dans un thread séparé (`threading.Thread`) pour ne pas bloquer l'UI
- Export PNG via dialogue `filedialog.asksaveasfilename`
- Animation `FuncAnimation` avec contrôle Pause/Reprendre
- Thème sombre cohérent entre tkinter et matplotlib

---

## Prérequis

Python 3.8 ou supérieur avec tkinter (inclus par défaut sur Windows et macOS).

**Linux** — installer tkinter si absent :
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
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
| `matplotlib` (TkAgg) | Graphiques embarqués dans l'interface |
| `seaborn` | Heatmap de corrélation |
| `pandas` | Chargement et manipulation des données |
| `numpy` | Calculs vectoriels |
| `scipy` | Régression linéaire (`linregress`) |
| `pillow` | Export GIF |
| `threading` | Export GIF non-bloquant |

---

## Dataset

**Iris** — R.A. Fisher, 1936  
150 observations, 3 espèces, 4 variables morphologiques mesurées en centimètres.

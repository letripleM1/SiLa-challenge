# Système Bancaire Orienté Objet

## Description

Ce projet implémente un système bancaire en Python selon les principes de la programmation orientée objet. Il prend en charge trois types de comptes (standard, épargne, professionnel), une authentification par mot de passe haché, des opérations bancaires avec contrôle d'erreurs, un historique horodaté des transactions et une persistance des données au format JSON. Une interface en ligne de commande guide l'utilisateur à travers toutes les opérations.

---

## Structure du projet

```
systeme_bancaire/
├── banque.py       # Code source principal (classes + interface CLI)
├── banque.json     # Fichier de données généré automatiquement à l'exécution
└── README.md       # Ce fichier
```

---

## Prérequis

- Python 3.8 ou supérieur
- Aucune bibliothèque externe requise (utilisation de `json`, `hashlib`, `datetime`, `getpass` — tous inclus dans la bibliothèque standard)

---

## Lancement

```bash
python banque.py
```

---

## Classes

### `Compte` (classe de base)

**Attributs :**
- `titulaire` : nom du titulaire
- `numero` : identifiant unique du compte
- `mot_de_passe` : mot de passe haché en SHA-256
- `solde` : solde courant en euros
- `historique` : liste des transactions horodatées

**Méthodes :**
- `deposer(montant)` : crédite le compte
- `retirer(montant)` : débite le compte (lève `SoldeInsuffisantError` si solde insuffisant)
- `virement(montant, compte_destinataire)` : transfère un montant vers un autre compte avec annulation automatique en cas d'échec ; enregistre l'opération distinctement dans les deux historiques
- `verifier_mot_de_passe(mdp)` : compare le mot de passe saisi (haché) avec celui stocké
- `to_dict()` : sérialise le compte en dictionnaire pour la persistance JSON

---

### `CompteEpargne` (hérite de `Compte`)

**Attributs supplémentaires :**
- `taux_interet` : taux annuel (ex. `0.02` pour 2 %)

**Méthodes supplémentaires :**
- `appliquer_interets()` : calcule et crédite les intérêts sur le solde courant

---

### `ComptePro` (hérite de `Compte`)

**Attributs supplémentaires :**
- `decouvert_autorise` : montant maximum de découvert autorisé

**Méthodes redéfinies :**
- `retirer(montant)` : autorise un retrait jusqu'à `-decouvert_autorise` ; lève `PlafondDepasserError` si dépassement

---

### `Banque`

Gère l'ensemble des comptes et la persistance des données.

**Méthodes :**
- `ajouter_compte(compte)` : enregistre un nouveau compte (vérifie l'unicité du numéro)
- `trouver_compte(numero)` : retourne le compte correspondant ou `None`
- `supprimer_compte(numero)` : supprime un compte existant
- `sauvegarder(chemin)` : exporte tous les comptes dans un fichier JSON
- `charger(chemin)` : importe les comptes depuis un fichier JSON

---

## Exceptions personnalisées

| Exception | Déclenchement |
|---|---|
| `SoldeInsuffisantError` | Retrait sur `Compte` ou `CompteEpargne` avec solde insuffisant |
| `PlafondDepasserError` | Retrait sur `ComptePro` dépassant le découvert autorisé |

---

## Interface utilisateur

### Menu principal

| Option | Action |
|---|---|
| 1. Créer un compte | Saisie des informations, choix du type, solde initial et paramètres spécifiques |
| 2. Se connecter | Authentification par numéro et mot de passe masqué |
| 3. Quitter | Ferme le programme |

### Menu du compte (après connexion)

| Option | Action |
|---|---|
| 1. Dépôt | Crédite le solde |
| 2. Retrait | Débite le solde avec contrôle des exceptions |
| 3. Virement | Transfère vers un autre compte existant |
| 4. Voir l'historique | Affiche toutes les transactions (date, type, montant, solde après) |
| 5. Appliquer les intérêts *(épargne uniquement)* | Calcule et crédite les intérêts |
| 5 / 6. Supprimer ce compte | Demande confirmation puis supprime définitivement |
| 6 / 7. Se déconnecter | Retour au menu principal |

Chaque opération modifiant le solde déclenche une sauvegarde automatique dans `banque.json`.

---

## Sécurité

- Les mots de passe sont hachés en **SHA-256** avant stockage ; ils ne sont jamais enregistrés en clair.
- La vérification se fait par comparaison des empreintes SHA-256.
- Toutes les entrées numériques sont validées avant traitement.
- Un virement vers le même compte est bloqué.
- La confirmation de mot de passe est demandée à la création du compte.

---

## Persistance JSON

Les données sont sauvegardées dans `banque.json`. Chaque compte est stocké avec son type, ses attributs, son mot de passe haché et son historique complet.

Exemple de structure :

```json
[
    {
        "type": "Compte",
        "titulaire": "Alice",
        "numero": "FR123",
        "mot_de_passe": "2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b",
        "solde": 800.0,
        "historique": [
            {
                "date": "2026-02-18T10:00:00",
                "operation": "dépôt",
                "montant": 200.0,
                "solde_apres": 800.0
            }
        ]
    },
    {
        "type": "CompteEpargne",
        "titulaire": "Bob",
        "numero": "FR456",
        "mot_de_passe": "...",
        "solde": 5000.0,
        "taux_interet": 0.03,
        "historique": []
    },
    {
        "type": "ComptePro",
        "titulaire": "Entreprise X",
        "numero": "FR789",
        "mot_de_passe": "...",
        "solde": -200.0,
        "decouvert_autorise": 1000.0,
        "historique": []
    }
]
```

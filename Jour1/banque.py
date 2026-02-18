import json
import hashlib
from datetime import datetime
import getpass


class SoldeInsuffisantError(Exception):
    pass


class PlafondDepasserError(Exception):
    pass


def _hacher(mot_de_passe: str) -> str:
    return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()


class Compte:
    def __init__(self, titulaire: str, numero: str, mot_de_passe: str, solde_initial: float = 0.0, _hache: bool = False):
        if not isinstance(titulaire, str) or not titulaire.strip():
            raise ValueError("Le titulaire doit être une chaîne non vide.")
        if not isinstance(numero, str) or not numero.strip():
            raise ValueError("Le numéro de compte doit être une chaîne non vide.")
        if not isinstance(mot_de_passe, str) or not mot_de_passe.strip():
            raise ValueError("Le mot de passe doit être une chaîne non vide.")
        if not isinstance(solde_initial, (int, float)):
            raise ValueError("Le solde initial doit être un nombre.")
        self.titulaire = titulaire.strip()
        self.numero = numero.strip()
        self.mot_de_passe = mot_de_passe if _hache else _hacher(mot_de_passe)
        self.solde = float(solde_initial)
        self.historique = []

    def _valider_montant(self, montant):
        if not isinstance(montant, (int, float)):
            raise TypeError("Le montant doit être un nombre.")
        if montant <= 0:
            raise ValueError("Le montant doit être strictement positif.")

    def _enregistrer(self, operation: str, montant: float):
        self.historique.append({
            "date": datetime.now().isoformat(timespec="seconds"),
            "operation": operation,
            "montant": round(montant, 2),
            "solde_apres": round(self.solde, 2)
        })

    def deposer(self, montant: float):
        self._valider_montant(montant)
        self.solde += montant
        self._enregistrer("dépôt", montant)

    def retirer(self, montant: float):
        self._valider_montant(montant)
        if self.solde < montant:
            raise SoldeInsuffisantError(
                f"Solde insuffisant : solde actuel {self.solde:.2f} €, retrait demandé {montant:.2f} €."
            )
        self.solde -= montant
        self._enregistrer("retrait", montant)

    def virement(self, montant: float, compte_destinataire: "Compte"):
        if not isinstance(compte_destinataire, Compte):
            raise TypeError("Le destinataire doit être une instance de Compte.")
        if compte_destinataire.numero == self.numero:
            raise ValueError("Impossible d'effectuer un virement vers le même compte.")
        self._valider_montant(montant)
        self.retirer(montant)
        self.historique[-1]["operation"] = f"virement émis vers {compte_destinataire.numero}"
        try:
            compte_destinataire.deposer(montant)
            compte_destinataire.historique[-1]["operation"] = f"virement reçu de {self.numero}"
        except Exception as e:
            self.solde += montant
            self.historique.pop()
            raise e

    def verifier_mot_de_passe(self, mdp: str) -> bool:
        return self.mot_de_passe == _hacher(mdp)

    def __str__(self):
        return f"Compte({self.numero}) | Titulaire : {self.titulaire} | Solde : {self.solde:.2f} €"

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "titulaire": self.titulaire,
            "numero": self.numero,
            "mot_de_passe": self.mot_de_passe,
            "solde": round(self.solde, 2),
            "historique": self.historique
        }


class CompteEpargne(Compte):
    def __init__(self, titulaire: str, numero: str, mot_de_passe: str, solde_initial: float = 0.0, taux_interet: float = 0.01, _hache: bool = False):
        super().__init__(titulaire, numero, mot_de_passe, solde_initial, _hache)
        if not isinstance(taux_interet, (int, float)) or not (0 <= taux_interet <= 1):
            raise ValueError("Le taux d'intérêt doit être compris entre 0 et 1.")
        self.taux_interet = float(taux_interet)

    def appliquer_interets(self):
        interets = round(self.solde * self.taux_interet, 2)
        if interets > 0:
            self.deposer(interets)
            self.historique[-1]["operation"] = "intérêts appliqués"

    def __str__(self):
        return (
            f"CompteEpargne({self.numero}) | Titulaire : {self.titulaire} "
            f"| Solde : {self.solde:.2f} € | Taux : {self.taux_interet * 100:.2f} %"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["taux_interet"] = self.taux_interet
        return data


class ComptePro(Compte):
    def __init__(self, titulaire: str, numero: str, mot_de_passe: str, solde_initial: float = 0.0, decouvert_autorise: float = 500.0, _hache: bool = False):
        if not isinstance(titulaire, str) or not titulaire.strip():
            raise ValueError("Le titulaire doit être une chaîne non vide.")
        if not isinstance(numero, str) or not numero.strip():
            raise ValueError("Le numéro de compte doit être une chaîne non vide.")
        if not isinstance(mot_de_passe, str) or not mot_de_passe.strip():
            raise ValueError("Le mot de passe doit être une chaîne non vide.")
        if not isinstance(solde_initial, (int, float)):
            raise ValueError("Le solde initial doit être un nombre.")
        if not isinstance(decouvert_autorise, (int, float)) or decouvert_autorise < 0:
            raise ValueError("Le découvert autorisé doit être un nombre positif ou nul.")
        self.titulaire = titulaire.strip()
        self.numero = numero.strip()
        self.mot_de_passe = mot_de_passe if _hache else _hacher(mot_de_passe)
        self.solde = float(solde_initial)
        self.historique = []
        self.decouvert_autorise = float(decouvert_autorise)

    def retirer(self, montant: float):
        self._valider_montant(montant)
        if self.solde - montant < -self.decouvert_autorise:
            raise PlafondDepasserError(
                f"Plafond de découvert dépassé : découvert autorisé {self.decouvert_autorise:.2f} €, "
                f"solde actuel {self.solde:.2f} €, retrait demandé {montant:.2f} €."
            )
        self.solde -= montant
        self._enregistrer("retrait", montant)

    def __str__(self):
        return (
            f"ComptePro({self.numero}) | Titulaire : {self.titulaire} "
            f"| Solde : {self.solde:.2f} € | Découvert autorisé : {self.decouvert_autorise:.2f} €"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["decouvert_autorise"] = self.decouvert_autorise
        return data


class Banque:
    _TYPE_MAP = {
        "Compte": Compte,
        "CompteEpargne": CompteEpargne,
        "ComptePro": ComptePro,
    }

    def __init__(self):
        self.comptes = []

    def ajouter_compte(self, compte: Compte):
        if not isinstance(compte, Compte):
            raise TypeError("L'objet doit être une instance de Compte.")
        if self.trouver_compte(compte.numero):
            raise ValueError(f"Un compte avec le numéro '{compte.numero}' existe déjà.")
        self.comptes.append(compte)

    def trouver_compte(self, numero: str):
        for compte in self.comptes:
            if compte.numero == numero:
                return compte
        return None

    def supprimer_compte(self, numero: str):
        compte = self.trouver_compte(numero)
        if not compte:
            raise ValueError(f"Aucun compte trouvé avec le numéro '{numero}'.")
        self.comptes.remove(compte)

    def sauvegarder(self, chemin: str):
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.comptes], f, ensure_ascii=False, indent=4)

    def charger(self, chemin: str):
        with open(chemin, "r", encoding="utf-8") as f:
            data_list = json.load(f)
        self.comptes = []
        for data in data_list:
            type_compte = data.get("type", "Compte")
            cls = self._TYPE_MAP.get(type_compte)
            if cls is None:
                raise ValueError(f"Type de compte inconnu : {type_compte}")
            solde = data.get("solde", 0.0)
            mdp = data["mot_de_passe"]
            if type_compte == "CompteEpargne":
                compte = cls(data["titulaire"], data["numero"], mdp, solde, data.get("taux_interet", 0.01), _hache=True)
            elif type_compte == "ComptePro":
                compte = cls(data["titulaire"], data["numero"], mdp, solde, data.get("decouvert_autorise", 500.0), _hache=True)
            else:
                compte = cls(data["titulaire"], data["numero"], mdp, solde, _hache=True)
            compte.historique = data.get("historique", [])
            self.comptes.append(compte)

    def __str__(self):
        return f"Banque | {len(self.comptes)} compte(s) enregistré(s)"


def _lire_float(invite: str) -> float:
    while True:
        try:
            valeur = input(invite).strip()
            return float(valeur) if valeur else 0.0
        except ValueError:
            print("Valeur invalide. Veuillez entrer un nombre.")


def menu_principal():
    print("\n╔══════════════════════════════╗")
    print("║       SYSTÈME BANCAIRE       ║")
    print("╠══════════════════════════════╣")
    print("║  1. Créer un compte          ║")
    print("║  2. Se connecter             ║")
    print("║  3. Quitter                  ║")
    print("╚══════════════════════════════╝")
    return input("Votre choix : ").strip()


def menu_compte(compte):
    print(f"\n  {compte}")
    print("─" * 36)
    print("  1. Dépôt")
    print("  2. Retrait")
    print("  3. Virement")
    print("  4. Voir l'historique")
    if isinstance(compte, CompteEpargne):
        print("  5. Appliquer les intérêts")
        print("  6. Supprimer ce compte")
        print("  7. Se déconnecter")
    else:
        print("  5. Supprimer ce compte")
        print("  6. Se déconnecter")
    print("─" * 36)
    return input("Votre choix : ").strip()


def creer_compte(banque):
    print("\n--- Création d'un compte ---")
    titulaire = input("Nom du titulaire : ").strip()
    if not titulaire:
        print("Nom invalide.")
        return
    numero = input("Numéro de compte : ").strip()
    if not numero:
        print("Numéro invalide.")
        return
    if banque.trouver_compte(numero):
        print("Ce numéro de compte existe déjà.")
        return
    mot_de_passe = getpass.getpass("Mot de passe : ")
    if not mot_de_passe:
        print("Mot de passe invalide.")
        return
    confirmation = getpass.getpass("Confirmez le mot de passe : ")
    if mot_de_passe != confirmation:
        print("Les mots de passe ne correspondent pas.")
        return
    print("Types disponibles : standard / épargne / pro")
    type_compte = input("Type de compte : ").strip().lower()
    solde_initial = _lire_float("Solde initial (0 par défaut) : ")
    try:
        if type_compte in ("épargne", "epargne"):
            taux = _lire_float("Taux d'intérêt (ex : 0.02 pour 2 %, défaut 0.01) : ")
            if taux == 0.0:
                taux = 0.01
            compte = CompteEpargne(titulaire, numero, mot_de_passe, solde_initial, taux)
        elif type_compte == "pro":
            decouvert = _lire_float("Découvert autorisé (défaut 500) : ")
            if decouvert == 0.0:
                decouvert = 500.0
            compte = ComptePro(titulaire, numero, mot_de_passe, solde_initial, decouvert)
        else:
            compte = Compte(titulaire, numero, mot_de_passe, solde_initial)
        banque.ajouter_compte(compte)
        banque.sauvegarder("banque.json")
        print(f"Compte créé avec succès : {compte}")
    except Exception as e:
        print(f"Erreur lors de la création : {e}")


def connecter(banque):
    print("\n--- Connexion ---")
    numero = input("Numéro de compte : ").strip()
    compte = banque.trouver_compte(numero)
    if not compte:
        print("Compte introuvable.")
        return None
    mot_de_passe = getpass.getpass("Mot de passe : ")
    if compte.verifier_mot_de_passe(mot_de_passe):
        print(f"Connexion réussie. Bienvenue, {compte.titulaire}.")
        return compte
    print("Mot de passe incorrect.")
    return None


def afficher_historique(compte):
    print("\n--- Historique des transactions ---")
    if not compte.historique:
        print("Aucune transaction enregistrée.")
        return
    for i, entry in enumerate(compte.historique, 1):
        print(
            f"  {i:>3}. {entry['date']}  |  "
            f"{entry['operation']:<40}  |  "
            f"{entry['montant']:>10.2f} €  |  "
            f"Solde : {entry['solde_apres']:.2f} €"
        )


def effectuer_depot(compte, banque):
    montant = _lire_float("Montant à déposer : ")
    try:
        compte.deposer(montant)
        banque.sauvegarder("banque.json")
        print(f"Dépôt effectué. Nouveau solde : {compte.solde:.2f} €")
    except Exception as e:
        print(f"Erreur : {e}")


def effectuer_retrait(compte, banque):
    montant = _lire_float("Montant à retirer : ")
    try:
        compte.retirer(montant)
        banque.sauvegarder("banque.json")
        print(f"Retrait effectué. Nouveau solde : {compte.solde:.2f} €")
    except (SoldeInsuffisantError, PlafondDepasserError, ValueError) as e:
        print(f"Erreur : {e}")


def effectuer_virement(compte, banque):
    destinataire_num = input("Numéro du compte destinataire : ").strip()
    destinataire = banque.trouver_compte(destinataire_num)
    if not destinataire:
        print("Compte destinataire introuvable.")
        return
    montant = _lire_float("Montant à virer : ")
    try:
        compte.virement(montant, destinataire)
        banque.sauvegarder("banque.json")
        print(f"Virement effectué. Nouveau solde : {compte.solde:.2f} €")
    except Exception as e:
        print(f"Erreur : {e}")


def supprimer_compte(banque, compte):
    print("\n--- Suppression de compte ---")
    confirmation = input("Êtes-vous sûr de vouloir supprimer ce compte ? (oui/non) : ").strip().lower()
    if confirmation == "oui":
        banque.supprimer_compte(compte.numero)
        banque.sauvegarder("banque.json")
        print("Compte supprimé définitivement.")
        return True
    print("Suppression annulée.")
    return False


def session_compte(compte, banque):
    epargne = isinstance(compte, CompteEpargne)
    while True:
        choix = menu_compte(compte)
        if choix == "1":
            effectuer_depot(compte, banque)
        elif choix == "2":
            effectuer_retrait(compte, banque)
        elif choix == "3":
            effectuer_virement(compte, banque)
        elif choix == "4":
            afficher_historique(compte)
        elif choix == "5" and epargne:
            try:
                compte.appliquer_interets()
                banque.sauvegarder("banque.json")
                print(f"Intérêts appliqués. Nouveau solde : {compte.solde:.2f} €")
            except Exception as e:
                print(f"Erreur : {e}")
        elif (choix == "6" and epargne) or (choix == "5" and not epargne):
            if supprimer_compte(banque, compte):
                break
        elif (choix == "7" and epargne) or (choix == "6" and not epargne):
            print("Déconnexion.")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


def main():
    banque = Banque()
    try:
        banque.charger("banque.json")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")

    while True:
        choix = menu_principal()
        if choix == "1":
            creer_compte(banque)
        elif choix == "2":
            compte = connecter(banque)
            if compte:
                session_compte(compte, banque)
        elif choix == "3":
            print("Au revoir.")
            break
        else:
            print("Choix invalide. Veuillez entrer 1, 2 ou 3.")


if __name__ == "__main__":
    main()

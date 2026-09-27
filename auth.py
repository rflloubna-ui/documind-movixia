"""
Authentification simplifiée (démo pédagogique) : gestion des comptes
utilisateurs stockés localement dans un fichier JSON, mots de passe hashés.

⚠️ Ce système est simplifié à des fins de démonstration (projet de stage).
Il n'est pas conçu pour un usage en production : pas de protection contre
les attaques par force brute, pas de récupération de mot de passe, stockage
local non chiffré du fichier utilisateurs.json.
"""
import json
import hashlib
import os

FICHIER_UTILISATEURS = "utilisateurs.json"


def _hacher(mot_de_passe):
    return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()


def _charger_utilisateurs():
    if not os.path.exists(FICHIER_UTILISATEURS):
        return {}
    with open(FICHIER_UTILISATEURS, "r", encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_utilisateurs(utilisateurs):
    with open(FICHIER_UTILISATEURS, "w", encoding="utf-8") as f:
        json.dump(utilisateurs, f, ensure_ascii=False, indent=2)


def creer_compte(nom, poste, email, mot_de_passe):
    """Crée un nouveau compte. Retourne (succès: bool, message: str)."""
    utilisateurs = _charger_utilisateurs()
    email = email.strip().lower()

    if not nom.strip() or not poste.strip() or not email or not mot_de_passe:
        return False, "Merci de remplir tous les champs."
    if email in utilisateurs:
        return False, "Un compte existe déjà avec cette adresse e-mail."
    if len(mot_de_passe) < 4:
        return False, "Le mot de passe doit contenir au moins 4 caractères."

    utilisateurs[email] = {
        "nom": nom.strip(),
        "poste": poste.strip(),
        "mot_de_passe_hache": _hacher(mot_de_passe),
    }
    _sauvegarder_utilisateurs(utilisateurs)
    return True, "Compte créé avec succès. Tu peux maintenant te connecter."


def authentifier(email, mot_de_passe):
    """Vérifie les identifiants.

    Retourne (True, infos_utilisateur: dict) avec les clés "nom", "poste",
    "email" en cas de succès, ou (False, message_erreur: str) sinon.
    """
    utilisateurs = _charger_utilisateurs()
    email = email.strip().lower()

    if email not in utilisateurs:
        return False, "Adresse e-mail inconnue."
    if utilisateurs[email]["mot_de_passe_hache"] != _hacher(mot_de_passe):
        return False, "Mot de passe incorrect."

    infos = utilisateurs[email]
    return True, {
        "nom": infos.get("nom", ""),
        "poste": infos.get("poste", ""),
        "email": email,
    }
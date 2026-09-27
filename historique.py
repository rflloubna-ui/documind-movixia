"""
Module Historique : journalise localement (fichier JSON) chaque document
traité et chaque e-mail envoyé, pour permettre un suivi (page Historique)
et des statistiques d'usage (page Statistiques).
"""
import json
import os
from datetime import datetime

FICHIER_HISTORIQUE = "historique.json"


def _charger():
    if not os.path.exists(FICHIER_HISTORIQUE):
        return []
    with open(FICHIER_HISTORIQUE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _sauvegarder(entrees):
    with open(FICHIER_HISTORIQUE, "w", encoding="utf-8") as f:
        json.dump(entrees, f, ensure_ascii=False, indent=2)


def enregistrer_document(utilisateur, nom_source, nb_mots, score_final, langue_traduction):
    """Journalise un document traité (résumé + traduction générés)."""
    entrees = _charger()
    entrees.append({
        "type": "document",
        "utilisateur": utilisateur or "Inconnu",
        "nom_source": nom_source,
        "nb_mots": nb_mots,
        "score_final": score_final,
        "langue_traduction": langue_traduction,
        "date": datetime.now().isoformat(timespec="seconds"),
    })
    _sauvegarder(entrees)


def enregistrer_envoi(utilisateur, destinataires, type_contenu):
    """Journalise un e-mail envoyé aux collaborateurs."""
    entrees = _charger()
    entrees.append({
        "type": "envoi",
        "utilisateur": utilisateur or "Inconnu",
        "destinataires": destinataires,
        "type_contenu": type_contenu,
        "date": datetime.now().isoformat(timespec="seconds"),
    })
    _sauvegarder(entrees)


def charger_historique():
    """Retourne toutes les entrées enregistrées, triées du plus récent au plus ancien."""
    entrees = _charger()
    return sorted(entrees, key=lambda e: e["date"], reverse=True)

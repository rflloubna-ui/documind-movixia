"""
Page Historique : liste tous les documents traités et tous les e-mails
envoyés depuis le début de l'utilisation de l'application (toutes
personnes confondues), du plus récent au plus ancien.
"""
import streamlit as st
import pandas as pd
from style import entete_page
from historique import charger_historique

entete_page("🕓", "Historique", "Documents traités et e-mails envoyés")

entrees = charger_historique()

if not entrees:
    st.info("Aucune activité enregistrée pour l'instant.")
    st.stop()

filtre = st.radio(
    "Afficher",
    ["Tout", "Documents traités", "E-mails envoyés"],
    horizontal=True,
)

if filtre == "Documents traités":
    entrees = [e for e in entrees if e["type"] == "document"]
elif filtre == "E-mails envoyés":
    entrees = [e for e in entrees if e["type"] == "envoi"]

lignes = []
for e in entrees:
    if e["type"] == "document":
        lignes.append({
            "Date": e["date"].replace("T", " "),
            "Type": "📄 Document",
            "Utilisateur": e["utilisateur"],
            "Détail": e["nom_source"],
            "Info": f"{e['nb_mots']} mots — score {e['score_final']}/10 — trad. {e['langue_traduction']}",
        })
    else:
        lignes.append({
            "Date": e["date"].replace("T", " "),
            "Type": "📤 Envoi",
            "Utilisateur": e["utilisateur"],
            "Détail": e["type_contenu"],
            "Info": ", ".join(e["destinataires"]),
        })

st.dataframe(pd.DataFrame(lignes), use_container_width=True, hide_index=True)

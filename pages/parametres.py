"""
Page Paramètres : affiche la configuration actuelle du système et
explique comment activer l'envoi automatique d'e-mails.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from agents import MODELE, SEUIL_QUALITE, MAX_ITERATIONS
from style import entete_page

load_dotenv()

entete_page("⚙️", "Paramètres")

st.markdown("**Configuration actuelle du système**")
st.write(f"- Modèle LLM utilisé : `{MODELE}`")
st.write(f"- Seuil de qualité (boucle Rédacteur ↔ Critique) : {SEUIL_QUALITE}/10")
st.write(f"- Nombre maximum d'itérations : {MAX_ITERATIONS}")
st.write("- Langue de traduction : Allemand")

st.divider()
st.markdown("**Envoi automatique d'e-mails**")

gmail_configure = bool(os.environ.get("GMAIL_ADDRESS")) and bool(os.environ.get("GMAIL_APP_PASSWORD"))

if gmail_configure:
    st.success(f"Envoi automatique activé (compte : {os.environ.get('GMAIL_ADDRESS')})")
else:
    st.warning("Envoi automatique non configuré — la page Collaborateurs utilise une solution de secours (mailto).")
    with st.expander("Comment activer l'envoi automatique réel ?"):
        st.markdown("""
        1. Active la validation en deux étapes sur ton compte Gmail (obligatoire pour l'étape suivante).
        2. Va sur **myaccount.google.com/apppasswords** et crée un « mot de passe d'application »
           (choisis par exemple le nom « Streamlit »).
        3. Copie le mot de passe généré (16 caractères).
        4. Ouvre ton fichier `.env` et ajoute ces deux lignes :
           ```
           GMAIL_ADDRESS=ton_adresse@gmail.com
           GMAIL_APP_PASSWORD=le_mot_de_passe_genere
           ```
        5. Redémarre l'application. La page Collaborateurs enverra alors réellement les e-mails.
        """)

st.divider()
st.caption(
    "Ces paramètres sont actuellement définis dans le code (agents.py) et dans le "
    "fichier .env. Une évolution possible serait de les rendre modifiables ici directement."
)
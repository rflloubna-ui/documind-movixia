"""
Page Déconnexion : met fin à la session de l'utilisateur connecté
et le ramène à l'écran de connexion MOVIXIA Consulting.
"""
import streamlit as st
from style import entete_page

entete_page("🚪", "Déconnexion")

nom = st.session_state.get("utilisateur_nom", "")
st.write(f"Tu es actuellement connecté(e){' en tant que **' + nom + '**' if nom else ''}.")
st.caption("En te déconnectant, le document analysé et l'historique du chatbot seront effacés.")

if st.button("Se déconnecter", type="primary"):
    st.session_state.clear()
    st.rerun()
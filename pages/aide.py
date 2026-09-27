"""
Page Aide : mode d'emploi rapide de l'application.
"""
import streamlit as st
from style import entete_page

entete_page("❓", "Aide")

st.markdown("""
**Comment utiliser l'application ?**

1. **Analyse document** — dépose un fichier (.txt, .pdf, .docx) ou colle un texte, puis lance l'analyse.
2. **Résumé** — consulte le résumé validé par l'agent Critique et l'évolution du score.
3. **Traduction** — consulte la traduction automatique du résumé en allemand.
4. **Chatbot** — pose des questions précises sur le contenu du document.
5. **Collaborateurs** — envoie le résumé ou la traduction par e-mail à un destinataire.

**Un souci ?**
- Si une page affiche un avertissement, c'est probablement qu'aucun document n'a encore
  été analysé — retourne sur **Analyse document**.
- Si une erreur de clé API apparaît, vérifie ton fichier `.env`.
""")
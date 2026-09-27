"""
Page Accueil / Analyse document : upload du document, lancement de
l'analyse complète (résumé + critique + traduction + préparation RAG).
"""
import streamlit as st
from extraction import extraire_texte
from agents import boucle_generation_evaluation, LANGUES_DISPONIBLES, TONS_DISPONIBLES
from rag import construire_index
from style import entete_page
from historique import enregistrer_document

entete_page(
    "🏠", "Analyse document",
    "Analyse intelligente de documents — résumé, évaluation, traduction et questions-réponses"
)

st.divider()

fichier = st.file_uploader(
    "Dépose un document (.txt, .pdf ou .docx)",
    type=["txt", "pdf", "docx"],
)

texte_colle = st.text_area(
    "…ou colle directement un texte ici (optionnel si tu as uploadé un fichier)",
    height=150,
)

langue_choisie = st.selectbox(
    "Langue de traduction du résumé",
    LANGUES_DISPONIBLES,
    index=0,
)

ton_choisi = st.selectbox(
    "Ton du résumé (adapté au destinataire)",
    list(TONS_DISPONIBLES.keys()),
    index=0,
)

lancer = st.button("Lancer l'analyse complète", type="primary")

if lancer:
    texte_original = None

    if fichier is not None:
        with st.spinner("Extraction du texte du document..."):
            try:
                texte_original = extraire_texte(fichier)
            except Exception as e:
                st.error(f"Erreur lors de l'extraction : {e}")
    elif texte_colle.strip():
        texte_original = texte_colle.strip()

    if not texte_original:
        st.warning("Merci d'uploader un document ou de coller un texte.")
    else:
        st.session_state.pop("messages", None)
        st.session_state["texte_original"] = texte_original

        st.success(f"Texte récupéré ({len(texte_original.split())} mots environ)")
        with st.expander("Voir le texte original"):
            st.write(texte_original)

        st.divider()
        st.subheader("Boucle Rédacteur ↔ Critique")
        conteneur_iterations = st.container()

        def afficher_iteration(iteration):
            with conteneur_iterations:
                with st.expander(
                    f"Itération {iteration['numero']} — Score : {iteration['score']}/10",
                    expanded=True,
                ):
                    st.markdown("**Résumé :**")
                    st.write(iteration["resume"])
                    st.markdown("**Feedback du Critique :**")
                    st.write(iteration["feedback"])

        with st.spinner("Les agents travaillent (résumé, évaluation, traduction)..."):
            resultat = boucle_generation_evaluation(
                texte_original, callback_iteration=afficher_iteration,
                langue_cible=langue_choisie, ton=ton_choisi,
            )
        st.session_state["resultat"] = resultat

        with st.spinner("Préparation du module de questions-réponses..."):
            chunks, embeddings = construire_index(texte_original)
            st.session_state["rag_chunks"] = chunks
            st.session_state["rag_embeddings"] = embeddings

        # Journalisation dans l'historique (visible sur la page Historique
        # et utilisée par le tableau de bord Statistiques)
        enregistrer_document(
            utilisateur=st.session_state.get("utilisateur_nom"),
            nom_source=fichier.name if fichier is not None else "Texte collé",
            nb_mots=len(texte_original.split()),
            score_final=resultat["score_final"],
            langue_traduction=resultat["langue_traduction"],
        )

        st.divider()
        st.success(
            "Analyse terminée. Utilise le menu à gauche pour consulter le "
            "Résumé, la Traduction, poser des questions dans le Chatbot, "
            "ou envoyer le résultat à un collaborateur."
        )
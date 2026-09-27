"""
Page Traduction : affiche la traduction du résumé final, produite par
l'agent Traducteur, dans la langue choisie sur la page Analyse document.
"""
import streamlit as st
from style import entete_page
from export import generer_docx, generer_pdf
from audio import generer_audio

entete_page("🌐", "Traduction")

if "resultat" not in st.session_state:
    st.warning("Va d'abord sur la page Analyse document pour analyser un document.")
    st.stop()

resultat = st.session_state["resultat"]
langue = resultat.get("langue_traduction", "Allemand")
traduction_texte = resultat.get("traduction", resultat.get("traduction_allemand", ""))

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🇫🇷 Résumé original — Français**")
    st.write(resultat["resume_final"])

with col2:
    st.markdown(f"**🌐 Traduction — {langue}**")
    st.info(traduction_texte)

st.divider()
st.subheader("Écouter la traduction")
if st.button("🔊 Générer l'audio de la traduction"):
    with st.spinner("Génération de l'audio..."):
        try:
            audio_traduction = generer_audio(traduction_texte, langue=langue)
            st.audio(audio_traduction, format="audio/mp3")
            st.download_button(
                "⬇️ Télécharger l'audio (.mp3)",
                data=audio_traduction,
                file_name="traduction_audio.mp3",
                mime="audio/mp3",
            )
        except Exception as e:
            st.error(
                "Échec de la synthèse vocale (vérifie ta connexion internet, "
                f"gTTS en a besoin) : {e}"
            )

st.divider()
st.subheader("Télécharger la traduction")

col_docx, col_pdf = st.columns(2)
with col_docx:
    st.download_button(
        "⬇️ Télécharger en Word (.docx)",
        data=generer_docx(f"Traduction ({langue})", traduction_texte),
        file_name="traduction.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
with col_pdf:
    try:
        pdf_bytes = generer_pdf(f"Traduction ({langue})", traduction_texte)
        st.download_button(
            "⬇️ Télécharger en PDF",
            data=pdf_bytes,
            file_name="traduction.pdf",
            mime="application/pdf",
        )
    except ModuleNotFoundError:
        st.caption(
            "Export PDF indisponible : installe la bibliothèque avec "
            "`pip install fpdf2` puis redémarre l'application."
        )

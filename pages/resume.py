"""
Page Résumé : affiche l'évolution du score à travers les itérations
et le résumé final validé par l'agent Critique.
"""
import streamlit as st
import plotly.graph_objects as go
from agents import SEUIL_QUALITE
from style import entete_page, COULEUR_PRIMAIRE, COULEUR_SUCCES
from export import generer_docx, generer_pdf
from audio import generer_audio

entete_page("📄", "Résumé du document")

if "resultat" not in st.session_state:
    st.warning("Va d'abord sur la page Analyse document pour analyser un document.")
    st.stop()

resultat = st.session_state["resultat"]

st.subheader("Évolution du score à travers les itérations")

scores = [it["score"] for it in resultat["historique"]]
numeros = [it["numero"] for it in resultat["historique"]]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=numeros, y=scores,
    mode="lines+markers",
    name="Score du résumé",
    line=dict(width=3, color=COULEUR_PRIMAIRE),
    marker=dict(size=10, color=COULEUR_PRIMAIRE),
))
fig.add_hline(
    y=SEUIL_QUALITE,
    line_dash="dash",
    line_color=COULEUR_SUCCES,
    annotation_text=f"Seuil de qualité ({SEUIL_QUALITE}/10)",
)
fig.update_layout(
    xaxis_title="Itération",
    yaxis_title="Score /10",
    yaxis_range=[0, 10],
    xaxis=dict(tickmode="linear", dtick=1),
    height=350,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

with st.expander("Voir le détail de chaque itération"):
    for it in resultat["historique"]:
        st.markdown(f"**Itération {it['numero']} — Score {it['score']}/10**")
        st.write(it["resume"])
        st.caption(f"Feedback du Critique : {it['feedback']}")
        st.markdown("---")

st.divider()
st.subheader("Résumé final retenu")

col1, col2 = st.columns([3, 1])
with col1:
    resume_modifie = st.text_area(
        "Tu peux corriger le résumé ci-dessous avant de l'exporter ou de l'envoyer :",
        value=resultat["resume_final"],
        height=160,
        key="resume_edite",
    )
    if st.button("💾 Enregistrer les modifications"):
        st.session_state["resultat"]["resume_final"] = resume_modifie
        st.success("Résumé mis à jour.")
        st.rerun()
with col2:
    st.metric("Score final", f"{resultat['score_final']}/10")
    if resultat["score_final"] >= SEUIL_QUALITE:
        st.success("Qualité validée")
    else:
        st.warning("Max itérations atteint")

st.divider()
st.subheader("Écouter le résumé")
if st.button("🔊 Générer l'audio du résumé"):
    with st.spinner("Génération de l'audio..."):
        try:
            audio_resume = generer_audio(resultat["resume_final"], langue="Français")
            st.audio(audio_resume, format="audio/mp3")
            st.download_button(
                "⬇️ Télécharger l'audio (.mp3)",
                data=audio_resume,
                file_name="resume_audio.mp3",
                mime="audio/mp3",
            )
        except Exception as e:
            st.error(
                "Échec de la synthèse vocale (vérifie ta connexion internet, "
                f"gTTS en a besoin) : {e}"
            )

st.divider()
st.subheader("Télécharger le résumé")

col_docx, col_pdf = st.columns(2)
with col_docx:
    st.download_button(
        "⬇️ Télécharger en Word (.docx)",
        data=generer_docx("Résumé du document", resultat["resume_final"]),
        file_name="resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
with col_pdf:
    try:
        pdf_bytes = generer_pdf("Résumé du document", resultat["resume_final"])
        st.download_button(
            "⬇️ Télécharger en PDF",
            data=pdf_bytes,
            file_name="resume.pdf",
            mime="application/pdf",
        )
    except ModuleNotFoundError:
        st.caption(
            "Export PDF indisponible : installe la bibliothèque avec "
            "`pip install fpdf2` puis redémarre l'application."
        )
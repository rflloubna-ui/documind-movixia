"""
Page Chatbot : permet de poser des questions sur le document original,
à l\'écrit ou à l\'oral (audio transcrit automatiquement), et de recevoir
la réponse dans la langue choisie — avec option d\'écoute audio de la
réponse. Utilise le pipeline RAG (recherche des passages pertinents +
réponse du LLM basée sur ces passages).
"""
import hashlib
import streamlit as st
from agents import LANGUES_DISPONIBLES
from rag import repondre_question
from audio import transcrire_audio, generer_audio
from style import entete_page

entete_page(
    "💬", "Assistant du document",
    "Les réponses sont basées uniquement sur le contenu réel du document."
)

if "rag_chunks" not in st.session_state or "rag_embeddings" not in st.session_state:
    st.warning("Va d\'abord sur la page Analyse document pour analyser un document.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

langue_reponse = st.selectbox(
    "Langue des réponses",
    ["Français"] + LANGUES_DISPONIBLES,
    index=0,
)

with st.expander("🎤 Poser la question à l\'oral (audio)"):
    audio_a_traiter = None
    mime_audio = "audio/wav"

    if hasattr(st, "audio_input"):
        audio_enregistre = st.audio_input("Enregistre ta question au micro")
        if audio_enregistre is not None:
            audio_a_traiter = audio_enregistre.getvalue()
            mime_audio = audio_enregistre.type or "audio/wav"
    else:
        st.caption(
            "L\'enregistrement au micro nécessite une version plus récente de "
            "Streamlit (`pip install --upgrade streamlit`). En attendant, "
            "dépose un fichier audio ci-dessous."
        )

    fichier_audio = st.file_uploader(
        "…ou dépose un fichier audio (.mp3, .wav, .m4a, .ogg)",
        type=["mp3", "wav", "m4a", "ogg"],
    )
    if audio_a_traiter is None and fichier_audio is not None:
        audio_a_traiter = fichier_audio.getvalue()
        mime_audio = fichier_audio.type or "audio/mpeg"

question = st.chat_input("...ou écris ta question sur le document...")

if audio_a_traiter is not None:
    hachage_audio = hashlib.sha256(audio_a_traiter).hexdigest()
    if st.session_state.get("dernier_audio_traite") != hachage_audio:
        st.session_state["dernier_audio_traite"] = hachage_audio
        with st.spinner("Transcription de l\'audio..."):
            try:
                question = transcrire_audio(audio_a_traiter, mime_audio)
                st.caption(f"🎤 Transcription : *{question}*")
            except Exception as e:
                st.error(f"Échec de la transcription audio : {e}")
                question = None

# --- Traitement de la nouvelle question (avant affichage, pour tout
# rendre ensuite dans une seule boucle cohérente, y compris le bouton
# d\'écoute audio de la réponse) ---
if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.spinner("Recherche dans le document..."):
        reponse = repondre_question(
            question,
            st.session_state["rag_chunks"],
            st.session_state["rag_embeddings"],
            langue=langue_reponse,
        )
    st.session_state["messages"].append({
        "role": "assistant",
        "content": reponse,
        "langue": langue_reponse,
        "audio": None,
    })

# --- Affichage de tout l\'historique (y compris la question qui vient
# d\'être traitée), avec bouton d\'écoute persistant pour chaque réponse ---
for idx, message in enumerate(st.session_state["messages"]):
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant":
            if message.get("audio"):
                st.audio(message["audio"], format="audio/mp3")
            elif st.button("🔊 Écouter la réponse", key=f"ecouter_{idx}"):
                with st.spinner("Génération de l\'audio..."):
                    try:
                        message["audio"] = generer_audio(
                            message["content"],
                            langue=message.get("langue", "Français"),
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Échec de la synthèse vocale : {e}")

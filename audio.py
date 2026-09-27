"""
Module Audio : transcrit un enregistrement audio (micro ou fichier) en
texte, en s'appuyant sur la compréhension audio native de l'API Google
Gemini — pas besoin d'installer un moteur de reconnaissance vocale séparé
(type Whisper) ni de clé API supplémentaire.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from agents import MODELE

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

_modele_audio = genai.GenerativeModel(MODELE)


def transcrire_audio(donnees_audio, mime_type="audio/wav"):
    """
    Transcrit fidèlement un enregistrement audio en texte français.
    `donnees_audio` : contenu binaire (bytes) du fichier audio.
    `mime_type` : type MIME de l'audio (ex: "audio/wav", "audio/mpeg", "audio/ogg").
    """
    reponse = _modele_audio.generate_content([
        {"mime_type": mime_type, "data": donnees_audio},
        "Transcris fidèlement, mot pour mot, tout ce qui est dit dans cet "
        "enregistrement audio, dans la langue originale parlée (ne traduis "
        "pas). Réponds UNIQUEMENT avec la transcription telle quelle, sans "
        "introduction, sans commentaire, sans guillemets.",
    ])
    return reponse.text.strip()


# Correspondance langue affichée (côté interface) -> code langue gTTS
_CODES_LANGUE = {
    "Français": "fr",
    "Allemand": "de",
    "Anglais": "en",
    "Espagnol": "es",
    "Italien": "it",
    "Portugais": "pt",
    "Arabe": "ar",
}


def generer_audio(texte, langue="Français"):
    """
    Convertit un texte en fichier audio (voix de synthèse) via gTTS
    (Google Text-to-Speech). Retourne les octets d'un MP3 prêt à être
    lu (st.audio) ou téléchargé (st.download_button).
    """
    from gtts import gTTS
    import io

    code_langue = _CODES_LANGUE.get(langue, "fr")
    tts = gTTS(text=texte, lang=code_langue)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()

"""
Module RAG (Retrieval-Augmented Generation) : permet de poser des questions
sur le document original, au-delà du simple résumé.

Fonctionnement :
1. Le document est découpé en petits morceaux (chunks)
2. Chaque chunk est transformé en vecteur numérique (embedding)
3. Quand l'utilisateur pose une question, on cherche les chunks les plus
   proches sémantiquement de la question (similarité cosinus)
4. On envoie ces chunks pertinents + la question au LLM pour qu'il réponde
   en se basant uniquement sur le contenu réel du document
"""
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from agents import appeler_llm

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODELE_EMBEDDING = "models/gemini-embedding-001"


def diviser_en_chunks(texte, taille_mots=200, chevauchement=50):
    """
    Découpe le texte en morceaux d'environ `taille_mots` mots, avec un
    léger chevauchement pour ne pas couper une idée en plein milieu.
    """
    mots = texte.split()
    chunks = []
    debut = 0
    while debut < len(mots):
        fin = debut + taille_mots
        chunk = " ".join(mots[debut:fin])
        if chunk.strip():
            chunks.append(chunk)
        debut += taille_mots - chevauchement
    return chunks


def embedding_texte(texte, type_tache):
    """Transforme un texte en vecteur numérique via l'API Google."""
    resultat = genai.embed_content(
        model=MODELE_EMBEDDING,
        content=texte,
        task_type=type_tache,  # "retrieval_document" ou "retrieval_query"
    )
    return np.array(resultat["embedding"])


def construire_index(texte_original):
    """
    Découpe le document et calcule l'embedding de chaque chunk.
    Retourne (chunks, matrice_embeddings) à conserver pour les questions futures.
    """
    chunks = diviser_en_chunks(texte_original)
    embeddings = np.array([
        embedding_texte(chunk, "retrieval_document") for chunk in chunks
    ])
    return chunks, embeddings


def chunks_pertinents(question, chunks, embeddings, top_k=3):
    """Retourne les `top_k` chunks les plus proches sémantiquement de la question."""
    vecteur_question = embedding_texte(question, "retrieval_query")

    normes = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(vecteur_question)
    similarites = (embeddings @ vecteur_question) / normes

    indices_tries = np.argsort(similarites)[::-1][:top_k]
    return [chunks[i] for i in indices_tries]


def repondre_question(question, chunks, embeddings, langue="Français"):
    """
    Pipeline RAG complet : trouve les passages pertinents du document,
    puis demande au LLM de répondre (dans la langue demandée) en se basant
    uniquement sur eux.
    """
    passages = chunks_pertinents(question, chunks, embeddings)
    contexte = "\n\n---\n\n".join(passages)

    prompt = f"""Tu es un assistant qui répond à des questions en te basant
UNIQUEMENT sur le contexte extrait du document ci-dessous.

Si la réponse ne se trouve pas dans ce contexte, dis clairement (dans la
langue demandée ci-dessous) que l'information n'est pas présente dans le
document. N'invente jamais de réponse.

CONTEXTE (extraits du document) :
{contexte}

QUESTION :
{question}

IMPORTANT : réponds UNIQUEMENT dans la langue suivante : {langue}. Même si le
contexte ou la question sont dans une autre langue, ta réponse doit être
entièrement rédigée en {langue}.

Réponds de manière claire et concise, en te basant uniquement sur le
contexte ci-dessus."""

    return appeler_llm(prompt, max_tokens=1024)
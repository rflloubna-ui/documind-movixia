"""
Système multi-agents : Agent Rédacteur + Agent Critique
Les deux agents collaborent via une boucle de feedback itérative
pour produire un résumé optimisé d'un document.

Utilise l'API Google Gemini (tier gratuit).
"""
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # lit le fichier .env s'il existe et charge les variables

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODELE = "gemini-3.5-flash-lite"
SEUIL_QUALITE = 7  # score minimum sur 10 pour arrêter la boucle
MAX_ITERATIONS = 3

modele_gemini = genai.GenerativeModel(MODELE)


def appeler_llm(prompt, max_tokens=4096):
    """Fonction unique d'appel au LLM, réutilisée par les deux agents."""
    config_kwargs = {
        "max_output_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        # Désactive le mode "réflexion interne" (thinking) qui consomme
        # une partie du budget de tokens avant même de répondre.
        # Si le SDK installé ne supporte pas ce paramètre, on l'ignore simplement.
        config_kwargs["thinking_config"] = genai.types.ThinkingConfig(thinking_budget=0)
        reponse = modele_gemini.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(**config_kwargs),
        )
    except (TypeError, AttributeError):
        # Le paramètre thinking_config n'est pas supporté par cette version du SDK
        config_kwargs.pop("thinking_config", None)
        reponse = modele_gemini.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(**config_kwargs),
        )

    return reponse.text.strip()


# Tons disponibles pour la rédaction du résumé, selon le destinataire visé
TONS_DISPONIBLES = {
    "Synthétique (pour un manager)": (
        "Adopte un ton synthétique et orienté décision, comme pour un manager "
        "pressé : va droit à l'essentiel, mets en avant les points clés et les "
        "actions à retenir, évite les détails secondaires."
    ),
    "Détaillé technique": (
        "Adopte un ton précis et technique, en conservant les détails, chiffres "
        "et termes spécifiques importants, comme pour un collègue expert du sujet."
    ),
    "Formel": (
        "Adopte un ton formel et professionnel, avec des phrases complètes et un "
        "registre soutenu, adapté à une communication officielle."
    ),
}


def agent_redacteur(texte_original, feedback_precedent=None, resume_precedent=None,
                     ton="Synthétique (pour un manager)"):
    """
    Génère un résumé du texte, dans le ton demandé. Si un feedback précédent
    existe, l'utilise pour corriger le résumé précédent.
    """
    instruction_ton = TONS_DISPONIBLES.get(ton, TONS_DISPONIBLES["Synthétique (pour un manager)"])

    if feedback_precedent is None:
        prompt = f"""Résume le texte suivant en 3 à 5 phrases claires et concises,
en gardant uniquement les idées essentielles.

STYLE ATTENDU : {instruction_ton}

IMPORTANT : donne UNIQUEMENT le résumé final, sans aucune introduction,
sans réflexion préalable, sans commentaire. Commence directement par la première
phrase du résumé.

TEXTE :
{texte_original}"""
    else:
        prompt = f"""Voici un texte original, un résumé précédent, et un feedback
d'amélioration. Corrige le résumé en tenant compte du feedback.

STYLE ATTENDU : {instruction_ton}

IMPORTANT : donne UNIQUEMENT le résumé corrigé, sans aucune introduction,
sans réflexion préalable, sans commentaire. Commence directement par la première
phrase du résumé corrigé.

TEXTE ORIGINAL :
{texte_original}

RÉSUMÉ PRÉCÉDENT :
{resume_precedent}

FEEDBACK À APPLIQUER :
{feedback_precedent}"""

    return appeler_llm(prompt, max_tokens=2048)


def agent_critique(texte_original, resume):
    """
    Évalue la fidélité, la complétude et la concision du résumé.
    Retourne un score /10 et un feedback textuel.
    """
    prompt = f"""Tu es un évaluateur exigeant de résumés. Évalue le résumé suivant
par rapport au texte original, selon 3 critères : fidélité (pas d'invention),
complétude (idées essentielles présentes), concision (pas de détails superflus).

IMPORTANT : réponds UNIQUEMENT dans le format exact ci-dessous, sans aucune
réflexion préalable ni explication avant. Commence directement par "SCORE:".

SCORE: [note entière sur 10]
FEEDBACK: [1 à 2 phrases expliquant ce qui doit être amélioré, ou "Résumé satisfaisant" si tout va bien]

TEXTE ORIGINAL :
{texte_original}

RÉSUMÉ À ÉVALUER :
{resume}"""

    reponse = appeler_llm(prompt, max_tokens=800)
    score, feedback = _parser_evaluation(reponse)
    return score, feedback


def _parser_evaluation(reponse):
    """Extrait le score numérique et le feedback depuis la réponse de l'agent critique."""
    # On nettoie les éventuels marqueurs markdown (**gras**) qui perturbent le parsing
    texte_propre = reponse.replace("*", "")

    score_match = re.search(r"SCORE\s*:\s*(\d+)", texte_propre, re.IGNORECASE)
    feedback_match = re.search(r"FEEDBACK\s*:\s*(.+)", texte_propre, re.IGNORECASE | re.DOTALL)

    if score_match:
        score = int(score_match.group(1))
    else:
        # Si le format attendu n'a pas été respecté, on cherche juste un chiffre isolé
        chiffre_isole = re.search(r"\b(\d{1,2})\s*/\s*10\b", texte_propre)
        score = int(chiffre_isole.group(1)) if chiffre_isole else 5

    if feedback_match:
        feedback = feedback_match.group(1).strip()
    else:
        feedback = texte_propre.strip() or "Pas de feedback disponible."

    score = max(0, min(10, score))  # on borne le score entre 0 et 10

    return score, feedback


# Langues proposées pour la traduction du résumé (menu déroulant côté interface)
LANGUES_DISPONIBLES = ["Allemand", "Anglais", "Espagnol", "Italien", "Portugais", "Arabe"]


def agent_traducteur(resume_final, langue_cible="Allemand"):
    """
    Traduit le résumé final vers la langue cible demandée. Troisième agent
    de la chaîne, intervient une fois que le résumé a été validé par le Critique.
    """
    prompt = f"""Tu es un traducteur professionnel français → {langue_cible}.

Traduis INTÉGRALEMENT le texte suivant en {langue_cible}, du début jusqu'à la
toute dernière phrase, sans en omettre une partie. Ne laisse aucun mot
ou passage en français dans ta traduction. Ne t'arrête pas avant d'avoir
traduit l'intégralité du texte.

IMPORTANT : réponds UNIQUEMENT avec la traduction complète, sans introduction,
sans commentaire, sans note, sans astérisque.

TEXTE À TRADUIRE :
{resume_final}"""

    traduction = appeler_llm(prompt, max_tokens=2048)
    # Sécurité : on retire d'éventuels astérisques ou artefacts de formatage
    return traduction.replace("*", "").strip()


def boucle_generation_evaluation(texte_original, callback_iteration=None, langue_cible="Allemand",
                                  ton="Synthétique (pour un manager)"):
    """
    Boucle principale multi-agents :
    1. Le Rédacteur génère un résumé
    2. Le Critique l'évalue
    3. Si le score est insuffisant, le Rédacteur corrige avec le feedback
    4. Répète jusqu'à MAX_ITERATIONS ou jusqu'à atteindre SEUIL_QUALITE

    callback_iteration : fonction optionnelle appelée à chaque itération,
    utile pour afficher la progression en direct dans Streamlit.
    """
    historique = []
    resume = None
    feedback = None
    meilleur_resume = None
    meilleur_score = -1

    for i in range(1, MAX_ITERATIONS + 1):
        resume = agent_redacteur(texte_original, feedback, resume, ton)
        score, feedback = agent_critique(texte_original, resume)

        iteration = {
            "numero": i,
            "resume": resume,
            "score": score,
            "feedback": feedback,
        }
        historique.append(iteration)

        if callback_iteration:
            callback_iteration(iteration)

        if score > meilleur_score:
            meilleur_score = score
            meilleur_resume = resume

        if score >= SEUIL_QUALITE:
            break

    resultat = {
        "resume_final": meilleur_resume,
        "score_final": meilleur_score,
        "historique": historique,
        "ton": ton,
    }

    # Troisième agent : traduction du résumé final vers la langue choisie
    resultat["traduction"] = agent_traducteur(meilleur_resume, langue_cible)
    resultat["langue_traduction"] = langue_cible

    return resultat
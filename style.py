"""
Module de style visuel centralisé pour l'application.
Palette : bleu nuit → violet (évoque la tech/IA), fond clair épuré,
typographie sobre. Importé et appliqué sur chaque page.
"""
import streamlit as st

# --- Palette de couleurs ---
COULEUR_PRIMAIRE = "#4F46E5"      # Indigo — accent principal
COULEUR_SECONDAIRE = "#7C3AED"    # Violet — dégradé
COULEUR_FONCEE = "#1E1B4B"        # Bleu nuit — titres, textes forts
COULEUR_CLAIRE = "#F8F7FF"        # Fond très clair, légèrement teinté
COULEUR_SUCCES = "#059669"        # Vert — validation, scores élevés
COULEUR_ALERTE = "#D97706"        # Ambre — avertissements
COULEUR_TEXTE = "#334155"         # Gris ardoise — texte courant


def appliquer_style():
    """À appeler en tout début de chaque page pour homogénéiser le design."""
    st.markdown(f"""
        <style>
        /* Typographie générale */
        html, body, [class*="css"] {{
            font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
        }}

        /* Titres avec dégradé */
        h1 {{
            background: linear-gradient(90deg, {COULEUR_FONCEE} 0%, {COULEUR_PRIMAIRE} 60%, {COULEUR_SECONDAIRE} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            padding-bottom: 0.2em;
        }}

        h2, h3 {{
            color: {COULEUR_FONCEE};
            font-weight: 600;
        }}

        /* Bouton principal avec dégradé */
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, {COULEUR_PRIMAIRE} 0%, {COULEUR_SECONDAIRE} 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            padding: 0.6em 1.4em;
            transition: opacity 0.2s ease;
        }}
        div.stButton > button[kind="primary"]:hover {{
            opacity: 0.88;
        }}

        /* Fond général de l'application : dégradé doux */
        .stApp {{
            background: linear-gradient(160deg, #FFFFFF 0%, #F8F7FF 45%, #EEF2FF 100%);
        }}

        /* Barre latérale : dégradé professionnel plus marqué */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COULEUR_FONCEE} 0%, {COULEUR_PRIMAIRE} 55%, {COULEUR_SECONDAIRE} 100%);
            border-right: none;
        }}
        section[data-testid="stSidebar"] * {{
            color: #F5F3FF !important;
        }}

        /* Liens de navigation du menu (pages) */
        section[data-testid="stSidebarNav"] a {{
            border-radius: 8px;
            padding: 0.5em 0.8em;
            margin: 0.15em 0.5em;
            transition: background-color 0.2s ease;
        }}
        section[data-testid="stSidebarNav"] a:hover {{
            background-color: rgba(255, 255, 255, 0.15);
        }}
        section[data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: rgba(255, 255, 255, 0.22);
            font-weight: 600;
        }}

        /* Séparateur visuel entre les sections du menu (avant "Compte") */
        section[data-testid="stSidebarNav"] ul li:has(+ [data-testid="stSidebarNavSeparator"]) {{
            margin-bottom: 0.5em;
        }}
        section[data-testid="stSidebarNav"] hr,
        section[data-testid="stSidebarNav"] [data-testid="stSidebarNavSeparator"] {{
            border-color: rgba(255, 255, 255, 0.25);
            margin: 0.8em 1em;
        }}

        /* Titre de section dans le menu (ex: "Compte") */
        section[data-testid="stSidebarNav"] p {{
            color: rgba(255, 255, 255, 0.6) !important;
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* Cartes d'information (st.info, st.success) */
        div[data-testid="stAlert"] {{
            border-radius: 10px;
            border-left: 4px solid {COULEUR_PRIMAIRE};
        }}

        /* Séparateurs plus discrets */
        hr {{
            border-color: #E5E7EB;
        }}

        /* Métriques (score final) */
        div[data-testid="stMetricValue"] {{
            color: {COULEUR_PRIMAIRE};
            font-weight: 700;
        }}
        </style>
    """, unsafe_allow_html=True)


def entete_page(icone, titre, sous_titre=None):
    """
    Affiche un en-tête de page harmonisé : icône discrète + titre en dégradé
    + sous-titre optionnel en gris.
    """
    st.markdown(f"""
        <div style="margin-bottom: 0.3em;">
            <span style="font-size: 1.1em; opacity: 0.75;">{icone}</span>
            <span style="font-size: 1.9em; font-weight: 700;
                background: linear-gradient(90deg, {COULEUR_FONCEE}, {COULEUR_PRIMAIRE}, {COULEUR_SECONDAIRE});
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text; margin-left: 0.15em;">
                {titre}
            </span>
        </div>
    """, unsafe_allow_html=True)
    if sous_titre:
        st.markdown(f"<p style='color:{COULEUR_TEXTE}; margin-top:-0.3em;'>{sous_titre}</p>",
                    unsafe_allow_html=True)
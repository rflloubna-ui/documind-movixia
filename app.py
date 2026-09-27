"""
Point d'entrée de l'application.
1. Si l'utilisateur n'est pas authentifié : affiche l'écran de connexion
   / création de compte MOVIXIA Consulting.
2. Une fois authentifié : affiche le menu de navigation et lance la page
   sélectionnée.
"""
import streamlit as st
from style import appliquer_style
from auth import creer_compte, authentifier

st.set_page_config(
    page_title="Outil interne de traitement des documents",
    page_icon="🤖",
    layout="centered",
)
appliquer_style()

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# --- Écran de connexion / création de compte ---
if not st.session_state["authentifie"]:
    # Masque complètement le menu latéral : impossible d'accéder aux pages
    # sans être authentifié, même en connaissant leur URL directe.
    st.markdown(
        "<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'] "
        "{display: none;}</style>",
        unsafe_allow_html=True,
    )

    st.markdown("""
        <div style="text-align:center; margin-top: 1.5em;">
            <span style="font-size: 2.6em; font-weight: 800;
                background: linear-gradient(90deg, #1E1B4B, #4F46E5, #7C3AED);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;">
                MOVIXIA Consulting
            </span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <p style="text-align:center; color:#334155; max-width:540px;
                  margin: 0.6em auto 2em auto; line-height:1.5;">
            Chez MOVIXIA Consulting, nous croyons que la technologie doit
            simplifier le travail, pas le compliquer. Cet outil interne met
            l'intelligence artificielle au service de votre équipe pour
            analyser, résumer et traduire vos documents en quelques secondes.
        </p>
    """, unsafe_allow_html=True)

    onglet_connexion, onglet_creation = st.tabs(["Se connecter", "Créer un compte"])

    with onglet_connexion:
        email = st.text_input("Adresse e-mail", key="login_email")
        mdp = st.text_input("Mot de passe", type="password", key="login_mdp")
        if st.button("Se connecter", type="primary", key="btn_login"):
            ok, resultat = authentifier(email, mdp)
            if ok:
                st.session_state["authentifie"] = True
                st.session_state["utilisateur_nom"] = resultat["nom"]
                st.session_state["utilisateur_poste"] = resultat["poste"]
                st.session_state["utilisateur_email"] = resultat["email"]
                st.rerun()
            else:
                st.error(resultat)

    with onglet_creation:
        nom = st.text_input("Nom et prénom", key="signup_nom")
        poste = st.text_input("Poste occupé (ex : Chef de service, Assistante RH...)", key="signup_poste")
        email_c = st.text_input("Adresse e-mail", key="signup_email")
        mdp_c = st.text_input("Mot de passe", type="password", key="signup_mdp")
        mdp_c2 = st.text_input("Confirmer le mot de passe", type="password", key="signup_mdp2")
        if st.button("Créer un compte", type="primary", key="btn_signup"):
            if mdp_c != mdp_c2:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                ok, message = creer_compte(nom, poste, email_c, mdp_c)
                if ok:
                    st.success(message)
                else:
                    st.error(message)

    st.stop()

# --- Utilisateur authentifié : menu et application ---
with st.sidebar:
    st.markdown("### 🤖 Outil interne de traitement des documents")
    if "utilisateur_nom" in st.session_state:
        poste_aff = st.session_state.get("utilisateur_poste", "")
        suffixe = f" — {poste_aff}" if poste_aff else ""
        st.caption(f"Connecté en tant que {st.session_state['utilisateur_nom']}{suffixe}")

pages = {
    "": [
        st.Page("pages/accueil.py", title="Analyse document", icon="🏠", default=True),
        st.Page("pages/chatbot.py", title="Chatbot", icon="💬"),
        st.Page("pages/resume.py", title="Résumé", icon="📄"),
        st.Page("pages/traduction.py", title="Traduction", icon="🌐"),
        st.Page("pages/collaborateurs.py", title="Collaborateurs", icon="👥"),
        st.Page("pages/historique.py", title="Historique", icon="🕓"),
        st.Page("pages/statistiques.py", title="Statistiques", icon="📊"),
    ],
    "Compte": [
        st.Page("pages/parametres.py", title="Paramètres", icon="⚙️"),
        st.Page("pages/aide.py", title="Aide", icon="❓"),
        st.Page("pages/deconnexion.py", title="Déconnexion", icon="🚪"),
    ],
}

pg = st.navigation(pages)
pg.run()
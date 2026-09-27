"""
Page Collaborateurs : envoie réellement le résumé ou la traduction par
e-mail via le serveur SMTP de Gmail (nécessite un compte Gmail + un
mot de passe d'application configurés dans le fichier .env).

Si l'envoi automatique n'est pas configuré, une solution de secours
(lien mailto ouvrant la messagerie locale) est proposée à la place.
"""
import streamlit as st
import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from style import entete_page
from historique import enregistrer_envoi

load_dotenv()

entete_page("👥", "Envoyer aux collaborateurs")

if "resultat" not in st.session_state:
    st.warning("Va d'abord sur la page Analyse document pour générer un résumé.")
    st.stop()

resultat = st.session_state["resultat"]

# Carnet d'adresses proposé — modifiable directement ici
DESTINATAIRES = {
    "Chef de service": "rflloubna@gmail.com",
    "Service RH": "lubna.rfl1@gmail.com",
    "Stéphane Chant (collaborateur)": "staphane-chant@gmail.fr",
    "Estelle Robert (collaboratrice)": "Estelle-robert@outlook.fr",
}

langue_traduction = resultat.get("langue_traduction", "Allemand")

contenu_choisi = st.radio(
    "Quel contenu veux-tu envoyer ?",
    ["Résumé (Français)", f"Traduction ({langue_traduction})"],
    horizontal=True,
)

choix_destinataires = st.multiselect(
    "Destinataire(s) proposé(s)",
    options=list(DESTINATAIRES.keys()),
)

email_perso = st.text_input("Ou saisis une autre adresse e-mail (optionnel)")

st.divider()

adresses = [DESTINATAIRES[c] for c in choix_destinataires]
if email_perso.strip():
    adresses.append(email_perso.strip())

if contenu_choisi == "Résumé (Français)":
    sujet = "Résumé automatique du document"
    corps = resultat["resume_final"]
else:
    sujet = f"Traduction automatique du document ({langue_traduction})"
    corps = resultat.get("traduction", resultat.get("traduction_allemand", ""))

# Identité de l'expéditeur (renseignée à la création du compte) : ajoutée
# automatiquement en signature de chaque e-mail, pour que les destinataires
# sachent toujours qui a envoyé le document et à quel poste il/elle est.
utilisateur_nom = st.session_state.get("utilisateur_nom", "")
utilisateur_poste = st.session_state.get("utilisateur_poste", "")
utilisateur_email = st.session_state.get("utilisateur_email", "")

signature_lignes = ["", "", "---"]
if utilisateur_nom:
    signature_lignes.append(utilisateur_nom + (f" — {utilisateur_poste}" if utilisateur_poste else ""))
if utilisateur_email:
    signature_lignes.append(utilisateur_email)
signature_lignes.append("Envoyé via l'outil interne MOVIXIA")
signature = "\n".join(signature_lignes)

corps_avec_signature = corps + signature

st.markdown("**Aperçu du contenu qui sera envoyé :**")
st.info(corps_avec_signature)

gmail_adresse = os.environ.get("GMAIL_ADDRESS")
gmail_mdp_app = os.environ.get("GMAIL_APP_PASSWORD")


def envoyer_email_reel(destinataires, sujet, corps):
    message = MIMEMultipart()
    if utilisateur_nom:
        nom_affiche = utilisateur_nom + (f" ({utilisateur_poste})" if utilisateur_poste else "")
        message["From"] = f"{nom_affiche} <{gmail_adresse}>"
    else:
        message["From"] = gmail_adresse
    message["To"] = ", ".join(destinataires)
    message["Subject"] = sujet
    if utilisateur_email:
        message["Reply-To"] = utilisateur_email
    message.attach(MIMEText(corps, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
        serveur.login(gmail_adresse, gmail_mdp_app)
        serveur.sendmail(gmail_adresse, destinataires, message.as_string())


if not adresses:
    st.caption("Sélectionne au moins un destinataire (ou saisis une adresse) pour activer l'envoi.")

elif gmail_adresse and gmail_mdp_app:
    # Envoi automatique réel via Gmail
    if st.button("📤 Envoyer l'e-mail maintenant", type="primary"):
        try:
            with st.spinner("Envoi en cours..."):
                envoyer_email_reel(adresses, sujet, corps_avec_signature)
            st.success(f"E-mail envoyé avec succès à : {', '.join(adresses)}")
            enregistrer_envoi(
                utilisateur=st.session_state.get("utilisateur_nom"),
                destinataires=adresses,
                type_contenu=contenu_choisi,
            )
        except smtplib.SMTPAuthenticationError:
            st.error(
                "Échec de connexion à Gmail. Vérifie que GMAIL_ADDRESS et "
                "GMAIL_APP_PASSWORD dans ton fichier .env sont corrects, et que "
                "tu utilises bien un mot de passe d'application (pas ton mot de "
                "passe Gmail habituel)."
            )
        except Exception as e:
            st.error(f"Échec de l'envoi : {e}")

else:
    # Solution de secours si l'envoi automatique n'est pas configuré
    sujet_encode = urllib.parse.quote(sujet)
    corps_encode = urllib.parse.quote(corps_avec_signature)
    destinataires_str = ",".join(adresses)
    lien_mailto = f"mailto:{destinataires_str}?subject={sujet_encode}&body={corps_encode}"

    st.warning(
        "L'envoi automatique n'est pas encore configuré (voir la page **Paramètres** "
        "pour l'activer). En attendant, ce bouton ouvre ta messagerie locale par défaut "
        "avec tout pré-rempli — mais si tu n'as pas de logiciel de messagerie installé "
        "sur ce PC, rien ne s'ouvrira."
    )
    st.link_button("Ouvrir dans ma messagerie", lien_mailto)
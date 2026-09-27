"""
Page Statistiques : tableau de bord synthétique de l'usage de l'application
(documents traités, e-mails envoyés, répartition par utilisateur, etc.)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from style import entete_page, COULEUR_PRIMAIRE, COULEUR_SECONDAIRE
from historique import charger_historique

entete_page("📊", "Statistiques", "Vue d'ensemble de l'activité de l'application")

entrees = charger_historique()

if not entrees:
    st.info("Aucune activité enregistrée pour l'instant — les statistiques apparaîtront ici dès qu'un document aura été traité.")
    st.stop()

documents = [e for e in entrees if e["type"] == "document"]
envois = [e for e in entrees if e["type"] == "envoi"]

col1, col2, col3 = st.columns(3)
col1.metric("Documents traités", len(documents))
col2.metric("E-mails envoyés", len(envois))
score_moyen = round(sum(d["score_final"] for d in documents) / len(documents), 1) if documents else 0
col3.metric("Score moyen des résumés", f"{score_moyen}/10")

st.divider()

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.subheader("Documents traités par utilisateur")
    if documents:
        df_users = pd.DataFrame(documents)["utilisateur"].value_counts().reset_index()
        df_users.columns = ["Utilisateur", "Nombre"]
        fig = px.bar(df_users, x="Utilisateur", y="Nombre", color_discrete_sequence=[COULEUR_PRIMAIRE])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Pas encore de document traité.")

with col_droite:
    st.subheader("Langues de traduction utilisées")
    if documents:
        df_langues = pd.DataFrame(documents)["langue_traduction"].value_counts().reset_index()
        df_langues.columns = ["Langue", "Nombre"]
        fig2 = px.pie(df_langues, names="Langue", values="Nombre",
                      color_discrete_sequence=[COULEUR_PRIMAIRE, COULEUR_SECONDAIRE, "#A5B4FC", "#C4B5FD", "#818CF8", "#6D28D9"])
        fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("Pas encore de document traité.")

st.subheader("Activité dans le temps")
if entrees:
    df_all = pd.DataFrame(entrees)
    df_all["jour"] = pd.to_datetime(df_all["date"]).dt.date
    df_par_jour = df_all.groupby(["jour", "type"]).size().reset_index(name="Nombre")
    fig3 = px.bar(df_par_jour, x="jour", y="Nombre", color="type", barmode="group",
                  color_discrete_map={"document": COULEUR_PRIMAIRE, "envoi": COULEUR_SECONDAIRE})
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Date", yaxis_title="Nombre")
    st.plotly_chart(fig3, use_container_width=True)

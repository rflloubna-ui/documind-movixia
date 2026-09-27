"""
Petit script de diagnostic : liste les modèles Gemini réellement
disponibles pour TON compte/clé API, avec leur quota si disponible.

Lancement : python lister_modeles.py
Nécessite la variable d'environnement GOOGLE_API_KEY.
"""
import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

print("Modèles disponibles pour ton compte (supportant generateContent) :\n")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        # On filtre pour n'afficher que les modèles "flash" ou "lite",
        # les plus légers et donc les plus probables d'avoir un bon quota gratuit
        if "flash" in m.name.lower() or "lite" in m.name.lower():
            print(f"  {m.name}")

print("\nCopie le nom d'un de ces modèles (sans 'models/' devant) dans MODELE = \"...\" dans agents.py")

"""
Extraction de texte depuis différents formats de fichiers (.txt, .pdf, .docx)
"""
from pypdf import PdfReader
from docx import Document
import io


def extraire_texte(fichier_uploade):
    """
    Prend un fichier uploadé (objet Streamlit UploadedFile) et retourne
    le texte brut, quel que soit le format (.txt, .pdf, .docx).
    """
    nom = fichier_uploade.name.lower()

    if nom.endswith(".txt"):
        return _extraire_txt(fichier_uploade)
    elif nom.endswith(".pdf"):
        return _extraire_pdf(fichier_uploade)
    elif nom.endswith(".docx"):
        return _extraire_docx(fichier_uploade)
    else:
        raise ValueError(
            f"Format non supporté : {nom}. Formats acceptés : .txt, .pdf, .docx"
        )


def _extraire_txt(fichier):
    contenu = fichier.read()
    if isinstance(contenu, bytes):
        contenu = contenu.decode("utf-8", errors="ignore")
    return contenu.strip()


def _extraire_pdf(fichier):
    reader = PdfReader(io.BytesIO(fichier.read()))
    texte = ""
    for page in reader.pages:
        texte += page.extract_text() or ""
        texte += "\n"
    return texte.strip()


def _extraire_docx(fichier):
    doc = Document(io.BytesIO(fichier.read()))
    paragraphes = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphes).strip()
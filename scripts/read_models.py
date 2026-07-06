from docx import Document

files = [
    r"data\raw\65060956_extracted\D.C. AOO SF 22-2025\Modèle de la déclaration sur l'honneur.docx",
    r"data\raw\65060956_extracted\D.C. AOO SF 22-2025\Modèle de l'acte d'engagement.docx"
]

with open("temp_models.txt", "w", encoding="utf-8") as out:
    for f in files:
        out.write(f"\n\n{'='*50}\nFICHIER: {f.split(chr(92))[-1]}\n{'='*50}\n")
        try:
            doc = Document(f)
            text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
            out.write(text)
        except Exception as e:
            out.write(f"Erreur de lecture: {e}")

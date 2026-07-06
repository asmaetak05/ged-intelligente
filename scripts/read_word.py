import win32com.client
import os

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
path = os.path.abspath(r"data\raw\65060956_extracted\D.C. AOO SF 22-2025\RC SF 22-2025  Etude d'élar.renf RR 507 PK 0-20+500.doc")

try:
    doc = word.Documents.Open(path)
    text = doc.Content.Text
    
    with open('temp_output.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Ecrit dans temp_output.txt")
    doc.Close()
except Exception as e:
    print("Erreur:", e)
finally:
    word.Quit()

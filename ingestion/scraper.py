import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}

session = requests.Session()
session.headers.update(headers)

print("1. Récupération de la page d'accueil...")
response = session.get(url, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

print("2. Extraction de TOUS les champs du formulaire...")
payload = {}
# Récupérer tous les inputs (hidden, text, checkbox, submit)
for input_tag in soup.find_all('input'):
    name = input_tag.get('name')
    if not name:
        continue
    value = input_tag.get('value', '')
    payload[name] = value

# Récupérer tous les selects
for select_tag in soup.find_all('select'):
    name = select_tag.get('name')
    if not name:
        continue
    # On prend l'option sélectionnée par défaut, ou la première
    selected = select_tag.find('option', selected=True)
    if selected:
        payload[name] = selected.get('value', '')
    else:
        first_option = select_tag.find('option')
        payload[name] = first_option.get('value', '') if first_option else ''

print("3. Modification des critères pour 2025...")
# On écrase nos filtres
# payload['date_parution1'] = '01/01/2025'
# payload['date_parution2'] = '31/12/2025'

# TEST: Simuler le clic sur "AO en cours" via __doPostBack
payload['__EVENTTARGET'] = 'LinkButton_encours'
payload['__EVENTARGUMENT'] = ''

# Supprimer tous les boutons submit car on utilise __EVENTTARGET
submit_keys = [k for k in payload.keys() if 'btn' in k.lower() or 'detail' in k.lower()]
for k in submit_keys:
    del payload[k]

print("4. Envoi de la requête POST (__doPostBack)...")
response2 = session.post(url, data=payload, verify=False)
soup2 = BeautifulSoup(response2.text, 'html.parser')

print("5. Analyse de la réponse...")
# Vérifions si on a toujours une erreur
if "Runtime Error" in response2.text:
    print("ÉCHEC : Le serveur a encore renvoyé une Runtime Error.")
else:
    table = soup2.find('table', id='TabC1_all_GV')
    if table:
        rows = table.find_all('tr')
        print(f"SUCCÈS ! Trouvé {len(rows)-1} éléments dans le tableau.")
        links = table.find_all('a')
        for a in links[:10]:
            print(f" - {a.text.strip()} (Lien: {a.get('href')})")
    else:
        print("Requête acceptée (pas d'erreur), mais le tableau TabC1_all_GV est introuvable.")
        print("Titre de la page retournée :", soup2.title.string if soup2.title else "Aucun")

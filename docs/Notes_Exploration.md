# Notes d'Exploration du Portail (J1)

**Source :** `http://appels-offres.equipement.gov.ma/recherche/criteres.aspx`

## 1. Observations Techniques sur le Portail
- **Technologie :** Le site est développé en ASP.NET (WebForms). Il utilise des champs cachés (`__VIEWSTATE`, `__EVENTVALIDATION`) pour maintenir l'état du formulaire de recherche.
- **Requêtes :** Pour simuler une recherche (ex: filtrer par date ou activité), il faudra faire une requête HTTP `POST` en renvoyant exactement le `__VIEWSTATE` récupéré au préalable lors d'un `GET`.
- **Mécanique de téléchargement :** Les fichiers ne sont pas des liens PDF directs. Les marchés sont encapsulés dans des archives `.zip`.

## 2. Structure des Données Téléchargées (ZIP)
Un téléchargement type contient :
1. Un avis d'appel d'offres (AAO)
2. Le Règlement de Consultation (RC)
3. Le Cahier des Prescriptions Spéciales (CPS)
4. Souvent des bordereaux de prix ou des plans.

## 3. Qualité des Documents (Les PDFs à l'intérieur)
Il existe deux grandes catégories de PDFs rencontrés :
- **Les PDF Natifs** : Générés depuis Word/Excel (texte sélectionnable). Ils sont faciles à extraire et fiables à 100%.
- **Les PDF Scannés** : Documents imprimés, signés, puis numérisés. Ils sont traités comme de simples images. **C'est là que réside le défi principal du projet : appliquer un OCR sur ces pages.**

## 4. Conclusion J1
Le scraping automatique est réalisable mais demandera de gérer l'état ASP.NET avec `BeautifulSoup`. Le traitement documentaire demandera systématiquement une décompression ZIP préalable.

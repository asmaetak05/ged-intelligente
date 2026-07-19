# Réalisation ING-02

**Ticket** : Découplage des sélecteurs (Configuration Externe)
**Statut** : Terminé

**Détails de l'implémentation** :
- Tous les sélecteurs CSS et XPath ont été extraits du code source de `ingestion/playwright_scraper_batch.py`.
- Création du fichier `ingestion/config_selectors.json` pour stocker les éléments de recherche (ex: `date_parution1`, `btn_rechercher`, `.tab_results`).
- Ajout d'une fonction `load_selectors()` qui charge ce JSON au démarrage, permettant des mises à jour sans toucher au code Python en cas de refonte du portail.

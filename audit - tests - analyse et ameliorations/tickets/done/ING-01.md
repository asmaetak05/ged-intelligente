# Réalisation ING-01

**Ticket** : Pool Playwright + parallélisation contrôlée
**Statut** : Terminé

**Détails de l'implémentation** :
- Le téléchargement des avis dans `ingestion/playwright_scraper_batch.py` a été parallélisé.
- Utilisation de `asyncio.gather` avec une limite imposée par `asyncio.Semaphore(3)` pour ne pas surcharger le portail et risquer un bannissement IP.
- La phase A (navigation des pages) est restée séquentielle car elle dépend de l'état ASP.NET GridView (Viewstate). Seule la phase B de téléchargement a été parallélisée.

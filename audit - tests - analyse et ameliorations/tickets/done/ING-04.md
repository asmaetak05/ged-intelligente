# Réalisation ING-04

**Ticket** : Idempotence et Déduplication par Hash SHA-256
**Statut** : Terminé

**Détails de l'implémentation** :
- Ajout d'une colonne `checksum_sha256` dans le modèle `Document` (géré avec Alembic).
- Implémentation du calcul SHA-256 du fichier ZIP directement à l'acquisition dans `backend/main.py`.
- L'endpoint d'upload bloque le traitement asynchrone si le hash existe déjà avec un statut `ocr_processed`, retournant directement les métadonnées existantes.
- Ceci garantit que les processus intensifs CPU (`extract_ocr.py`) ne sont jamais appelés deux fois pour le même fichier exact.

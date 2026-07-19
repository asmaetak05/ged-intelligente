# Réalisation NLP-03

**Ticket** : Extraction des agréments ministériels exigés
**Statut** : Terminé

**Détails de l'implémentation** :
- Création du module `nlp/extract_agrement.py`.
- Ajout d'une recherche regex ciblant spécifiquement la terminologie "agrément(s) exigé(s) de classe" et capturant le domaine de classe (ex. D9, D12) qui sont vitaux pour les bureaux d'études.
- La logique d'extraction est correctement découplée et appelée via le module parent `extract_entities.py`.

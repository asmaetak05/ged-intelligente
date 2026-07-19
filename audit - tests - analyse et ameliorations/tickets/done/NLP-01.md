# Réalisation NLP-01

**Ticket** : Extraction du type d'avis
**Statut** : Terminé

**Détails de l'implémentation** :
- Création du module dédié `nlp/extract_typeavis.py`.
- L'expression régulière a été conçue pour identifier les "appel d'offres" avec les qualificatifs ouverts, restreints, simplifiés ou négociés, ainsi que les "concours" et "bon de commande".
- La logique est appelée depuis `nlp/extract_entities.py` pour enregistrer l'entité de type `type_avis` au sein du dictionnaire JSON final.

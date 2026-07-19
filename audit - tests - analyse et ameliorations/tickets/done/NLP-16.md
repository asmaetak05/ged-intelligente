# Réalisation NLP-16

**Ticket** : Optimisation de l'extraction de l'acheteur (Maître d'ouvrage)
**Statut** : Terminé

**Détails de l'implémentation** :
- Refactoring du bloc d'extraction de l'acheteur dans `nlp/extract_entities.py`.
- Un système de scoring a été mis en place, séparant la détection regex (`mo_candidate` local) et la détection via `spacy`.
- La recherche sémantique avec spaCy est effectuée prioritairement. Si aucune entité de type organisation (ORG) n'est trouvée pour qualifier l'acheteur, le système se rabat sur le fallback regex, évitant ainsi le problème logique précédent où la regex n'était jamais activée.
- Les tests ont été déplacés et renforcés dans `tests/test_nlp_extraction_avancee.py`.

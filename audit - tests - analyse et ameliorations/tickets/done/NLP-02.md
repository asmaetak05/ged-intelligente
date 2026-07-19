# Réalisation NLP-02

**Ticket** : Extraction des qualifications requises (Q1-Q6 BTP)
**Statut** : Terminé

**Détails de l'implémentation** :
- Création du module dédié `nlp/extract_qualif.py`.
- Implémentation d'expressions régulières robustes aux sauts de ligne pour extraire les numéros de qualifications marocaines (Q1 à Q6, ou catégories A-S).
- Intégration à l'orchestrateur NLP pour la capture des qualifications exigées au moment de l'ingestion d'un règlement de consultation.

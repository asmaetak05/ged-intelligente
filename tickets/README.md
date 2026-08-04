# Backlog de réalisation — GED intelligente

Ce dossier transforme l'audit en tickets de développement directement exploitables. Il est organisé par modules et priorités, dans l'ordre où ils doivent être réalisés.

## Point d'entrée obligatoire pour un outil de code

Un outil de code ne doit pas commencer par lire des tickets au hasard. Il doit suivre cet ordre :

1. lire [START_HERE.md](START_HERE.md) ;
2. lire [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) ;
3. lire [MASTER_BACKLOG.md](MASTER_BACKLOG.md) et [TICKET_STATUS.md](TICKET_STATUS.md) ;
4. sélectionner le **premier ticket non terminé dont les dépendances sont terminées** ;
5. ne traiter qu'un ticket à la fois ;
6. fournir le compte rendu imposé par [RESULT_TEMPLATE.md](RESULT_TEMPLATE.md) ;
7. mettre à jour `TICKET_STATUS.md` seulement avec des preuves d'exécution.

## Règles de lecture

| Champ | Signification |
|---|---|
| `P0` | Bloquant : à terminer avant toute soutenance ou pilote |
| `P1` | Indispensable pour un MVP cohérent |
| `P2` | À faire si le temps le permet ; peut être une perspective de PFA |
| `Partiel` | Code présent, mais incomplet, fragile ou non démontré |
| `À faire` | Fonctionnalité non présente dans le dépôt |
| `À vérifier` | Fonctionnalité annoncée, mais non validée par exécution |

Un ticket ne passe à `Terminé` que lorsque ses critères d'acceptation sont prouvés par un test, une commande reproductible ou un scénario de démonstration documenté.

## Ordre de réalisation obligatoire

1. `00_socle_qualite` — sécurité, reproductibilité, migrations et contrats.
2. `01_ingestion_import` — entrée des documents et suivi fiable.
3. `02_extraction_ocr` — texte exploitable et qualité mesurée.
4. `03_nlp_validation` — données métier vérifiables et correction humaine.
5. `04_recherche_consultation` — recherche, fiche et comparaison.
6. `05_dashboard_analytique` — indicateurs réels, pas décoratifs.
7. `06_administration_audit` — rôles, audit et supervision.
8. `07_ml_experimental` — uniquement après constitution du corpus annoté.

## Définition du MVP de soutenance

Le MVP est atteint lorsqu'un dossier de démonstration peut suivre ce chemin sans données simulées :

```text
Import ZIP/PDF → validation → extraction/OCR → champs NLP → correction humaine
→ indexation → recherche → fiche détaillée → dashboard → trace d'audit
```

Le scraping du portail officiel est un bonus : le mode import et un corpus local versionné doivent permettre une démonstration même si le portail est indisponible.

## État initial constaté

- `backend/main.py` concentre une grande partie de l'API et contient des routes non protégées ;
- import ZIP, OCR, règles NLP, recherche et interface React existent sous forme partielle ;
- la recherche nommée FTS utilise actuellement `LIKE`/`ILIKE` ;
- le ML est un prototype sans protocole d'évaluation défendable ;
- tests et installation ne sont pas reproductibles dans l'état audité.

Consulter chaque `TICKETS.md` pour les tâches détaillées.

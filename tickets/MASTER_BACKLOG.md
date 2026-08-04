# Ordonnancement maître et dépendances

## Séquence d'exécution

| Rang | Ticket | Priorité | Dépend de | Livrable observable |
|---:|---|---|---|---|
| 1 | SQ-01 | P0 | — | secrets et bootstrap sûrs |
| 2 | SQ-02 | P0 | SQ-01 | matrice RBAC et routes protégées |
| 3 | SQ-03 | P0 | SQ-01 | installation et validation reproductibles |
| 4 | SQ-04 | P0 | SQ-03 | migrations et schémas API cohérents |
| 5 | ING-01 | P0 | SQ-02, SQ-04 | import de fichiers sécurisé |
| 6 | ING-02 | P0 | ING-01 | états et jobs persistants |
| 7 | ING-03 | P1 | ING-02 | connecteur source/replay remplaçable |
| 8 | ING-04 | P1 | ING-01 | corpus de démonstration gouverné |
| 9 | OCR-01 | P1 | ING-02 | stratégie unique d'extraction |
| 10 | OCR-02 | P1 | SQ-03, OCR-01 | OCR portable et diagnostiquable |
| 11 | OCR-03 | P1 | OCR-01 | qualité et pages persistées |
| 12 | OCR-04 | P1 | OCR-02, ING-04 | baseline OCR mesurée |
| 13 | NLP-01 | P1 | SQ-04, OCR-03 | champs métier canoniques |
| 14 | NLP-02 | P1 | NLP-01 | extraction explicable |
| 15 | NLP-03 | P1 | NLP-01, SQ-02 | validation humaine |
| 16 | NLP-04 | P1 | NLP-02, NLP-03, ING-04 | baseline NLP mesurée |
| 17 | SRC-04 | P1 | SQ-03 | client API React unique |
| 18 | SRC-01 | P1 | NLP-01, SRC-04 | recherche correctement qualifiée |
| 19 | SRC-02 | P1 | NLP-03, OCR-03, SRC-01 | fiche avec preuves |
| 20 | SRC-03 | P1 | SRC-02, SQ-02 | comparaison/export audité |
| 21 | ANA-01 | P1 | NLP-01 | KPI métier calculés |
| 22 | ANA-02 | P1 | ING-02, OCR-03, NLP-03 | dashboard qualité |
| 23 | ANA-03 | P1 | ANA-01, ANA-02 | tests/benchmark analytics |
| 24 | ADM-01 | P1 | SQ-02 | gestion utilisateurs/sessions |
| 25 | ADM-02 | P1 | ADM-01, ING-01, NLP-03, SRC-03 | audit complet |
| 26 | ADM-03 | P1 | ING-02, ADM-02 | monitoring sécurisé |
| 27 | ML-01 | P2 | NLP-03, NLP-04, ING-04 | dataset et splits validés |
| 28 | ML-02 | P2 | ML-01 | classification évaluée |
| 29 | ML-03 | P2 | NLP-01, NLP-03 | signaux explicables |
| 30 | ML-04 | P2 | ING-02, ML-02, ML-03, ADM-02 | réentraînement gouverné |

## Règle de parallélisation

La parallélisation n'est autorisée qu'après lecture des dépendances. Par défaut, travailler séquentiellement. Les seuls travaux pouvant être menés en parallèle sans modification de mêmes fichiers sont :

- ING-04 avec ING-02 après ING-01 ;
- SRC-04 avec OCR-01/OCR-02 après SQ-03 ;
- documentation de métriques après disponibilité du corpus et des scripts.

Ne pas paralléliser deux tickets qui modifient `backend/main.py`, `backend/models.py`, les migrations Alembic ou `frontend-react/src/App.jsx` sans coordination explicite.

## Critère de passage PFA

La soutenance peut présenter les gates G0 à G4. G5 ne doit être présenté que si les tickets ML sont terminés avec métriques reproductibles ; sinon il reste une perspective clairement annoncée.


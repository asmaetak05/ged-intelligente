# État d'avancement des tickets

**Règle :** ce fichier est la source de vérité de l'avancement. Une ligne ne devient `Terminé` que sur preuve. Initialement, aucun ticket n'est terminé.

| Ticket | État | Priorité | Dépendances | Date | Preuves / résultat | Fichiers modifiés |
|---|---|---|---|---|---|---|
| SQ-01 | À faire | P0 | — | — | — | — |
| SQ-02 | À faire | P0 | SQ-01 | — | — | — |
| SQ-03 | À faire | P0 | SQ-01 | — | — | — |
| SQ-04 | À faire | P0 | SQ-03 | — | — | — |
| ING-01 | À faire | P0 | SQ-02, SQ-04 | — | — | — |
| ING-02 | À faire | P0 | ING-01 | — | — | — |
| ING-03 | À faire | P1 | ING-02 | — | — | — |
| ING-04 | À faire | P1 | ING-01 | — | — | — |
| OCR-01 | À faire | P1 | ING-02 | — | — | — |
| OCR-02 | À faire | P1 | SQ-03, OCR-01 | — | — | — |
| OCR-03 | À faire | P1 | OCR-01 | — | — | — |
| OCR-04 | À faire | P1 | OCR-02, ING-04 | — | — | — |
| NLP-01 | À faire | P1 | SQ-04, OCR-03 | — | — | — |
| NLP-02 | À faire | P1 | NLP-01 | — | — | — |
| NLP-03 | À faire | P1 | NLP-01, SQ-02 | — | — | — |
| NLP-04 | À faire | P1 | NLP-02, NLP-03, ING-04 | — | — | — |
| SRC-04 | À faire | P1 | SQ-03 | — | — | — |
| SRC-01 | À faire | P1 | NLP-01, SRC-04 | — | — | — |
| SRC-02 | À faire | P1 | NLP-03, OCR-03, SRC-01 | — | — | — |
| SRC-03 | À faire | P1 | SRC-02, SQ-02 | — | — | — |
| ANA-01 | À faire | P1 | NLP-01 | — | — | — |
| ANA-02 | À faire | P1 | ING-02, OCR-03, NLP-03 | — | — | — |
| ANA-03 | À faire | P1 | ANA-01, ANA-02 | — | — | — |
| ADM-01 | À faire | P1 | SQ-02 | — | — | — |
| ADM-02 | À faire | P1 | ADM-01, ING-01, NLP-03, SRC-03 | — | — | — |
| ADM-03 | À faire | P1 | ING-02, ADM-02 | — | — | — |
| ML-01 | À faire | P2 | NLP-03, NLP-04, ING-04 | — | — | — |
| ML-02 | À faire | P2 | ML-01 | — | — | — |
| ML-03 | À faire | P2 | NLP-01, NLP-03 | — | — | — |
| ML-04 | À faire | P2 | ING-02, ML-02, ML-03, ADM-02 | — | — | — |

## États autorisés

- `À faire` : aucun travail réalisé ou vérifié.
- `En cours` : un seul outil/intervenant travaille actuellement sur le ticket.
- `Partiel` : une partie du ticket est réalisée, mais au moins un critère d'acceptation manque.
- `Bloqué` : une dépendance, une décision métier ou un accès manque ; le blocage doit être décrit dans la colonne de preuves.
- `Terminé` : tous les critères d'acceptation sont validés et les preuves sont enregistrées.


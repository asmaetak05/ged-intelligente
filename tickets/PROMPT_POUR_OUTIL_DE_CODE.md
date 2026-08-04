# Prompt prêt à donner à un autre outil de code

Copier le texte ci-dessous, puis remplacer `TICKET_ID` par le ticket éligible indiqué dans `tickets/TICKET_STATUS.md`.

```text
Tu travailles dans le dépôt GED intelligente. Ton unique mission pour cette session est le ticket TICKET_ID.

Lis intégralement, dans cet ordre :
1. tickets/START_HERE.md
2. tickets/EXECUTION_GUIDE.md
3. tickets/MASTER_BACKLOG.md
4. tickets/TICKET_STATUS.md
5. le fichier tickets/<module>/TICKETS.md qui contient TICKET_ID

Respecte strictement ces règles :
- ne travaille que sur TICKET_ID ; ne commence aucun ticket suivant ;
- vérifie que toutes ses dépendances sont marquées Terminé ; sinon arrête-toi et explique le blocage ;
- préserve tous les changements existants non liés ;
- lis le code et les tests concernés avant toute modification ;
- ne simule pas de données ou de résultat ;
- ajoute ou adapte les tests nécessaires ;
- traite toute migration avec upgrade et downgrade sûrs ;
- n'expose jamais de secrets, tokens, mots de passe ou données métier sans autorisation ;
- exécute les validations applicables avant et après la modification ;
- n'affirme jamais qu'une commande a réussi si tu ne l'as pas exécutée ;
- mets à jour uniquement la ligne de TICKET_ID dans tickets/TICKET_STATUS.md, avec des preuves factuelles.

À la fin, réponds obligatoirement en utilisant exactement le modèle tickets/RESULT_TEMPLATE.md. Indique les échecs préexistants séparément des régressions que tu aurais créées.
```

## Exemple de premier lancement

```text
Remplace TICKET_ID par SQ-01. Si SQ-01 est terminé et prouvé, le prochain ticket admissible est SQ-02, puis SQ-03.
```


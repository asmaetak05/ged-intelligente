# Démarrage pour un outil de code

Ce dossier est le contrat de réalisation du projet. Le but est d'obtenir un MVP de PFA fonctionnel et vérifiable, et non de produire des écrans ou des affirmations non démontrables.

## Mission

Implémenter les tickets dans l'ordre défini par `MASTER_BACKLOG.md`, sans sortir du périmètre du ticket actif. Chaque ticket doit laisser le projet dans un état au moins aussi stable qu'avant son démarrage.

## Règles impératives

1. Lire intégralement `EXECUTION_GUIDE.md`, `MASTER_BACKLOG.md` et `TICKET_STATUS.md` avant toute modification.
2. Choisir **un seul ticket actif**. Ne pas avancer sur un autre ticket, même s'il semble simple.
3. Lire le code directement concerné, les tests associés et les migrations avant de modifier quoi que ce soit.
4. Préserver toutes les modifications non liées déjà présentes dans le dépôt.
5. Ne jamais simuler une fonctionnalité avec des valeurs fixes, des mocks de production ou des données inventées.
6. Ne jamais ajouter de secret, mot de passe, token ou donnée sensible dans le code, les logs ou Git.
7. Ne jamais supprimer de données, fichiers ou migrations existants sans une migration/solution de repli explicitement prévue par le ticket.
8. Créer ou mettre à jour les tests du ticket. Une fonction sans preuve de validation est incomplète.
9. Mettre à jour la documentation visée par le ticket.
10. Ne marquer un ticket `Terminé` que si tous ses critères d'acceptation sont satisfaits et prouvés.

## Interdictions de périmètre

- ne pas refactorer l'ensemble du backend sous prétexte de traiter un ticket local ;
- ne pas commencer le ML avant que les tickets prérequis soient terminés ;
- ne pas rendre publiques des routes métier pour simplifier les tests ;
- ne pas changer de framework, de base de données ou de système de queue sans décision écrite dans un ticket ;
- ne pas modifier l'historique Git ou écraser les changements d'un autre intervenant.

## Définition de « terminé »

Un ticket est terminé seulement si :

- le code répond au besoin décrit ;
- les critères d'acceptation du ticket sont validés ;
- les tests nouveaux ou modifiés passent ;
- les tests non liés n'ont pas régressé, dans la limite de l'environnement disponible ;
- les limites ou échecs éventuels sont consignés dans le résultat ;
- `TICKET_STATUS.md` est mis à jour avec la date, les preuves et les fichiers touchés.

## Première action

Commencer par le ticket `SQ-01`. Ne pas traiter `SQ-02` avant d'avoir obtenu et consigné le résultat de `SQ-01`.


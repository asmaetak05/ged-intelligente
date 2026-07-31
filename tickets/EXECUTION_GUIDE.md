# Guide d'exécution exact

Ce guide définit la méthode obligatoire pour chaque ticket. Il est conçu pour que n'importe quel outil de code puisse passer le relais sans ambiguïté.

## 1. Préparation de la session

Avant chaque ticket :

1. Lire `tickets/START_HERE.md`, `tickets/MASTER_BACKLOG.md`, `tickets/TICKET_STATUS.md` et le `TICKETS.md` du module.
2. Vérifier que le ticket choisi est le premier ticket éligible dans `TICKET_STATUS.md`.
3. Exécuter et consigner :

```powershell
git status --short
git diff --stat
```

4. Lire les fichiers cités par le ticket, leurs tests et les appels directs qui pourraient être affectés.
5. Définir en une phrase le comportement observable à obtenir. Exemple : « Sans `JWT_SECRET_KEY` valide, l'API échoue avec un message explicite avant d'ouvrir une route. »

Ne pas poursuivre si le dépôt contient des modifications qui se chevauchent avec le ticket et dont l'origine est inconnue. Les préserver et signaler le conflit.

## 2. Baseline de validation

L'outil doit mesurer l'état avant modification, sans masquer un échec existant.

### Backend

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Si l'environnement Python est absent ou incomplet, le noter comme blocage factuel. Ne pas déclarer que les tests passent.

### Frontend

```powershell
Set-Location frontend-react
npm ci --no-audit --no-fund
npm run test -- --run
npm run build
```

Si `npm ci` échoue à cause d'un répertoire `node_modules` existant, ne pas supprimer ce répertoire sans vérifier qu'il n'appartient pas à un autre travail en cours. Documenter l'échec ou demander une décision.

### Migrations

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Exécuter les commandes adaptées au ticket. Les commandes non applicables doivent être marquées « non concerné », pas « réussies ».

## 3. Réalisation

1. Implémenter d'abord le modèle de données et les migrations, puis services/repositories, API, frontend, tests et documentation.
2. Utiliser les conventions déjà présentes dans le dépôt : FastAPI, SQLAlchemy, Alembic, React/Vite, Vitest.
3. Garder les changements petits et cohérents ; ne modifier que les fichiers nécessaires.
4. Pour toute migration : prévoir `upgrade` et `downgrade`, tester sur une base vide et éviter toute perte de données.
5. Pour toute API : définir validation d'entrée, autorisation, erreurs, réponses et tests.
6. Pour tout écran : utiliser le client API centralisé, gérer loading/empty/error, ne pas contenir de données métier simulées.
7. Pour toute extraction : conserver valeur brute, valeur normalisée, source, page/extrait, méthode et version.
8. Pour tout traitement asynchrone : persister un état, une erreur et une possibilité de reprise avant d'afficher une progression.

## 4. Validation après modification

Exécuter, selon le ticket, dans cet ordre :

1. test ciblé créé ou modifié ;
2. tests du module ;
3. tests backend globaux ;
4. tests frontend ;
5. build frontend ;
6. migration sur base vide ;
7. scénario manuel décrit dans le ticket.

Tout échec doit être classé :

- `Régression créée` : à corriger avant de terminer le ticket ;
- `Échec préexistant` : à prouver avec la baseline et à inscrire dans le résultat ;
- `Bloquant environnement` : dépendance/outillage absent, avec commande et erreur exacte ;
- `Hors périmètre` : créer une proposition de ticket, sans l'implémenter.

## 5. Mise à jour d'état

Après validation, mettre à jour une seule ligne dans `TICKET_STATUS.md` :

- état : `Terminé`, `Partiel`, `Bloqué` ou `À faire` ;
- date ;
- résumé factuel ;
- preuves : commandes/tests/scénario ;
- fichiers modifiés.

Ne jamais écrire `Terminé` si un seul critère d'acceptation manque.

## 6. Passation obligatoire

La réponse finale de l'outil doit suivre exactement `RESULT_TEMPLATE.md`. Elle doit notamment dire :

- le ticket traité ;
- ce qui est réellement fonctionnel ;
- ce qui reste incomplet ;
- les commandes exécutées et leur résultat ;
- les fichiers modifiés ;
- le prochain ticket éligible.

## 7. Points de contrôle (gates)

| Gate | Tickets requis | Décision |
|---|---|---|
| G0 — socle sûr | SQ-01 à SQ-04 | Interdit de présenter un déploiement sans ce gate |
| G1 — entrée fiable | ING-01 à ING-04 | Import et corpus local démontrables |
| G2 — contenu exploitable | OCR-01 à OCR-04, NLP-01 à NLP-04 | Mesures et revue humaine disponibles |
| G3 — valeur métier | SRC-01 à SRC-04, ANA-01 à ANA-03 | Recherche, fiche et KPI réels |
| G4 — usage encadré | ADM-01 à ADM-03 | Rôles, audit et monitoring maîtrisés |
| G5 — IA expérimentale | ML-01 à ML-04 | À présenter seulement avec métriques réelles |

Un gate non validé doit apparaître explicitement dans toute démo ou document de soutenance.


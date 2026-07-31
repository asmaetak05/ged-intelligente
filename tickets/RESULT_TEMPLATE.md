# Modèle obligatoire de compte rendu d'un ticket

Chaque outil de code doit terminer son intervention avec ce format, sans affirmer qu'un test ou une fonctionnalité est réussi sans preuve.

```markdown
## Ticket traité

- ID : `XXX-00`
- État final : `Terminé | Partiel | Bloqué`
- Objectif observable : une phrase.

## Réalisation

- Ce qui a été ajouté ou modifié.
- Comportement réellement obtenu.
- Décisions techniques prises et raison.

## Fichiers modifiés

- `chemin/fichier.ext` — rôle de la modification.

## Validation

| Vérification | Commande ou scénario | Résultat |
|---|---|---|
| Test ciblé | `...` | réussi / échoué / non concerné |
| Tests module | `...` | réussi / échoué / bloqué |
| Tests globaux | `...` | réussi / échec préexistant prouvé |
| Build frontend | `...` | réussi / non concerné |
| Migration | `...` | réussie / non concernée |
| Scénario manuel | étapes exactes | résultat |

## Critères d'acceptation

- [x] Critère validé, avec preuve.
- [ ] Critère non validé, raison précise.

## Limites, risques ou blocages

- Éléments qui empêchent de déclarer le ticket terminé ou dette créée.

## Mise à jour du backlog

- Ligne `XXX-00` mise à jour dans `tickets/TICKET_STATUS.md` : oui/non.
- Prochain ticket éligible : `YYY-00`.
```


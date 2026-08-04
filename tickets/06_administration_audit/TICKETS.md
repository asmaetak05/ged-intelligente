# 06 — Administration, audit et exploitation

**Priorité du module : P0/P1.** Pour un contexte DSI, l'administration et l'audit ne sont pas des écrans secondaires.

## ADM-01 — Finaliser utilisateurs, rôles et sessions

**État : Partiel.** Utilisateurs, rôles et endpoints existent ; le modèle de rôle doit être aligné avec la matrice RBAC et les routes restent inégalement protégées.

### Réalisation attendue

1. Aligner `backend/models.py`, `backend/auth/rbac.py`, `backend/routers/users.py` sur les rôles définis dans `docs/MATRICE_RBAC.md`.
2. Ajouter activation/désactivation d'un compte, réinitialisation administrée et interdiction de supprimer le dernier administrateur.
3. Ajouter expiration/révocation de refresh token ou liste de sessions, selon le périmètre MVP retenu.
4. Mettre à jour `frontend-react/src/pages/Users.jsx`, `Profile.jsx` et `Login.jsx` avec droits réels et messages de sécurité.
5. Ajouter tests de verrouillage, changement de mot de passe, rôles et comptes inactifs.

### Critères d'acceptation

- un compte inactif ne peut pas obtenir de session ;
- la suppression d'un rôle n'ouvre pas de privilège implicite ;
- tous les changements utilisateurs sont audités.

## ADM-02 — Rendre l'audit complet et exploitable

**État : Partiel.** `AuditEvent`, `backend/routers/audit.py` et `frontend-react/src/pages/Audit.jsx` existent ; la couverture des actions est incomplète.

### Réalisation attendue

1. Définir événements obligatoires : authentification, import, traitement, relance, consultation fichier, correction, export, administration, échec d'autorisation.
2. Créer `backend/services/audit_service.py` et remplacer les insertions dispersées.
3. Ajouter identifiant de corrélation avec le middleware request ID, acteur, type de ressource, résultat et adresse IP traitée selon politique définie.
4. Empêcher modification/suppression par les routes métier ordinaires.
5. Ajouter filtres date/utilisateur/action/ressource et export réservé aux auditeurs.

### Critères d'acceptation

- un scénario import → correction → export génère une chaîne d'audit complète ;
- les données sensibles et tokens ne sont jamais inclus dans les événements ;
- l'audit est lisible dans l'interface et testable par API.

## ADM-03 — Assainir monitoring et console technique

**État : Partiel/risqué.** `Monitoring.jsx`, `/system/monitoring`, `/system/schema` et le WebSocket console existent ; celui-ci met actuellement le token dans l'URL et doit être évalué avec prudence.

### Réalisation attendue

1. Limiter le monitoring à des métriques techniques utiles : health, DB, jobs, source, durée, erreurs ; ne jamais exposer secrets, commandes ou schéma complet à un utilisateur standard.
2. Remplacer la console WebSocket d'exécution de commandes par logs de jobs filtrés, ou isoler cette fonction derrière rôle admin technique et environnement non production.
3. Utiliser `wss://` en cible et mécanisme d'authentification sans token long dans la query string.
4. Créer alertes basiques : source indisponible, queue bloquée, taux d'échec élevé, stockage bas.
5. Ajouter tests de non-exposition et documentation d'exploitation.

### Critères d'acceptation

- un analyste ne voit aucun détail d'infrastructure sensible ;
- les échecs de pipeline sont visibles avec un identifiant corrélable ;
- aucune console de commande n'est exposée au pilote.


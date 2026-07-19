# 🎫 Lot 8 : DevOps, Logging & Observabilité (DevOps & Observability)

## 📌 Présentation du Lot
Ce lot prépare la mise en production de la plateforme en configurant des conteneurs multi-stages Docker, en mettant en œuvre la journalisation structurée (pour faciliter le débogage en production) et en intégrant des outils de monitoring (Prometheus et Grafana).

* **Complexité globale** : Medium
* **Composants impactés** : `Dockerfile`, `docker-compose.yml`, Prometheus config files, logging setup in backend
* **Indépendance git** : Excellente. Ce lot n'impacte que les fichiers de configuration de déploiement et de monitoring, ainsi que la configuration transversale des logs. Il ne modifie pas les écrans ou les algorithmes.

---

## 📋 Liste des Tickets Associés

### 1. OPS-01 — Docker Compose multi-services pour la production 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `Dockerfile`, `docker-compose.yml`
* **Scénarios de test liés** : Scénarios OPS-01 et OPS-02
* **Description** : Refactoriser le `Dockerfile` pour utiliser des builds multi-stages (optimisation de la taille de l'image de production en séparant les dépendances de build et d'exécution). Configurer `docker-compose.yml` pour orchestrer :
  - L'API FastAPI backend.
  - La base PostgreSQL de production.
  - La file d'attente Redis pour les tâches asynchrones.
  - L'application React frontend (servie par Nginx).

### 2. OPS-02 — Exportateur de Métriques Prometheus 🟠
* **Priorité** : 🟠 P1
* **Effort** : S (1 j)
* **Composant** : `backend/main.py`, Prometheus config
* **Scénarios de test liés** : `ST-PE-001`
* **Description** : Intégrer l'exportateur Prometheus dans FastAPI (en utilisant `prometheus-fastapi-instrumentator`) pour exposer un endpoint `/metrics` sécurisé.
* **Travail** : Exposer les temps de latence HTTP, le nombre d'erreurs 500, et le temps de traitement moyen par page en OCR.

### 3. OPS-03 — Tableaux de bord Grafana 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : Grafana configurations
* **Scénarios de test liés** : `ST-PE-003`
* **Description** : Configurer un dashboard Grafana standardisé lisant les métriques exposées par Prometheus.
* **Travail** :
  - Créer des graphes pour suivre l'utilisation CPU/Mémoire, le débit de requêtes HTTP et le statut des tâches de fond OCR/NLP.

### 4. B-05 — Journalisation structurée avec structlog 🟠
* **Priorité** : 🟠 P1
* **Effort** : S (1 j)
* **Composant** : Backend logging middleware
* **Scénarios de test liés** : `ST-API-005`
* **Description** : Remplacer les `print()` rudimentaires du backend par des logs structurés au format JSON à l'aide de la bibliothèque `structlog`. Cela permet d'exporter facilement les logs vers des agrégateurs de logs (ex. Elasticsearch/Kibana ou Grafana Loki).

---

## 🛠️ Description des Travaux
1. **Refactoring Docker** :
   - Écrire un `Dockerfile` optimisé pour Python 3.11.
   - Configurer Nginx pour servir les assets statiques compilés du frontend React.
2. **Configuration Prometheus/Grafana** :
   - Ajouter un dossier `monitoring/` contenant les fichiers `prometheus.yml` et de provisionnement des tableaux de bord Grafana.

---

## 🧪 Critères de Validation et Non-régression
- **Taille de l'image** : Vérifier que l'image de production finale est optimisée (taille < 500 Mo hors modèles spaCy lourds).
- **Vérification d'export des métriques** : Effectuer un appel `curl http://localhost:8000/metrics` et s'assurer que les métriques FastAPI standard s'affichent correctement en texte brut.
- **Visualisation Grafana** : S'assurer que le tableau de bord Grafana se connecte à la source de données Prometheus locale et affiche les courbes d'activité.

# 🎫 Lot 6 : Frontend — Dashboard & Visualisation BI (Dashboard & BI)

## 📌 Présentation du Lot
Ce lot modernise l'interface utilisateur en optimisant le tableau de bord décisionnel (widgets KPIs, graphiques Recharts responsifs, intégration de Zustand pour la gestion d'état globale et Axios pour les retours utilisateur en cas d'erreurs d'API).

* **Complexité globale** : Medium
* **Composants impactés** : `frontend-react/src/components/Dashboard.jsx`, `frontend-react/src/store/` (nouveau dossier), `frontend-react/src/api/` (nouveau dossier)
* **Indépendance git** : Très bonne. Il n'édite aucun fichier backend, et se concentre uniquement sur la partie présentation BI du frontend React.

---

## 📋 Liste des Tickets Associés

### 1. UI-01 — Gestion d'état globale avec Zustand 🟠
* **Priorité** : 🟠 P1
* **Effort** : M (2 j)
* **Composant** : `frontend-react/src/store/useUIStore.js`
* **Scénarios de test liés** : Scénario F-01
* **Description** : Installer Zustand et configurer un store global pour suivre l'état de l'application (ex. menu latéral ouvert/fermé, mode sombre, données KPIs en cache session).

### 2. UI-02 — Intercepteur Axios + Notifications Toast (Sonner) 🟠
* **Priorité** : 🟠 P1
* **Effort** : S (1 j)
* **Composant** : `frontend-react/src/api/axios.js`
* **Scénarios de test liés** : Scénario F-02
* **Description** : Centraliser les appels API. Configurer un intercepteur Axios pour intercepter les erreurs HTTP (4xx, 5xx) et afficher un toast visuel temporaire (notification d'erreur en rouge) en utilisant la bibliothèque `sonner` ou `react-toastify`.

### 3. UI-03 — Skeletons de chargement pour les KPIs et Graphiques 🟠
* **Priorité** : 🟠 P1
* **Effort** : S (1 j)
* **Composant** : `frontend-react/src/components/Skeleton.jsx`
* **Scénarios de test liés** : `ST-DB-005`
* **Description** : Remplacer les indicateurs de chargement textuels rustiques ("Loading...") par des squelettes de chargement (Skeletons) animés en CSS (gris clignotant) pour les widgets KPIs et les conteneurs de graphiques en attendant le retour de l'API.

---

## 🛠️ Description des Travaux
1. **Création des Stores Zustand** :
   - Initialiser le dossier `frontend-react/src/store` et configurer `useUIStore` et `useAuthStore`.
2. **Refactoring de `Dashboard.jsx`** :
   - Remplacer les composants de chargement par `<Skeleton />`.
   - Utiliser `ResponsiveContainer` de Recharts pour assurer que les graphiques se redimensionnent correctement sur tablette et mobile.

---

## 🧪 Critères de Validation et Non-régression
- **Ressenti UX** : Brider artificiellement la vitesse réseau de l'API dans le navigateur et s'assurer que les skeletons de chargement s'affichent correctement en clignotant, puis disparaissent dès que les données arrivent.
- **Erreurs API** : Arrêter le serveur backend API, charger le dashboard, et vérifier qu'une notification toast d'erreur rouge apparaît en bas de l'écran signalant la perte de connexion avec le serveur.
- **Responsivité** : Réduire la taille de la fenêtre du navigateur et s'assurer que les graphiques s'adaptent dynamiquement sans déborder de la grille.

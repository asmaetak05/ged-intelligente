# Phase 9 — Polish final & soutenance

> **Effort** : ½ journée · **Risque** : faible · **Pré-requis** : Phases 1–8 terminées (tout est prêt)

---

## T9.1 — Vérification end-to-end sur machine vierge

**Description & objectif** : s'assurer que la démo tourne réellement, pas seulement sur la machine de dev.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | Sur une VM ou un conteneur propre, suivre `docs/installation.md` du début à la fin. |
| `repo` | `CMD` | `bash scripts/run_all_tests.sh` → doit finir par `✅ ALL TESTS PASSED`. |
| `repo` | `CMD` | Lancer l'API + frontend, exécuter le scénario `Scenario_Demo.md` complet chronométré. |

**Plan de vérification** :
- [ ] Temps total d'installation ≤ 15 min.
- [ ] Démo 5 min exécutée sans accroc.
- [ ] Tous les tests passent.

---

## T9.2 — Captures d'écran clés

**Description & objectif** : produire les visuels pour rapport + slides + README.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `CMD` | Capturer (en PNG 1920×1080) :<br>1. Dashboard avec KPIs réels<br>2. Recherche avec résultats<br>3. Détail d'un AO (texte OCR visible)<br>4. Upload en cours (barre progression)<br>5. Monitoring<br>6. PredictorML avec anomalies<br>7. /docs FastAPI (auto-généré) |
| `docs` | `MODIFY` | `docs/images/` : stocker les captures, nommer `01-dashboard.png`, etc. |
| `docs` | `MODIFY` | `docs/images/README.md` : légende de chaque capture. |

**Plan de vérification** :
- [ ] 7+ captures nettes, lisibles en 16:9.
- [ ] Aucune donnée sensible (numéro de téléphone, email nominatif) visible.

---

## T9.3 — GIF de démo

**Description & objectif** : montrer le produit en mouvement dans le README.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/images/demo.gif` (15–20 s, < 5 Mo) capturé avec `ffmpeg` ou `ScreenToGif`. Séquence : Dashboard → Recherche → Détail → Upload. |
| `repo` | `MODIFY` | `README.md` : insérer `![Démo](docs/images/demo.gif)`. |

**Plan de vérification** :
- [ ] Le GIF s'affiche dans le README GitHub.
- [ ] Taille < 5 Mo.

---

## T9.4 — Répétitions de soutenance

**Description & objectif** : atteindre la maîtrise du timing.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `NEW` | `docs/_repetitions.md` (privé) : log des 3 répétitions :<br>- Date, durée, problèmes, ajustements. |
| `repo` | `CMD` | Répétition 1 (seul) : 15 min. |
| `repo` | `CMD` | Répétition 2 (devant un ami) : 15 min. |
| `repo` | `CMD` | Répétition 3 (en conditions réelles, salle, vidéoprojecteur) : 20 min. |

**Plan de vérification** :
- [ ] 3 répétitions enregistrées dans `_repetitions.md`.
- [ ] Timing total ≤ 20 min (10 min présentation + 10 min Q&A).

---

## T9.5 — Anticipation des questions du jury

**Description & objectif** : préparer les réponses aux questions probables.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `docs` | `NEW` | `docs/QA_Anticipation.md` (≈ 100 lignes) avec 15–20 Q/R :<br>1. **Pourquoi pas PostgreSQL en prod ?** — Réponse : POC, échelle 30–50 AO, SQLite suffit ; bascule prévue.<br>2. **Pourquoi pas GPT pour le NLP ?** — Coût, latence, déterminisme, données potentiellement confidentielles.<br>3. **Quelle volumétrie visée ?** — 1000 AO/an (estimation ; pipeline scalable).<br>4. **Pourquoi spaCy fr_core_news_sm et pas un LLM ?** — Modèle local, déterministe, suffisant pour cette tâche ; un fine-tuning LLM serait overkill.<br>5. **Comment gérez-vous les doublons ?** — Clé unique `numero_appel_offre` (upsert dans `repository.create_or_update`).<br>6. **Que se passe-t-il si un PDF est protégé par mot de passe ?** — Try/except dans `read_pdf`, marqué `failed`, retrain manuel possible.<br>7. **Pourquoi LinearSVC et pas Random Forest ?** — Texte sparse haute dimension, SVM linéaire plus performant et rapide.<br>8. **Comment validez-vous les extractions ?** — `extractions_nlp` stocke la source et le score ; un humain peut corriger via une UI admin (à venir).<br>9. **Quel est le taux de succès OCR réel ?** — Calculé dynamiquement dans `/api/v1/analytics/kpis`.<br>10. **Pourquoi pas d'authentification ?** — POC en interne ; ajout d'un JWT prévu en V2.<br>11. **Comment déployez-vous ?** — Docker Compose (API + DB), frontend buildé en statique.<br>12. **Quel est le coût d'inférence ?** — 200 ms par AO (mesuré), 30 AO en 6 s.<br>13. **Pourquoi pas un dashboard plus interactif (drill-down) ?** — Recharts couvre 80 % des besoins ; drill-down dans V2.<br>14. **Que manque-t-il pour passer en prod ?** — Auth, monitoring (Prometheus), logging centralisé, tests de charge, CI/CD.<br>15. **Pourquoi React et pas Vue/Angular ?** — Compétence de l'équipe, écosystème (Recharts, Tailwind). |

**Plan de vérification** :
- [ ] Toutes les questions sont répondues sans hésitation.
- [ ] Aucune ne laisse sans réponse ("on n'a pas eu le temps" n'est pas une réponse valable → reformuler en "volontairement écarté pour ce POC car…").

---

## T9.6 — Tag de version

**Description & objectif** : figer l'état présenté.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | `git tag -a v1.0.0-soutenance -m "Version présentée en soutenance"` |
| `repo` | `CMD` | `git push origin v1.0.0-soutenance` |

**Plan de vérification** :
- [ ] `git tag` liste `v1.0.0-soutenance`.
- [ ] Le tag est accessible sur le remote.

---

## T9.7 — Backup final

**Description & objectif** : ne pas perdre le travail de 9 jours.

**Modifications** :

| Module | Action | Détail |
|---|---|---|
| `repo` | `CMD` | Copier le repo entier vers un disque externe / cloud (OneDrive, Google Drive). |
| `repo` | `CMD` | Exporter aussi : `ged.db`, `ml/models/*.joblib`, `data/samples/*.zip`, `docs/Slides_Soutenance.pdf`, `docs/Rapport_Stage.pdf`. |

**Plan de vérification** :
- [ ] 3 copies indépendantes du livrable final (local + GitHub + cloud).

---

## ✅ Critères de sortie de la Phase 9 (soutenance)

- [ ] Démo 5 min exécutée 3 fois sans accroc.
- [ ] Toutes les captures sont prêtes.
- [ ] Les 15 Q/R sont maîtrisées.
- [ ] Tag `v1.0.0-soutenance` posé.
- [ ] 3 copies du livrable final existent.
- [ ] Le rapport et les slides sont sur clé USB (au cas où).

**Effort total** : ½ journée.

---

## 🎉 Bilan global du projet

Une fois la Phase 9 terminée :

- **Couverture du plan initial** : ≥ 80 % (vs ~30 % au moment de l'audit).
- **Démo soutenable** : oui, end-to-end, sans mocks.
- **Données réelles** : ≥ 30 AO ingérés avec OCR + NLP + ML.
- **Code testable** : coverage ≥ 60 %, scripts `run_all_tests.sh` reproductible.
- **Documentation** : rapport, slides, guide, architecture, Q/R.
- **Valeur académique** : POC crédible, choix techniques justifiés, limites assumées.

# Présentation reformulée — Observatoire intelligent des dossiers d'appels d'offres

## 1. Identité du projet

**Nom académique :** GED intelligente des appels d'offres  
**Nom fonctionnel recommandé :** Observatoire intelligent des dossiers d'appels d'offres  
**Cadre :** projet de fin d'année réalisé au sein de la Direction des Systèmes d'Information du Ministère de l'Équipement et de l'Eau du Maroc  
**Nature :** prototype d'aide à la recherche, à la structuration et à l'analyse documentaire ; il ne remplace ni le portail officiel ni la décision humaine.

## 2. Définition du projet

Le projet vise à transformer des dossiers d'appels d'offres publiés sous forme de pages web, archives et documents PDF/DOCX hétérogènes en un patrimoine documentaire **collecté, traçable, interrogeable et exploitable**.

La plateforme automatise la chaîne allant de l'acquisition d'un dossier à sa consultation : collecte ou import, validation, décompression, extraction native ou OCR, structuration de métadonnées, indexation, recherche, contrôle humain et restitution sous forme de fiches et d'indicateurs.

L'intelligence du système ne réside pas seulement dans l'emploi d'algorithmes. Elle réside dans sa capacité à :

- conserver la provenance de chaque information ;
- mesurer son niveau de qualité ;
- signaler une information incertaine ;
- permettre à un utilisateur de la corriger ;
- apprendre des corrections lorsque les données deviennent suffisantes ;
- expliquer les résultats au lieu de produire une décision opaque.

## 3. Contexte et problématique

Les dossiers d'appels d'offres contiennent des informations essentielles : référence, objet, organisme acheteur, dates, montant estimatif, caution, lieu, qualification, agrément, délai et clauses techniques. Ces informations sont dispersées dans des documents de formats, langues et qualités variables.

La recherche manuelle entraîne :

- un temps de lecture important ;
- un risque d'omission ou d'erreur de saisie ;
- une difficulté à comparer plusieurs dossiers ;
- une faible capacité d'analyse transversale ;
- une dépendance à la disponibilité et à l'ergonomie du portail source ;
- une impossibilité de mesurer la qualité des données sans structuration préalable.

**Question directrice :** comment transformer automatiquement des dossiers d'appels d'offres hétérogènes en informations structurées, recherchables et vérifiables, tout en conservant la preuve documentaire et le contrôle humain ?

## 4. Vision

> Permettre à un agent autorisé de retrouver, comprendre, comparer et contrôler rapidement un dossier d'appel d'offres, sans perdre le lien avec le document officiel d'origine.

La cible n'est pas « remplacer l'expert », mais réduire le travail mécanique et concentrer l'expertise humaine sur la validation et l'analyse.

## 5. Objectifs

### Objectif général

Concevoir un prototype robuste de chaîne documentaire intelligente permettant d'acquérir, structurer, indexer et restituer les informations contenues dans les dossiers d'appels d'offres.

### Objectifs spécifiques

1. **Acquérir** les dossiers depuis un connecteur web ou un import manuel.
2. **Garantir la traçabilité** grâce à la source, la date de collecte, le hash et l'historique de traitement.
3. **Extraire le texte** des PDF natifs, scannés et documents bureautiques, en français et en arabe lorsque possible.
4. **Structurer les champs métier** avec leur page, extrait justificatif, méthode et score de qualité.
5. **Permettre la validation humaine** des valeurs extraites et conserver les corrections.
6. **Rechercher** dans le contenu et les métadonnées avec filtres, classement et facettes.
7. **Comparer** des dossiers et produire des exports contrôlés.
8. **Produire des indicateurs** dont la définition, la fraîcheur et le périmètre sont explicites.
9. **Signaler des cas atypiques** sans automatiser la décision.
10. **Assurer sécurité, auditabilité et reproductibilité** avant tout pilote.

## 6. Utilisateurs et besoins

| Profil | Besoin principal | Droits cibles |
|---|---|---|
| Lecteur | rechercher et consulter | lecture des dossiers autorisés |
| Analyste | filtrer, comparer, exporter, valider | lecture, correction et export |
| Gestionnaire documentaire | importer, classer, traiter les rejets | ingestion et métadonnées |
| Administrateur fonctionnel | gérer référentiels et règles | configuration métier |
| Administrateur technique | superviser jobs et infrastructure | exploitation, sans modifier les données métier |
| Auditeur | vérifier actions et provenance | lecture immuable des journaux |

La séparation des rôles est obligatoire : l'administrateur technique ne doit pas être implicitement propriétaire de toutes les décisions métier.

## 7. Périmètre

### Inclus dans le MVP

- import sécurisé de ZIP/PDF/DOCX ;
- connecteur configurable vers une source publique ;
- corpus local de replay ;
- extraction native et OCR ;
- extraction de champs prioritaires ;
- fiche dossier avec lien vers la preuve ;
- validation/correction humaine ;
- recherche textuelle et filtres ;
- tableau de bord de qualité et volumétrie ;
- authentification, rôles, audit et export ;
- monitoring des traitements.

### Hors périmètre du MVP

- remplacement du portail officiel ;
- décision automatique d'attribution ou de conformité ;
- archivage légal complet ;
- signature électronique ;
- classification ML présentée comme fiable sans dataset validé ;
- traitement exhaustif de toutes les variantes documentaires ;
- déploiement national sans pilote et homologation.

## 8. Architecture fonctionnelle cible

```text
Sources / Import
      ↓
Connecteurs et acquisition
      ↓
Validation, sécurité et stockage original
      ↓
Extraction native / OCR
      ↓
Structuration NLP + normalisation
      ↓
Contrôle humain et qualité
      ↓
Index de recherche + base métier
      ↓
API sécurisée
      ↓
Recherche · Fiche dossier · Comparaison · Dashboard · Administration
```

Chaque étape produit un état, des métriques, des erreurs explicites et une version. Une reprise ne doit ni perdre un dossier ni le dupliquer.

## 9. Modules clés redéfinis

### M1 — Gestion des sources et connecteurs

Enregistre les sources autorisées, leur URL, leur disponibilité, la version du connecteur et les règles de collecte. Le portail actuel est un connecteur parmi d'autres, non une dépendance codée au cœur du produit.

**Fonctions :** test de disponibilité, collecte par période, mode simulation, quota, journal des changements, replay hors ligne.

### M2 — Acquisition et sécurisation des fichiers

Reçoit les fichiers collectés ou importés, vérifie leur type réel, leur taille, leur intégrité et leur hash, puis conserve l'original de manière immuable.

**Fonctions :** anti-doublon, antivirus selon infrastructure, protection contre ZIP slip/bombes, quarantaine, provenance et manifeste.

### M3 — Orchestration des traitements

Pilote une machine d'états persistante et des workers séparés de l'API.

**États :** reçu, validé, extrait, OCR en cours, NLP en cours, indexé, à vérifier, terminé, rejeté.  
**Fonctions :** retry borné, reprise, annulation, priorité, dead-letter queue, durée et cause d'échec.

### M4 — Extraction documentaire

Sélectionne la meilleure stratégie selon le type de document : texte natif, OCR complet ou OCR de pages spécifiques.

**Fonctions :** PDF/DOCX, détection de langue, rotation, prétraitement, extraction page par page, coordonnées et cache.

### M5 — Qualité OCR

Mesure la qualité au niveau document/page et déclenche une revue lorsque les seuils ne sont pas atteints.

**Fonctions :** confiance technique, CER/WER sur corpus, pages faibles, rapport par langue, version du moteur.

### M6 — Extraction et normalisation métier

Extrait les champs prioritaires et les relie à leur preuve documentaire.

**Champs prioritaires :** numéro/référence, objet, organisme acheteur, type de procédure, dates, montant estimatif, caution, lieu/région, délai, qualification, agrément et contacts.

Chaque résultat comprend : valeur brute, valeur normalisée, page, extrait, méthode, version et statut de validation.

### M7 — Référentiels

Centralise régions, villes, organismes, types d'avis, catégories, qualifications, agréments, unités et devises.

**Fonctions :** version, date de validité, alias français/arabe, fusion contrôlée et historique.

### M8 — Revue humaine

Permet à l'analyste d'accepter, corriger ou rejeter une extraction en voyant le document et la zone source.

**Fonctions :** file de revue par risque, commentaire, double validation optionnelle, historique et jeu d'annotation réutilisable.

### M9 — Recherche et découverte

Fournit une recherche lexicale classée, des filtres structurés et éventuellement une recherche sémantique clairement identifiée comme expérimentale.

**Fonctions :** stemming, synonymes, recherche bilingue, facettes, snippets, surlignage, tri, requêtes sauvegardées et alertes.

### M10 — Fiche et comparaison des dossiers

Présente la donnée structurée, le fichier source, le texte extrait et l'historique dans une même vue.

**Fonctions :** comparaison côte à côte, différences, export, copie de lien, preuve par champ et téléchargement autorisé.

### M11 — Analytique et qualité

Sépare les indicateurs métier des indicateurs techniques.

**Métier :** volumes, montants, catégories, régions, organismes, délais.  
**Qualité :** complétude, OCR, corrections, échecs, fraîcheur et couverture du corpus.

### M12 — Signaux et aide à l'analyse

Combine d'abord règles métier explicables, puis modèles statistiques validés.

**Fonctions :** signaler montant/caution/délai atypique, expliquer les facteurs, enregistrer la décision de l'analyste, mesurer les faux positifs.

### M13 — Administration, sécurité et audit

Gère identités, rôles, permissions, secrets, sessions, référentiels et journaux.

**Fonctions :** RBAC, SSO cible, audit immuable, politique de conservation, chiffrement, export d'audit et séparation des responsabilités.

### M14 — Exploitation et observabilité

Expose l'état de santé utile sans révéler le schéma ou les secrets.

**Fonctions :** métriques, logs corrélés, alertes, sauvegarde/restauration, capacité, disponibilité source et SLO.

## 10. Fonctionnalités clés cibles

### Parcours « collecter »

1. L'utilisateur choisit une source et une période.
2. Le système vérifie la disponibilité et crée un job.
3. Chaque dossier est téléchargé avec sa provenance et son hash.
4. Les doublons sont reconnus sans supprimer l'historique de collecte.
5. Les erreurs sont isolées et rejouables.

### Parcours « importer »

1. L'utilisateur dépose un fichier autorisé.
2. Le système vérifie sécurité, intégrité et taille réelle.
3. Un statut persistant affiche chaque étape.
4. Le document original reste consultable selon les droits.

### Parcours « vérifier »

1. Le système priorise les champs incertains.
2. L'analyste voit la valeur et la zone source.
3. Il accepte, corrige ou rejette.
4. La correction est historisée et alimente le corpus annoté.

### Parcours « rechercher et comparer »

1. L'utilisateur saisit des mots ou applique des filtres.
2. Les résultats sont classés avec un extrait pertinent.
3. La fiche expose métadonnées, preuves, texte et historique.
4. Plusieurs dossiers peuvent être comparés et exportés.

### Parcours « superviser »

1. L'administrateur voit disponibilité, files, échecs et temps de traitement.
2. Il relance un job sans créer de doublon.
3. Il consulte les journaux corrélés sans voir les secrets.

## 11. Exigences non fonctionnelles

| Axe | Exigence MVP |
|---|---|
| Sécurité | aucune route métier anonyme ; secrets externes ; TLS ; RBAC testé |
| Traçabilité | source, hash, version et preuve pour chaque donnée critique |
| Fiabilité | reprise après redémarrage ; idempotence ; erreurs explicites |
| Performance | objectifs mesurés sur corpus de référence, pas d'allégation générale |
| Accessibilité | navigation clavier, contraste, libellés, tests automatiques et manuels |
| Bilinguisme | contenus FR/AR, Unicode correct, stratégie RTL et mesures séparées |
| Maintenabilité | modules courts, schémas typés, lint, CI, revue de code |
| Portabilité | configuration par environnement, conteneurs testés, aucun chemin absolu |
| Données | minimisation, conservation définie, sauvegarde et restauration testées |
| Explicabilité | aucune alerte sans motif et preuve consultable |

## 12. Données et modèle conceptuel minimal

Entités principales :

- **Source** et **version de connecteur** ;
- **Job de collecte/traitement** et **étape de job** ;
- **Dossier d'appel d'offres** ;
- **Document original**, version, hash et emplacement ;
- **Page/segment extrait** ;
- **Champ extrait**, preuve, méthode, score et validation ;
- **Référentiel** et version ;
- **Utilisateur, rôle et permission** ;
- **Correction**, commentaire et historique ;
- **Index/requête sauvegardée/alerte** ;
- **Signal analytique**, explication et décision humaine ;
- **Événement d'audit**.

## 13. Critères de succès

Le MVP est considéré réussi seulement si :

- un tiers peut l'installer et exécuter tests/build depuis un clone propre ;
- 100 dossiers de référence sont traités de façon reproductible ;
- aucun doublon n'est créé lors d'un replay ;
- 100 % des valeurs critiques affichent leur page et extrait source ;
- les mesures OCR/NLP sont publiées par langue et type de document ;
- toutes les routes métier sont couvertes par la matrice d'autorisation ;
- la recherche est évaluée sur des requêtes annotées ;
- une sauvegarde est restaurée avec succès ;
- les limites du ML sont visibles dans l'interface et la documentation.

## 14. Feuille de route recommandée

| Horizon | Résultat attendu |
|---|---|
| Semaine 1 | sécurité critique et discours remis à niveau |
| Semaines 2–3 | socle reproductible, CI, migrations et API typée |
| Semaines 4–5 | ingestion durable, replay et sécurité des fichiers |
| Semaines 6–8 | corpus annoté, qualité OCR/NLP et revue humaine |
| Semaines 9–10 | vraie recherche, comparaison et KPIs gouvernés |
| Semaines 11–12 | évaluation ML ou retrait assumé du ML |
| 3–6 mois | pilote DSI limité, sécurité et exploitation validées |

## 15. Message de soutenance proposé

> Les dossiers d'appels d'offres renferment des informations utiles mais difficiles à exploiter lorsqu'elles restent dispersées dans des documents hétérogènes. Notre prototype automatise leur acquisition, leur extraction et leur structuration, puis les rend recherchables dans une interface unique. Notre contribution principale est une chaîne traçable qui relie chaque donnée au document source. Les résultats actuels valident la faisabilité ; la mesure sur corpus annoté, la sécurité et l'industrialisation constituent les étapes nécessaires avant un pilote DSI.

## 16. Démonstration recommandée

1. Montrer un dossier original et expliquer la difficulté.
2. Importer un ZIP de référence en mode hors ligne.
3. Suivre les états du traitement.
4. Ouvrir la fiche et cliquer sur la preuve d'un montant/date.
5. Corriger une extraction incertaine.
6. Rechercher le dossier avec un filtre métier.
7. Comparer deux dossiers.
8. Montrer un tableau de bord de qualité, pas seulement des graphiques financiers.
9. Terminer par les métriques mesurées et les limites.

Cette démonstration raconte une valeur métier réelle et évite de dépendre du portail externe le jour de la soutenance.


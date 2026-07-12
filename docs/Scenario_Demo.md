# Scénario Démonstration Live - GED Intelligente

**Durée estimée** : 5 à 7 minutes.

## Étape 1 : Le Tableau de Bord (1 minute)
- **Action** : Ouvrir la page d'accueil de l'application React.
- **Discours** : "Bienvenue sur le tableau de bord de la GED Intelligente. Toutes ces statistiques sont générées en direct depuis notre base de données. On voit immédiatement le volume total, les top acheteurs, et un graphique de tendance mensuelle des Appels d'Offres."
- **Focus visuel** : Pointer le taux de réussite OCR qui prouve que l'extraction s'est bien déroulée.

## Étape 2 : Ingestion et Upload Asynchrone (2 minutes)
- **Action** : Se rendre sur la page "Upload" (Menu latéral).
- **Discours** : "Nous allons maintenant simuler la réception d'un nouveau Dossier de Consultation. Le système va l'ingérer."
- **Action** : Uploader un fichier zip factice valide (depuis `tests/fixtures/sample_ao.zip` si existant, ou un exemple généré).
- **Discours** : "Pendant que la barre de progression avance, notre backend Python FastAPI lance une tâche en arrière-plan. Il extrait le texte via OCR, puis analyse ce texte avec notre algorithme NLP pour renseigner automatiquement la base de données. Il fait également appel à un modèle de Machine Learning."

## Étape 3 : La Recherche FTS (1 minute)
- **Action** : Aller sur l'onglet "Explorateur".
- **Discours** : "Maintenant que notre document est ingéré, cherchons-le."
- **Action** : Taper un mot-clé précis dans la barre de recherche.
- **Focus visuel** : Montrer que le système ramène le bon résultat très rapidement grâce au moteur d'indexation Full-Text.

## Étape 4 : Détail et Intelligence Artificielle (1.5 minutes)
- **Action** : Cliquer sur l'Appel d'Offre issu de la recherche.
- **Discours** : "Nous voici sur la fiche détaillée. Dans ce premier onglet, vous voyez l'ensemble des données financières (montant estimatif, caution) que le NLP a trouvées de manière autonome dans le texte."
- **Action** : Aller sur l'onglet "Machine Learning".
- **Discours** : "Le système a labellisé cet appel d'offre avec un score de confiance très élevé. Un algorithme de détection d'anomalies veille également pour alerter l'utilisateur si les montants ou les délais sont inhabituels."
- **Action** : Naviguer vers l'onglet texte.
- **Discours** : "Et pour vérifier, l'utilisateur a toujours accès au texte brut complet extrait par l'OCR."

## Étape 5 : Conclusion (30 secondes)
- **Action** : Retour sur le dashboard.
- **Discours** : "Ce Proof of Concept démontre la viabilité technique d'un traitement massif des archives publiques."

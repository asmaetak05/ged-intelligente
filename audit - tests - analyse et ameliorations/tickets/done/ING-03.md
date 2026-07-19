# Réalisation ING-03

**Ticket** : Reprise sur erreur (Checkpoint + Offset)
**Statut** : Terminé

**Détails de l'implémentation** :
- Ajout d'un système de checkpointing local via `scraper_checkpoint.json`.
- Pendant la phase A (navigation), la `page_courante` et la liste des `discovered_numbers` sont sauvegardées à chaque itération.
- Lors du redémarrage, si la date de début et de fin correspondent, le script simule les clics pour restaurer l'état ASP.NET jusqu'à la `page_courante` et reprend la découverte là où elle s'était arrêtée.
- Enregistrement des numéros traités dans `processed_numbers` pour sauter ce qui a déjà été téléchargé.

-- Script de configuration des Triggers PostgreSQL pour le Full Text Search (FTS)

-- 1. Création de la fonction qui met à jour la colonne 'tsv_search'
CREATE OR REPLACE FUNCTION update_marches_tsv_search() RETURNS trigger AS $$
BEGIN
  -- On concatène les champs pertinents pour la recherche plein texte :
  -- Titre du projet, organisme acheteur, et la ville.
  -- coalesce permet d'éviter que toute la chaîne devienne NULL si un champ est NULL
  NEW.tsv_search := to_tsvector('french', 
    coalesce(NEW.titre_projet, '') || ' ' || 
    coalesce(NEW.organisme_acheteur, '') || ' ' ||
    coalesce(NEW.ville_execution, '')
  );
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- 2. Création du Trigger qui s'active avant chaque INSERT ou UPDATE
DROP TRIGGER IF EXISTS trg_marches_tsv_update ON marches;

CREATE TRIGGER trg_marches_tsv_update
BEFORE INSERT OR UPDATE ON marches
FOR EACH ROW
EXECUTE FUNCTION update_marches_tsv_search();

-- (Optionnel) Si vous avez déjà inséré des données avant d'appliquer ce script,
-- exécutez cette commande pour forcer la mise à jour des vecteurs existants :
-- UPDATE marches SET id = id;

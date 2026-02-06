# tex2qmd — LaTeX → Quarto

Package Python pour générer les livres Quarto à partir de sources LaTeX.

## Usage (générique)

Depuis la racine du dépôt (`ipp/`) :

1. **Optionnel** : définir les sources LaTeX  
   `export TEX2QMD_SOURCE_DIR=/chemin/vers/Chapitres`

2. Générer les `.qmd` :

   ```bash
   PYTHONPATH=quarto uv run python -m tex2qmd.<nom_du_livre>
   ```

3. Rendre le livre :

   ```bash
   cd quarto/<livre> && quarto render
   ```

Les sorties sont dans `quarto/<livre>/public/` (HTML et PDF).

Voir `README.md` à la racine pour le guide complet et un exemple.

## Installation

À la racine du dépôt : `uv pip install -e .[quarto]`

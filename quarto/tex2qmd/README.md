# tex2qmd — LaTeX → Quarto

Package Python pour générer les livres Quarto à partir de sources LaTeX.

## Usage fiscalité

Depuis la racine du dépôt (`ipp/`) :

1. **Optionnel** : définir les sources LaTeX (sinon défaut : `ipp/source/Fiscalité/Chapitres`)  
   `export TEX2QMD_SOURCE_DIR=/chemin/vers/Chapitres`

2. Générer les `.qmd` et `legislation.bib` :  
   `tex2qmd-fiscalite`

3. Rendre le livre (HTML + PDF) :  
   `cd quarto/fiscalite && quarto render`

Les sorties sont dans `quarto/fiscalite/public/` (HTML et PDF).

## Installation

À la racine du dépôt : `pip install -e .`

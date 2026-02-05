# Précis IPP – Fiscalité des ménages (Quarto)

Livre Quarto généré à partir des sources LaTeX du guide **Le système fiscal français** (répertoire configurable via `TEX2QMD_SOURCE_DIR`, par défaut `ipp/source/Fiscalité/Chapitres/`).

## Workflow

1. **Mettre à jour les .qmd depuis le LaTeX** (après modification des `.tex`) :
   ```bash
   cd ipp
   tex2qmd-fiscalite
   ```
   Ou sans installer le package : `PYTHONPATH=quarto python3 -m tex2qmd.fiscalite`

2. **Construire le livre** (HTML + PDF si TeX installé) :
   ```bash
   cd ipp/quarto/fiscalite
   # Utiliser le venv du projet pour les blocs Python (tableaux OpenFisca)
   export QUARTO_PYTHON="$PWD/../../.venv/bin/python"   # depuis ipp/, export QUARTO_PYTHON=".venv/bin/python"
   quarto render
   ```
   - **HTML** : généré dans `public/` (fonctionne sans TeX).
   - **PDF** : nécessite une distribution TeX (TeX Live ou MiKTeX). En cas d’erreur avec `xelatex`, changer le moteur en `pdflatex` dans `_quarto.yml` (section `format.pdf.pdf-engine`).

3. **Prévisualiser le livre HTML** (liens corrects) : lancer le serveur depuis `public/` :
   ```bash
   cd ipp/quarto/fiscalite
   ./serve.sh
   ```
   Puis ouvrir **http://localhost:8765/** dans le navigateur.

## Structure
- **Source LaTeX** : `TEX2QMD_SOURCE_DIR` ou `ipp/source/Fiscalité/Chapitres/*.tex`
- **Chapitres convertis** : `presentation.qmd`, `cotisations.qmd`, `revenu.qmd`, `patrimoine.qmd`, `indirecte.qmd`, `glossaire.qmd`
- **Introduction** : `index.qmd` (texte fixe, non régénéré depuis le LaTeX)
- **Documentation** : `docs/citations.md` (citations et double bibliographie)
- **Pages de couverture PDF** : en début de document, `couverture1.pdf` et `couverture2.pdf` ; en fin de document, `couverture4.pdf` (et `couverture3.pdf` si présent dans `source/Fiscalité/Couverture/`). Voir `cover-pages.tex` et `cover-back.tex`.

Les sections vides dans la source reçoivent automatiquement un indicateur *[À rédiger.]* à la conversion. Pour en ajouter d’autres, modifier les `.tex` avant de relancer `tex2qmd-fiscalite`.

## Tableaux : TVA (OpenFisca ou statique) / autres (toujours conversion LaTeX)

- **Tableau TVA uniquement** (« Évolution des taux de TVA » dans `indirecte.qmd`) : le paramètre `params.use_openfisca_tables` dans `_quarto.yml` (ou le front matter du chapitre) choisit la source :
  - `true` (défaut) : tableau généré depuis [OpenFisca-France](https://github.com/openfisca/openfisca-france).
  - `false` : tableau statique (fichier `tables/tva_historique_static.md`, issu du .tex).
- **Tous les autres tableaux** du livre (aperçu fiscalité, carburants, tabac, alcools, assurances, etc.) utilisent **toujours** la conversion LaTeX (contenu des .qmd) ; OpenFisca ne s’applique pas à eux.
- **Pour le mode OpenFisca (TVA)** : installer les dépendances, définir `QUARTO_PYTHON` sur le venv, puis `quarto render` (voir étape 2 ci‑dessus).
- Pour un rendu hors ligne ou des paramètres personnalisés, voir `parameters/README.md`.

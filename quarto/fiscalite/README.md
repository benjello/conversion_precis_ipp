# Précis IPP – Fiscalité des ménages (Quarto)

Livre Quarto généré à partir des sources LaTeX du guide **Le système fiscal français** (répertoire configurable via `TEX2QMD_SOURCE_DIR`, par défaut `ipp/source/Fiscalité/Chapitres/`).

## Workflow (fiscalité)

1. **Mettre à jour les .qmd depuis le LaTeX** (après modification des `.tex`) :

   ```bash
   cd ipp
   tex2qmd-fiscalite
   ```

   Ou sans installer le package : `PYTHONPATH=quarto uv run python -m tex2qmd.fiscalite`

2. **Construire le livre** (HTML + PDF si TeX installé) :

   ```bash
   cd ipp/quarto/fiscalite
   # Utiliser l'environnement Python géré par uv pour les blocs Python (tableaux OpenFisca)
   export QUARTO_PYTHON="$(uv python find)"
   quarto render
   ```

   - **HTML** : généré dans `public/` (fonctionne sans TeX).
   - **PDF** : nécessite une distribution TeX (TeX Live ou MiKTeX). En cas d’erreur avec `xelatex`, changer le moteur en `pdflatex` dans `_quarto.yml` (section `format.pdf.pdf-engine`).

3. **Prévisualiser le livre HTML** (liens corrects) : lancer le serveur depuis `public/` :

   ```bash
   cd ipp/quarto/fiscalite
   ./serve.sh
   ```

   Puis ouvrir **[http://localhost:8765/](http://localhost:8765/)** dans le navigateur.

## Vérifier rapidement le workflow

Pour détecter rapidement une casse après des changements structurels :

```bash
cd ipp/quarto/fiscalite
./check_workflow.sh
```

Ce script régénère les `.qmd` puis rend uniquement `chapters/indirecte/indirecte.qmd`
(qui exécute les tableaux OpenFisca), ce qui rend le test rapide.

Version générique (pour d'autres livres) :

```bash
cd ipp/quarto
./check_workflow.sh fiscalite chapters/indirecte/indirecte.qmd
```

Le script utilise `uv` pour exécuter Python (si disponible) et configure
`QUARTO_PYTHON` via `uv python find` par défaut.

## Structure (fiscalité)

- **Source LaTeX** : `TEX2QMD_SOURCE_DIR` ou `ipp/source/Fiscalité/Chapitres/*.tex`
- **Chapitres convertis** : `chapters/presentation/presentation.qmd`, `chapters/cotisations/cotisations.qmd`, `chapters/revenu/revenu.qmd`, `chapters/patrimoine/patrimoine.qmd`, `chapters/indirecte/indirecte.qmd`, `chapters/glossaire/glossaire.qmd`
- **Introduction** : `chapters/index/index.qmd` (texte fixe, non régénéré depuis le LaTeX)
- **Documentation** : `docs/citations.md` (citations et double bibliographie)
- **Pages de couverture PDF** : en début de document, `couverture1.pdf` et `couverture2.pdf` ; en fin de document, `couverture4.pdf` (et `couverture3.pdf` si présent dans `source/Fiscalité/Couverture/`). Voir `cover-pages.tex` et `cover-back.tex`.

Les sections vides dans la source reçoivent automatiquement un indicateur *[À rédiger.]* à la conversion. Pour en ajouter d’autres, modifier les `.tex` avant de relancer `tex2qmd-fiscalite`.

## Tableaux OpenFisca (chapitre "indirecte")

- **Tableaux OpenFisca** : TVA, tabac, alcools dans `chapters/indirecte/indirecte.qmd`. Le paramètre `params.use_openfisca_tables` dans `_quarto.yml` (ou le front matter du chapitre) choisit la source :
  - `true` (défaut) : tableaux générés depuis [OpenFisca-France](https://github.com/openfisca/openfisca-france).
  - `false` : tableaux statiques (fichiers `chapters/indirecte/tables/*_static.md`, issus du .tex).
- **Autres tableaux** du livre (aperçu fiscalité, carburants, assurances, etc.) utilisent **toujours** la conversion LaTeX (contenu des .qmd) ; OpenFisca ne s’applique pas à eux.
- **Organisation du code** : helpers génériques dans `../openfisca_tables/core.py` (shared across Quarto books), tableaux du chapitre indirecte dans `chapters/indirecte/openfisca_tables.py`.
- **Pour le mode OpenFisca** : installer les dépendances (openfisca-france, pyyaml, pandas), définir `QUARTO_PYTHON` sur le venv, puis `quarto render` (voir étape 2 ci‑dessus). Les paramètres sont lus depuis le paquet openfisca-france installé.

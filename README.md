# IPP — Précis socio-fiscal

## Régénérer le livre Quarto « Fiscalité des ménages »

Sources LaTeX → conversion → `.qmd` → HTML + PDF.

1. **Optionnel** : indiquer le répertoire des chapitres LaTeX (sinon : `source/Fiscalité/Chapitres`)  

   ```bash
   export TEX2QMD_SOURCE_DIR=/chemin/vers/Chapitres
   ```

2. Générer les `.qmd` et `legislation.bib` depuis la racine du dépôt (`ipp/`) :  

   ```bash
   uv pip install -e .   # une fois
   tex2qmd-fiscalite
   ```

   Ou sans installer :  

   ```bash
   PYTHONPATH=quarto uv run python -m tex2qmd.fiscalite
   ```

3. Rendre le livre (HTML + PDF dans `quarto/fiscalite/public/`) :  

   ```bash
   cd quarto/fiscalite && quarto render
   ```

## Créer un livre Quarto depuis des sources LaTeX (générique)

Objectif : `.tex` → `.qmd` → Quarto (HTML/PDF).

1. **Préparer les sources LaTeX**

   - Regrouper les chapitres `.tex` dans un répertoire unique.
   - Optionnel : définir `TEX2QMD_SOURCE_DIR=/chemin/vers/Chapitres`.

2. **Créer un générateur `tex2qmd` pour le livre**

   - Ajouter un module `quarto/tex2qmd/<nom_du_livre>.py`.
   - Définir la liste des chapitres, l’emplacement de sortie (`quarto/<livre>/chapters/`),
     et les transformations nécessaires (titres, tableaux, notes, etc.).
   - Si besoin, injecter des blocs Python (ex. tables OpenFisca) dans le chapitre.

3. **Initialiser le projet Quarto**

   - Créer `quarto/<livre>/_quarto.yml`.
   - Ajouter un `index.qmd` à la racine du livre.
   - La conversion génère les fichiers dans `quarto/<livre>/chapters/<chapitre>/<chapitre>.qmd`.

4. **Générer les `.qmd`**

   ```bash
   PYTHONPATH=quarto uv run python -m tex2qmd.<nom_du_livre>
   ```

5. **Rendre le livre**

   ```bash
   cd quarto/<livre>
   export QUARTO_PYTHON="$(uv python find)"
   quarto render
   ```

6. **Tester rapidement après changements**

   ```bash
   cd quarto
   ./check_workflow.sh <livre> <chapitre_qmd>
   ```

Voir :

- Guide détaillé : `quarto/tex2qmd/README.md`
- Exemple complet : `quarto/fiscalite/README.md`

### GitHub Pages

Pushes to `main` trigger a workflow that renders the Quarto book and deploys it to GitHub Pages. To enable the site:

1. In the repo: **Settings → Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.

The site will be available at `https://<owner>.github.io/<repo>/` (e.g. `https://benjello.github.io/conversion_precis_ipp/`).

- Détails conversion : `quarto/tex2qmd/README.md`
- Citations et bibliographie (fiscalité) : `quarto/fiscalite/docs/citations.md`

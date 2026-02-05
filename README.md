# IPP — Précis socio-fiscal

## Régénérer le livre Quarto « Fiscalité des ménages »

Sources LaTeX → conversion → `.qmd` → HTML + PDF.

1. **Optionnel** : indiquer le répertoire des chapitres LaTeX (sinon : `source/Fiscalité/Chapitres`)  
   ```bash
   export TEX2QMD_SOURCE_DIR=/chemin/vers/Chapitres
   ```

2. Générer les `.qmd` et `legislation.bib` depuis la racine du dépôt (`ipp/`) :  
   ```bash
   pip install -e .   # une fois, dans un venv si besoin
   tex2qmd-fiscalite
   ```  
   Ou sans installer :  
   ```bash
   PYTHONPATH=quarto python3 -m tex2qmd.fiscalite
   ```

3. Rendre le livre (HTML + PDF dans `quarto/fiscalite/public/`) :  
   ```bash
   cd quarto/fiscalite && quarto render
   ```

- Détails conversion : `quarto/tex2qmd/README.md`
- Citations et bibliographie (fiscalité) : `quarto/fiscalite/docs/citations.md`

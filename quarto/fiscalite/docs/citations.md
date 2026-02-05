# Citations et double bibliographie (fiscalité)

Le livre « fiscalité des ménages » souhaite deux listes distinctes :
- **Ouvrages** (références bibliographiques classiques)
- **Textes de lois** (références juridiques)

C'est un cas connu et délicat avec Pandoc/Quarto. Voici des options pragmatiques.

---

## 1. Une seule section « Bibliographie » (recommandé pour démarrer)

**Idée**  
Un seul bloc de références en fin d'ouvrage, avec :
- un fichier `.bib` pour les ouvrages (`references.bib`)
- un fichier `.bib` pour les textes de lois (`legislation.bib`)

Dans `_quarto.yml` :

```yaml
bibliography:
  - references.bib
  - legislation.bib
csl: juris-fr.csl   # optionnel : style juridique pour les lois
```

**Avantages**  
- Fonctionne tel quel en HTML et PDF.  
- Aucun filtre, pas de biblatex obligatoire.  
- Les entrées de type `@book` / `@article` et `@legislation` (ou `@misc` avec type) sont formatées différemment si le CSL le prévoit (ex. `juris-fr.csl`).

**Inconvénient**  
- Pas de titres séparés « Ouvrages » et « Textes de lois » ; tout est dans une seule liste.

---

## 2. Deux sections en PDF avec biblatex

**Idée**  
En sortie PDF, utiliser biblatex et afficher deux bibliographies avec des titres différents.

- Dans `_quarto.yml` :
  - `cite-method: biblatex`
  - `suppress-bibliography: true` (pour ne pas générer la liste automatique)
- Dans la page des références (ex. `references.qmd`), insérer du LaTeX :

```latex
# Bibliographie {.unnumbered}

\printbibliography[type=book,title={Ouvrages}]
\printbibliography[type=article,title={Articles}]
\printbibliography[type=legislation,title={Textes de lois}]
```

Les clés dans les `.bib` doivent avoir le bon **type** (book, article, legislation selon le style biblatex utilisé).

**Avantages**  
- Vraies sections « Ouvrages » et « Textes de lois » en PDF.  
- Contrôle fin du style (jurabib, etc.) si besoin.

**Inconvénients**  
- Ne s'applique qu'au PDF ; en HTML on obtient en général une seule liste sauf filtre.  
- Dépendance à biblatex et éventuellement à des styles (juris, etc.).

---

## 3. Deux sections en HTML avec un filtre Lua

**Idée**  
Un filtre Pandoc Lua qui, après la génération des références, duplique le bloc `#refs` en deux blocs : un pour les ouvrages, un pour les textes de lois, en ne gardant dans chaque bloc que les entrées du type voulu.  
C'est faisable mais demande de maintenir un script et de gérer les types (book, article vs legislation) de façon cohérente avec le CSL / les `.bib`.

À envisager seulement si vous avez vraiment besoin de deux sections en HTML.

---

## Recommandation

1. **Court terme**  
   Mettre en place l'**option 1** :  
   - `references.bib` + `legislation.bib` dans le projet fiscalité  
   - Les deux déclarés dans `bibliography`  
   - Un seul chapitre « Bibliographie » avec `::: {#refs} :::`  
   - Optionnel : réutiliser un CSL type `juris-fr.csl` (copie ou lien) pour formater correctement les lois.

2. **Si vous tenez aux deux sections**  
   - En **PDF** : passer à l'**option 2** (biblatex + `\printbibliography` par type).  
   - En **HTML** : soit accepter une seule liste, soit investir dans un filtre Lua (option 3).

3. **Cohérence des `.bib`**  
   - Dans `references.bib` : uniquement `@book`, `@article`, etc.  
   - Dans `legislation.bib` : `@legislation` (si le style le gère) ou `@misc` avec `type = {legislation}` et champs type `title`, `issued`, `number`, `url`, etc.  
   Vérifier que les clés citées dans le texte (`[@Ardant1971]`, `[@Piketty1999]`, etc.) existent bien dans `references.bib`.

---

## Fichiers concernés

- `_quarto.yml` : `bibliography`, éventuellement `csl`, et pour l'option 2 `cite-method` / `suppress-bibliography`
- `references.qmd` : chapitre « Bibliographie » et, pour l'option 2, le LaTeX ci‑dessus
- `references.bib` : ouvrages (Ardant1971, Piketty1999, etc.)
- `legislation.bib` : **généré par** le package `quarto/tex2qmd` (commande `tex2qmd-fiscalite`) à partir de `LEGISLATION_ENTRIES` dans `quarto/tex2qmd/legislation.py` — ne pas éditer à la main ; ajouter/modifier les lois dans ce module.
- Si besoin : réutiliser un CSL style juridique (ex. `fiscalite-references.csl` utilisé dans ce projet).

## Liaison automatique des textes de loi (package quarto/tex2qmd)

Le package `quarto/tex2qmd` (commande `tex2qmd-fiscalite`) :

1. **Repère** dans le texte des formulations de lois (ex. « loi du 15 juillet 1914 », « loi de finances pour 2013 »).
2. **Ajoute** une citation Pandoc après chaque occurrence : ` [@loi1914]`, etc.
3. **Génère** `legislation.bib` à partir de la liste `LEGISLATION_ENTRIES` dans `quarto/tex2qmd/legislation.py` (clé, motifs de recherche, titre, date, shorthand).

Pour ajouter une loi : éditer `LEGISLATION_ENTRIES` dans `quarto/tex2qmd/legislation.py` (nouvelle entrée avec `key`, `patterns`, `title`, `issued`, optionnel `shorthand`), puis relancer `tex2qmd-fiscalite`. Les motifs sont traités du plus long au plus court pour limiter les doublons.

**Liens Légifrance** : seules les URLs LODA vérifiées sont conservées (ex. TEPA 2007, LFI 2010). Pour ajouter un lien : aller sur [Légifrance](https://www.legifrance.gouv.fr/), rechercher le numéro de loi (ex. « 2011-900 », « loi finances 2013 »), ouvrir la fiche du texte consolidé, copier l'URL (format `https://www.legifrance.gouv.fr/loda/id/JORFTEXT0000...`), et l'ajouter dans `LEGISLATION_ENTRIES` avec la clé `url`.

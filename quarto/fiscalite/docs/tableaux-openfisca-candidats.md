# Tableaux candidats à la génération depuis les paramètres OpenFisca

La fonction générique `table_from_parameters(spec, ...)` permet de construire un tableau « paramètre × année » à partir d’une liste de paramètres OpenFisca ayant une structure **values** (une valeur par date). Voici les tableaux du livre qui peuvent être générés ainsi, ou qui demandent une adaptation.

---

## Déjà en place

| Tableau | Fichier | Spec / remarque |
|--------|---------|------------------|
| **Évolution des taux de TVA en France depuis 1972** | `chapters/indirecte/indirecte.qmd` | `TVA_PARAMETERS_SPEC` (taux_particulier_super_reduit, taux_reduit, taux_reduit_2, taux_normal, taux_majore). |

---

## Compatibles « tel quel » avec `table_from_parameters`

Même structure qu’un paramètre TVA : un YAML avec `values` (dates → valeur), éventuellement `metadata.unit`. On définit une liste `(chemin_paramètre, libellé_ligne)` et on appelle `table_from_parameters_df(spec, row_column_name=..., start_year=...)`.

### Fiscalité indirecte (`parameters/taxation_indirecte/`)

| Tableau dans le livre | Paramètres OpenFisca possibles | Fichier .qmd |
|------------------------|---------------------------------|--------------|
| **Fiscalité carburants (TICPE)** | `produits_energetiques/ticpe/` — taux ou montants par type de carburant (super, gazole, etc.) s’ils sont exposés comme un paramètre « valeur par date ». À vérifier : structure peut être par produit + date. | `chapters/indirecte/indirecte.qmd` |
| **Fiscalité tabacs** | `taxes_tabacs/` — droits ou taux par type de tabac (cigarettes, cigares, etc.) si un paramètre = une série temporelle. | `chapters/indirecte/indirecte.qmd` |
| **Fiscalité alcools** | `alcools_autres_boissons/` — droits ou taux par type de boisson. | `chapters/indirecte/indirecte.qmd` |
| **Taxes sur les assurances (TSCA, etc.)** | `taxes_assurances/` — taux par type de contrat (santé, vie, etc.) avec `values` par date. | `chapters/indirecte/indirecte.qmd` |
| **Évolution taxation contrats assurance santé depuis 1995** | Sous-ensemble de `taxes_assurances/` (paramètres avec historique long). | `chapters/indirecte/indirecte.qmd` |

### Prélèvements sociaux / cotisations (`parameters/prelevements_sociaux/`)

| Tableau dans le livre | Paramètres OpenFisca possibles | Fichier .qmd |
|------------------------|---------------------------------|--------------|
| **Historique des taux de CSG et de CRDS (revenus d’activité) depuis 1990** | `contributions_sociales/csg/activite/taux_global.yaml`, `contributions_sociales/csg/activite/imposable.yaml`, `contributions_sociales/csg/activite/abattement.yaml`, `contributions_sociales/crds.yaml`. | `chapters/revenu/revenu.qmd` (cotisations) |
| **Taux de CSG et de CRDS selon type de revenus de remplacement** | `contributions_sociales/csg/remplacement/` — sous-arbres par type (pensions, allocations chômage, etc.) avec `taux_plein`, `taux_reduit`, etc. | `chapters/revenu/revenu.qmd` |
| **Taux des contributions sociales sur revenus du patrimoine** | `contributions_sociales/` — paramètres « patrimoine » (taux par date). | `chapters/revenu/revenu.qmd` |
| **Taux des contributions sociales sur revenus de placement** | Idem, paramètres « placement ». | `chapters/revenu/revenu.qmd` |
| **Seuils d’exonération CSG-CRDS (2011, 2012)** | `contributions_sociales/csg/remplacement/seuils/` (seuil_rfr1, seuil_rfr2, seuil_ir, etc.). | `chapters/revenu/revenu.qmd` |

### Impôt sur le revenu (`parameters/impot_revenu/`)

| Tableau dans le livre | Paramètres OpenFisca possibles | Fichier .qmd |
|------------------------|---------------------------------|--------------|
| **Historique des plafonds d’avantage fiscal lié au QF depuis 2000** | Sous `calcul_impot_revenu/` ou `bareme_ir_depuis_1945/` : tout paramètre « plafond » ou « seuil » exposé comme une série **values** (une valeur par année). À identifier précisément (ex. plafond déduction QF, demi-part supplémentaire, etc.). | `chapters/revenu/revenu.qmd` |

---

## Nécessitant une logique spécifique (pas seulement `table_from_parameters`)

Structure différente : plusieurs valeurs par date (ex. barème = plusieurs tranches) ou tableau « tranche × taux » pour une année donnée.

| Tableau dans le livre | Structure OpenFisca | Piste |
|------------------------|---------------------|------|
| **Barème de l’IRPP (tranches et taux) pour les revenus 2013** | `bareme_ir_depuis_1945/` : par année, plusieurs tranches (seuil_min, seuil_max, taux). | Nouvelle fonction du type `table_bareme_ir(annee)` → tableau « Tranche \| Seuil min \| Seuil max \| Taux ». |
| **Historique des barèmes de l’IRPP depuis 1945** | Même arbre : une ligne par année, colonnes = tranches ou évolution d’un taux de tranche dans le temps. | Soit `table_from_parameters` sur un sous-ensemble (ex. taux de la dernière tranche par année), soit fonction dédiée qui agrège `bareme_ir_depuis_1945/<annee>/tranches/`. |
| **Surtaxe / barème forfaitaire IR** | Paramètres forfaitaires par tranche. | Adapter selon structure (une valeur par date → `table_from_parameters`, sinon fonction dédiée). |
| **PPE, CHR, micro-entreprises** | Seuils, taux, conditions. | Idem : paramètres « une valeur par date » → `table_from_parameters` ; barèmes ou règles complexes → fonction dédiée. |

---

## Résumé par chapitre

- **chapters/indirecte/indirecte.qmd** : TVA (fait) ; TICPE, tabacs, alcools, assurances → candidats directs après vérification des chemins et structure `values`.
- **chapters/revenu/revenu.qmd** : CSG/CRDS (taux et seuils) → candidats directs ; barème IR et plafonds QF → partie en `table_from_parameters`, partie en fonction dédiée (barèmes).
- **chapters/cotisations/cotisations.qmd** : Taux de cotisations (sécurité sociale, retraite, etc.) si exposés comme paramètres avec `values` par date.
- **chapters/patrimoine/patrimoine.qmd** : ISF/IFI, droits de donation/succession : selon structure (tranches vs une valeur par date).

---

## Comment ajouter un nouveau tableau

1. Dans le paquet, repérer le(s) fichier(s) YAML sous `openfisca_france/parameters/` avec une clé **values** (dates → valeur).
2. Construire une spec : liste de `(chemin_relatif, libellé_ligne)` (ex. `("parameters/prelevements_sociaux/contributions_sociales/csg/activite/taux_global.yaml", "CSG activité (taux global)")`).
3. Dans le .qmd, appeler par exemple :
   ```python
   from openfisca_tables import table_from_parameters_df
   spec = [...]
   table_from_parameters_df(spec, row_column_name="Paramètre", start_year=1990).style.hide(axis="index")
   ```
4. Optionnel : ajouter une constante (ex. `CSG_CRDS_SPEC`) et une fonction dédiée (ex. `table_csg_crds_activite_df()`) dans `openfisca_tables.py` pour réutilisation et légende commune.

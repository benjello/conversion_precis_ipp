# Paramètres OpenFisca (optionnel)

Pour générer les tableaux dynamiques (ex. évolution des taux de TVA) à partir des paramètres OpenFisca-France, vous pouvez :

1. **Ne rien faire** : le script `openfisca_tables.py` récupère les YAML nécessaires depuis GitHub au moment du rendu (nécessite PyYAML et pandas : `pip install pyyaml pandas`).

2. **Cloner les paramètres en local** (pour rendu hors ligne ou personnalisation) :
   ```bash
   git clone --depth 1 https://github.com/openfisca/openfisca-france.git /tmp/of-fr
   cp -r /tmp/of-fr/openfisca_france/parameters/taxation_indirecte ./parameters/
   export OPENFISCA_PARAMETERS_DIR="$(pwd)/parameters"
   ```

3. **Utiliser le package openfisca-france** : `pip install openfisca-france` ; les paramètres seront chargés depuis le package.

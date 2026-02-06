# Contributing to the IPP Fiscalité Guide

Thank you for your interest in contributing to the IPP Fiscalité Guide! This document explains how to suggest improvements and make edits.

## Ways to Contribute

### 1. Suggest Changes via GitHub Issues

If you notice an error, have a suggestion, or want to discuss an improvement:

1. Go to the [Issues tab](https://github.com/benjello/conversion_precis_ipp/issues)
2. Click "New Issue"
3. Describe your suggestion or report the error
4. We'll review and discuss with you

### 2. Edit Online (Easiest)

Each page in the rendered book has an "Edit" button in the top-right corner:

1. Click the **Edit** button on any page
2. You'll be taken to GitHub's web editor for that file (`.qmd`)
3. Make your changes
4. Click "Commit changes"
5. Follow GitHub's prompt to create a pull request
6. A maintainer will review and merge your changes

### 3. Fork & Clone (For Local Development)

If you want to make substantial changes or test them locally:

```bash
# Fork the repository on GitHub (click "Fork" button)
# Clone your fork
git clone https://github.com/YOUR-USERNAME/conversion_precis_ipp.git
cd conversion_precis_ipp

# Create a new branch for your changes
git checkout -b my-improvements

# Install dependencies
uv sync
# or: uv pip install -r quarto/fiscalite/requirements-quarto.txt

# Edit the .qmd files (see file structure below)
# Test locally:
cd quarto/fiscalite
quarto render

# Commit and push your changes
git add .
git commit -m "Description of your changes"
git push origin my-improvements

# Create a Pull Request on GitHub
```

## File Structure

The book chapters are in `quarto/fiscalite/`:

- `index.qmd` - Introduction/Home page
- `presentation.qmd` - Overview of the fiscal system
- `cotisations.qmd` - Social contributions
- `revenu.qmd` - Income tax
- `patrimoine.qmd` - Wealth/property tax
- `indirecte.qmd` - Indirect taxes (VAT, etc.)
- `glossaire.qmd` - Glossary
- `references.qmd` - Bibliography

## Editing Quarto Files (.qmd)

The book is written in Quarto Markdown format. Basic syntax:

````markdown
# Heading 1
## Heading 2

This is **bold** and this is *italic*.

- Bullet point
- Another point

1. Numbered item
2. Another item

[Link text](https://example.com)

![Image alt text](path/to/image.png)

```r
# R code block (optional)
```

```python
# Python code block (optional)
```

You can also use LaTeX math:

- Inline: $E = mc^2$
- Display: $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
````

## Pull Request Guidelines

When submitting a pull request:

1. **Clear description**: Explain what you changed and why
2. **One feature per PR**: Keep changes focused
3. **Test locally**: Run `quarto render` in `quarto/fiscalite/` to verify your changes work
4. **Reference issues**: If fixing an issue, mention it (e.g., "Fixes #123")

## Questions?

- Open an [Issue](https://github.com/benjello/conversion_precis_ipp/issues)
- Check existing issues to see if your question has been answered
- See the README.md for more project information

Thank you for helping improve this resource! 🙏

---

## Contribuer au Guide Fiscalité de l'IPP

Merci de votre intérêt pour contribuer au Guide Fiscalité de l'IPP ! Ce document explique comment suggérer des améliorations et effectuer des modifications.

## Façons de contribuer

### 1. Suggérer des changements via les issues GitHub

Si vous remarquez une erreur, avez une suggestion ou voulez discuter d'une amélioration :

1. Allez à l'onglet [Issues](https://github.com/benjello/conversion_precis_ipp/issues)
2. Cliquez sur "New Issue"
3. Décrivez votre suggestion ou signalez l'erreur
4. Nous examinerons et discuterons avec vous

### 2. Éditer en ligne (Le plus facile)

Chaque page du livre rendu a un bouton "Edit" en haut à droite :

1. Cliquez sur le bouton **Edit** sur n'importe quelle page
2. Vous serez redirigé vers l'éditeur web de GitHub pour ce fichier (`.qmd`)
3. Effectuez vos modifications
4. Cliquez sur "Commit changes"
5. Suivez les instructions de GitHub pour créer une pull request
6. Un mainteneur examinera et fusionnera vos modifications

### 3. Fork & Clone (Pour le développement local)

Si vous voulez effectuer des changements substantiels ou les tester localement :

```bash
# Forkez le dépôt sur GitHub (cliquez sur le bouton "Fork")
# Clonez votre fork
git clone https://github.com/VOTRE-NOMUTILISATEUR/conversion_precis_ipp.git
cd conversion_precis_ipp

# Créez une nouvelle branche pour vos changements
git checkout -b mes-ameliorations

# Installez les dépendances
uv sync
# ou : uv pip install -r quarto/fiscalite/requirements-quarto.txt

# Éditez les fichiers .qmd (voir la structure des fichiers ci-dessous)
# Testez localement :
cd quarto/fiscalite
quarto render

# Committez et poussez vos changements
git add .
git commit -m "Description de vos changements"
git push origin mes-ameliorations

# Créez une Pull Request sur GitHub
```

## Structure des fichiers

Les chapitres du livre sont dans `quarto/fiscalite/` :

- `index.qmd` - Page d'introduction/accueil
- `presentation.qmd` - Vue d'ensemble du système fiscal
- `cotisations.qmd` - Cotisations sociales
- `revenu.qmd` - Impôt sur le revenu
- `patrimoine.qmd` - Impôt sur la richesse/propriété
- `indirecte.qmd` - Taxes indirectes (TVA, etc.)
- `glossaire.qmd` - Glossaire
- `references.qmd` - Bibliographie

## Édition des fichiers Quarto (.qmd)

Le livre est écrit au format Quarto Markdown. Syntaxe de base :

````markdown
# En-tête 1
## En-tête 2

Ceci est **gras** et ceci est *italique*.

- Point de liste
- Un autre point

1. Élément numéroté
2. Un autre élément

[Texte du lien](https://example.com)

![Texte alt de l'image](chemin/vers/image.png)

```r
# Bloc de code R (optionnel)
```

```python
# Bloc de code Python (optionnel)
```

Vous pouvez aussi utiliser les mathématiques LaTeX :

- En ligne : $E = mc^2$
- Affichage : $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
````

## Directives pour les Pull Requests

Lors de la soumission d'une pull request :

1. **Description claire** : Expliquez ce que vous avez changé et pourquoi
2. **Une fonctionnalité par PR** : Gardez les changements ciblés
3. **Testez localement** : Exécutez `quarto render` dans `quarto/fiscalite/` pour vérifier que vos changements fonctionnent
4. **Référencez les issues** : Si vous corrigez une issue, mentionnez-la (ex. "Fixes #123")

## Des questions ?

- Ouvrez une [Issue](https://github.com/benjello/conversion_precis_ipp/issues)
- Vérifiez les issues existantes pour voir si votre question a été répondue
- Consultez le README.md pour plus d'informations sur le projet

Merci d'aider à améliorer cette ressource ! 🙏

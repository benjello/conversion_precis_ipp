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
# or: pip install -r quarto/fiscalite/requirements-quarto.txt

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

```markdown
# Heading 1
## Heading 2

This is **bold** and this is *italic*.

- Bullet point
- Another point

1. Numbered item
2. Another item

[Link text](https://example.com)

![Image alt text](path/to/image.png)

```{r}
# R code block (optional)
```

```{python}
# Python code block (optional)
```

You can also use LaTeX math:
- Inline: $E = mc^2$
- Display: $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
```

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

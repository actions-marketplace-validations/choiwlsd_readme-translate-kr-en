<!-- readme-translate-kr-en:start -->
<p align="right">
  <sub>
    🌐 Language&nbsp;&nbsp;
    <a href="./README.md">English</a>
    &nbsp;|&nbsp;
    <a href="./README.ko.md">한국어</a>
  </sub>
</p>
<!-- readme-translate-kr-en:end -->

# readme-translate-kr-en

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-readme--translate--kr--en-blue?logo=github)](https://github.com/marketplace/actions/readme-translate-kr-en)
[![GitHub release](https://img.shields.io/github/v/release/choiwlsd/readme-translate-kr-en)](https://github.com/choiwlsd/readme-translate-kr-en/releases/latest)
[![CI](https://github.com/choiwlsd/readme-translate-kr-en/actions/workflows/ci.yml/badge.svg)](https://github.com/choiwlsd/readme-translate-kr-en/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

A free, local-first GitHub Action for translating and synchronizing English and Korean README files.

**No npm package or paid translation API is required.** Translation runs on the GitHub Actions runner with open-source machine translation models.

## Quick start

Create `.github/workflows/translate-readme.yml` in the repository that contains the README you want to translate:

```yaml
name: Sync bilingual README

on:
  push:
    branches: [main]
    paths:
      - README.md
  workflow_dispatch:

permissions:
  contents: write

jobs:
  translate:
    if: github.actor != 'github-actions[bot]'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Translate README
        uses: choiwlsd/readme-translate-kr-en@v0.2.0
        with:
          source-file: README.md

      - name: Commit translated README
        run: |
          if [ -z "$(git status --porcelain -- README.md README.en.md README.ko.md)" ]; then exit 0; fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add README.md README.*.md
          git commit -m "docs: sync bilingual README"
          git push
```

### Create the first translation

Adding the workflow file does not immediately run it when `README.md` has not changed. After committing and pushing the workflow file to the default branch:

1. Open the repository's **Actions** tab on GitHub.
2. Select **Sync bilingual README**.
3. Select **Run workflow**, choose the default branch, and run it.
4. Wait for the workflow to finish. It detects the dominant language in `README.md`, then creates and commits `README.ko.md` for English source content or `README.en.md` for Korean source content.

The workflow must exist on the default branch before the **Run workflow** button is available. If the commit step is denied, open **Settings → Actions → General → Workflow permissions** and make sure GitHub Actions is allowed to write repository contents. Organization policy or branch protection can still prevent direct pushes.

After the first translation, every later push that changes `README.md` runs the workflow automatically. You can also use **Run workflow** again whenever you want to regenerate the translation without editing the source README.

Do not set `from` when you want content-based language detection. Setting `from: en` or `from: ko` intentionally overrides detection and forces that source language. Markdown code blocks, URLs, HTML, and other non-language content are excluded as much as possible before Korean and English characters are counted.

The first run downloads the translation model. Later runs reuse the Hugging Face model cache managed by the Action.

> Repositories with branch protection may reject direct pushes from `GITHUB_TOKEN`. Allow GitHub Actions to push to the target branch or adapt the final step to open a pull request.

## Features

- English → Korean and Korean → English translation
- Runs locally on the GitHub Actions runner
- No API key or paid AI service
- Automatic translated README filename selection
- Custom source and target paths
- Automatic translation direction detection from the latest commit
- Preserves fenced code, inline code, inline and reference links, images, badges, HTML, emphasis, YAML front matter, and emoji
- Adds English / 한국어 navigation to generated README files
- Caches downloaded Hugging Face models between runs

## Usage

### English to Korean

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

The default target is `README.ko.md`.

### Korean to English

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.ko.md
```

The default target is `README.md`.

### Custom filenames

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

### Automatic source detection

Omit `from` and `source-file` to detect a single changed standard README from the latest commit:

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
```

Use `fetch-depth: 2` when relying on automatic detection:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

If more than one standard README changed in the latest commit, specify `from` and `source-file` explicitly.

## Inputs

| Input            | Required | Default                    | Description                                   |
| ---------------- | -------- | -------------------------- | --------------------------------------------- |
| `from`           | No       | Auto-detect                | Source language: `en` or `ko`                 |
| `source-file`    | No       | Auto-detect or `README.md` | Source README path                            |
| `target-file`    | No       | Generated automatically    | Translated README path                        |
| `python-version` | No       | `3.11`                     | Python version used by the translation engine |

## How it works

The Action installs the Python translation dependencies, restores the cached Hugging Face model, protects Markdown elements, translates human-readable text, and writes the translated README back to the checked-out repository.

The Action modifies files only. Committing and pushing the result remains under the caller workflow's control.

Dedicated NLLB-based models are used for each direction:

| Direction        | Model                        |
| ---------------- | ---------------------------- |
| English → Korean | `NHNDQ/nllb-finetuned-en2ko` |
| Korean → English | `NHNDQ/nllb-finetuned-ko2en` |

README content is processed on the runner and is not sent to OpenAI, Anthropic, Gemini, DeepL, or another paid translation API.

> Translation models are distributed separately and have their own licenses and usage terms. Review the corresponding Hugging Face model card before redistribution or commercial use.

## Local development

The repository also contains a development CLI, but it is not currently published to npm.

Requirements:

- Node.js 20+
- Python 3.10+

```bash
python -m venv .venv
python -m pip install -r requirements.txt
node ./src/cli.js sync --from en --source README.md
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Run the test suite with:

```bash
npm test
```

The unit tests do not download or load the translation models.

## Release

The current Marketplace release is [`v0.2.0`](https://github.com/choiwlsd/readme-translate-kr-en/releases/tag/v0.2.0). Pinning the full release tag gives reproducible behavior:

```yaml
uses: choiwlsd/readme-translate-kr-en@v0.2.0
```

## License

This project is licensed under the [MIT License](./LICENSE).

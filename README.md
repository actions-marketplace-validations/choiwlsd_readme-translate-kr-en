<!-- readme-translate-kr-en:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-translate-kr-en:end -->

# readme-translate-kr-en

Free, local-first English ↔ Korean README translation and synchronization for GitHub.

**No API key. No paid AI API.**

`readme-translate-kr-en` translates README content locally using open-source machine translation models. Translation runs entirely on the machine running the CLI or GitHub Actions runner.

## What it does

- Synchronizes `README.md` and `README.ko.md`
- Supports English → Korean and Korean → English translation
- Uses a dedicated translation model for each direction
- Adds GitHub-friendly English / 한국어 navigation
- Preserves fenced code blocks, inline code, URLs, links, badges, and HTML as much as possible
- Runs locally without a translation API
- Works as both a CLI and a reusable GitHub Action
- Automatically detects which README changed when `--from` is omitted

## Translation models

`readme-translate-kr-en` uses dedicated NLLB-based models for each translation direction:

| Direction        | Model                        |
| ---------------- | ---------------------------- |
| English → Korean | `NHNDQ/nllb-finetuned-en2ko` |
| Korean → English | `NHNDQ/nllb-finetuned-ko2en` |

NLLB language codes:

| Language | Code       |
| -------- | ---------- |
| English  | `eng_Latn` |
| Korean   | `kor_Hang` |

Only the model required for the requested translation direction is loaded.

For example:

```bash
readme-translate-kr-en sync --from en
```

uses the English → Korean model, while:

```bash
readme-translate-kr-en sync --from ko
```

uses the Korean → English model.

Models are downloaded from Hugging Face on first use and cached locally for subsequent runs.

README content is processed on the machine running `readme-translate-kr-en` and is not sent to a paid translation or LLM API.

> Translation models are distributed separately and have their own licenses and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial use.

## Local development

### Requirements

- Node.js 20+
- Python 3.10+

Clone the repository and create a Python virtual environment before installing the translation dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Initialize the bilingual README files:

```powershell
node ./src/cli.js init
```

Translate English → Korean:

```powershell
node ./src/cli.js sync --from en
```

Translate Korean → English:

```powershell
node ./src/cli.js sync --from ko
```

Automatically detect the translation direction:

```powershell
node ./src/cli.js sync
```

When `--from` is omitted, the CLI checks the latest Git commit and attempts to determine whether `README.md` or `README.ko.md` was changed.

## npm usage

After the package is published to npm, it can be used without installing it globally.

Initialize bilingual README files:

```bash
npx readme-translate-kr-en init
```

Translate English → Korean:

```bash
npx readme-translate-kr-en sync --from en
```

Translate Korean → English:

```bash
npx readme-translate-kr-en sync --from ko
```

Automatically detect the translation direction:

```bash
npx readme-translate-kr-en sync
```

The `init` command creates or updates the language navigation at the top of the README files.

After initialization, both README files contain navigation like this:

```text
English · 한국어
```

`English` links to `README.md`, and `한국어` links to `README.ko.md`.

## How it works

English → Korean:

```text
README.md
   ↓
Markdown protection
   ↓
English → Korean model
   ↓
README.ko.md
```

Korean → English:

```text
README.ko.md
   ↓
Markdown protection
   ↓
Korean → English model
   ↓
README.md
```

Before translation, `readme-translate-kr-en` separates translatable text from Markdown elements that should remain unchanged.

It attempts to preserve:

- fenced code blocks
- inline code
- shell commands inside code blocks
- URLs
- Markdown links
- images
- badges
- HTML
- Markdown structure
- file paths and package names when protected by Markdown syntax

Only human-readable text is sent through the translation model where possible.

## GitHub Action

`readme-translate-kr-en` can also be used as a reusable GitHub Action.

No translation API key or API secret is required.

Create a workflow such as:

```text
.github/workflows/readme-translate.yml
```

and add:

```yaml
name: Sync bilingual README

on:
  push:
    branches: [main]
    paths:
      - README.md
      - README.ko.md

permissions:
  contents: write

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Translate README
        uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
        with:
          from: en

      - name: Commit translation
        run: |
          if git diff --quiet -- README.md README.ko.md; then exit 0; fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add README.md README.ko.md
          git commit -m "docs: sync bilingual README"
          git push
```

Replace `YOUR_GITHUB_NAME` with the GitHub username or organization that owns the `readme-translate-kr-en` repository.

### English → Korean

Use:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: en
```

This treats `README.md` as the source and updates `README.ko.md`.

### Korean → English

Use:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
```

This treats `README.ko.md` as the source and updates `README.md`.

### Automatic direction detection

You can also omit `from`:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
```

The CLI then checks the latest Git commit and attempts to determine which README changed.

For automatic detection, use:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

so the Action can compare the latest commit with its parent.

## Language navigation

`readme-translate-kr-en` maintains this navigation block at the top of both README files:

```html

```

The navigation block is removed before translation and added back afterward.

This prevents the language selector itself from being translated and avoids adding duplicate navigation blocks on repeated synchronization.

## Model caching

Translation models are downloaded only when needed.

For example:

```bash
readme-translate-kr-en sync --from en
```

loads the English → Korean model.

On first use, the model is downloaded from Hugging Face. Subsequent runs reuse the cached model when available.

The Korean → English model is downloaded separately when:

```bash
readme-translate-kr-en sync --from ko
```

is used for the first time.

The GitHub Action also caches the Hugging Face model directory between compatible workflow runs to reduce unnecessary model downloads.

Only the model required for the selected translation direction needs to be loaded.

## Cost model

`readme-translate-kr-en` does not call OpenAI, Anthropic, Gemini, DeepL, or another paid translation API.

**No translation API key is required, and `readme-translate-kr-en` itself creates no translation API bill.**

Translation runs on the local machine or CI runner instead.

GitHub-hosted Actions usage is governed separately by the repository owner's GitHub plan and usage limits.

Running `readme-translate-kr-en` locally or on a self-hosted runner avoids relying on GitHub-hosted compute.

## Tests

Run the test suite with:

```bash
npm test
```

The test suite does not download or load the translation models.

## Roadmap

Planned improvements include:

- Incremental README translation
- Translate only changed Markdown blocks
- Preserve manually edited translations where possible
- Improved Markdown parsing and protection
- Translation model benchmarking
- GitHub Profile README support
- Additional local translation engines

The long-term goal is to make bilingual README maintenance automatic while keeping translation local, predictable, and free from paid translation APIs.

## License

`readme-translate-kr-en` is licensed under the MIT License.

Translation models are downloaded separately and are not distributed as part of `readme-translate-kr-en`.

Each translation model has its own license and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial deployment.

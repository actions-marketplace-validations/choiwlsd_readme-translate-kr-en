<!-- readme-bilingual:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-bilingual:end -->

# readme-bilingual

Free, local-first English ↔ Korean README synchronization for GitHub.

**No API key. No paid AI API.**

`readme-bilingual` translates README content locally using open-source machine translation models. Translation runs entirely on the machine running the CLI or GitHub Actions runner.

## What it does

- Synchronizes `README.md` and `README.ko.md`
- Supports English → Korean and Korean → English translation
- Uses dedicated translation models for each direction
- Adds GitHub-friendly English / 한국어 navigation
- Preserves fenced code blocks, inline code, URLs, links, badges, and HTML as much as possible
- Runs locally without a translation API
- Works as both a CLI and a reusable GitHub Action
- Automatically detects which README changed when `--from` is omitted

## Translation models

`readme-bilingual` uses dedicated NLLB-based models for each translation direction:

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
readme-bilingual sync --from en
```

uses the English → Korean model, while:

```bash
readme-bilingual sync --from ko
```

uses the Korean → English model.

Models are downloaded from Hugging Face on first use and cached locally for subsequent runs.

README content is processed on the machine running `readme-bilingual` and is not sent to a paid translation or LLM API.

> Translation models are distributed separately and have their own licenses and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial use.

## Local CLI

### Requirements

- Node.js 20+
- Python 3.10+

Create and activate a Python virtual environment before installing the translation dependencies.

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

## Intended npm interface

After publishing to npm, the intended interface is:

```bash
npx readme-bilingual init

npx readme-bilingual sync --from en

npx readme-bilingual sync --from ko
```

When `--from` is omitted, `readme-bilingual` attempts to determine which README changed most recently.

```bash
npx readme-bilingual sync
```

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

Before translation, `readme-bilingual` separates translatable text from Markdown elements that should remain unchanged.

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

A repository can use `readme-bilingual` without configuring a translation API key or API secret.

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
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - uses: YOUR_GITHUB_NAME/readme-bilingual@v0.2.0
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

Use:

```yaml
with:
  from: en
```

for English → Korean translation.

Use:

```yaml
with:
  from: ko
```

for Korean → English translation.

If `from` is omitted, the CLI attempts to infer the source README from the latest commit.

## Model caching

Translation models are downloaded only when needed and cached by Hugging Face.

For example, running:

```bash
readme-bilingual sync --from en
```

downloads the English → Korean model on first use.

Subsequent runs reuse the cached model when available.

The Korean → English model is downloaded separately when that translation direction is used for the first time.

This keeps the runtime from loading both translation models when only one direction is needed.

## Cost model

`readme-bilingual` does not call OpenAI, Anthropic, Gemini, DeepL, or another paid translation API.

**No translation API key is required, and `readme-bilingual` itself creates no translation API bill.**

Translation runs on the local machine or CI runner instead.

GitHub-hosted Actions usage is governed separately by the repository owner's GitHub plan and usage limits.

Running `readme-bilingual` locally or on a self-hosted runner avoids relying on GitHub-hosted compute.

## Tests

Run the unit tests with:

```bash
npm test
```

The unit tests do not download or load the translation models.

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

`readme-bilingual` is licensed under the MIT License.

Translation models are downloaded separately and are not distributed as part of `readme-bilingual`.

Each translation model has its own license and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial deployment.

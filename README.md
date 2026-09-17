<!-- readme-bilingual:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-bilingual:end -->

# readme-bilingual

Free, local-first English ↔ Korean README synchronization for GitHub.

**No API key. No paid AI API.**

Translation runs locally using an open-source machine translation model on the machine running the CLI or GitHub Actions runner.

## What it does

- Synchronizes `README.md` and `README.ko.md`
- Adds GitHub-friendly English / 한국어 navigation
- Preserves fenced code blocks, inline code, URLs, links, badges, and HTML as much as possible
- Runs locally without a translation API
- Works as both a CLI and a reusable GitHub Action
- Automatically detects which README changed when `--from` is omitted

## Translation model

`readme-bilingual` currently uses:

| Model                              | Languages        |
| ---------------------------------- | ---------------- |
| `facebook/nllb-200-distilled-600M` | English ↔ Korean |

NLLB language codes:

| Language | Code       |
| -------- | ---------- |
| English  | `eng_Latn` |
| Korean   | `kor_Hang` |

A single NLLB model handles translation in both directions.

The model is downloaded from Hugging Face on first use and cached locally for subsequent runs.

README content is processed on the machine running `readme-bilingual` and is not sent to a paid translation or LLM API.

> The translation model has its own license and usage terms. Check the model card before redistribution or commercial use.

## Local CLI

Requirements:

- Node.js 20+
- Python 3.10+

Create and activate a Python virtual environment before installing the translation dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then initialize and synchronize the README files:

```powershell
node ./src/cli.js init
node ./src/cli.js sync --from en
```

Korean → English:

```powershell
node ./src/cli.js sync --from ko
```

### Intended npm interface

After publishing to npm, the intended interface is:

```bash
npx readme-bilingual init
npx readme-bilingual sync --from en
npx readme-bilingual sync --from ko
```

## How it works

English → Korean:

```text
README.md
   ↓
Markdown protection
   ↓
NLLB 600M
   ↓
README.ko.md
```

Korean → English:

```text
README.ko.md
   ↓
Markdown protection
   ↓
NLLB 600M
   ↓
README.md
```

Markdown elements such as fenced code blocks, inline code, URLs, links, badges, and HTML are protected from translation as much as possible.

## GitHub Action

A consuming repository can use the action without a translation API key or API secret:

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

Remove `from: en` if you want the CLI to infer the source README from the latest commit.

## Cost model

`readme-bilingual` does not call OpenAI, Anthropic, Gemini, DeepL, or another paid translation API.

**No translation API key is required, and the tool itself creates no translation API bill.**

The translation model runs on the local machine or runner instead.

GitHub-hosted Actions usage is governed separately by the repository owner's GitHub plan and usage limits. Running `readme-bilingual` locally or on a self-hosted runner avoids relying on GitHub-hosted compute.

## Tests

Run the unit tests with:

```bash
npm test
```

The unit tests do not download the translation model.

## License

`readme-bilingual` is licensed under the MIT License.

The translation model is distributed separately and has its own license and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial deployment.

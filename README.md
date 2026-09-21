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

Free, local-first English ↔ Korean README translation and synchronization for GitHub.

**No API key. No paid AI API.**

`readme-translate-kr-en` translates README content locally using open-source machine translation models. Translation runs entirely on the machine running the CLI or GitHub Actions runner.

## What it does

- Supports English → Korean and Korean → English translation
- Automatically creates or updates the translated README
- Supports custom source and target README filenames
- Automatically determines the target filename when `target-file` is omitted
- Uses a dedicated translation model for each direction
- Adds GitHub-friendly English / 한국어 navigation
- Preserves fenced code blocks, inline code, URLs, links, badges, and HTML as much as possible
- Runs locally without a translation API
- Works as both a CLI and a reusable GitHub Action
- Automatically detects which README changed when `--from` is omitted where possible

## README file naming

By default, `readme-translate-kr-en` can automatically determine the translated README filename from the source language.

For example:

```text
from: en
source-file: README.md
target-file: empty

→ README.ko.md
```

and:

```text
from: ko
source-file: README.md
target-file: empty

→ README.en.md
```

This means both of the following project structures are supported.

English as the main README:

```text
README.md
README.ko.md
```

Korean as the main README:

```text
README.md
README.en.md
```

Custom filenames can also be used by explicitly specifying both the source and target files.

For example:

```text
docs/README.md
docs/README.en.md
```

or:

```text
README_EN.md
README_KR.md
```

When `target-file` is omitted, the translated file is created in the same directory as the source file.

Examples:

```text
README.md
→ README.ko.md

docs/README.md
→ docs/README.ko.md

guide.md
→ guide.ko.md
```

for English → Korean translation.

For Korean → English translation:

```text
README.md
→ README.en.md

docs/README.md
→ docs/README.en.md

guide.md
→ guide.en.md
```

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

- `Node.js` 20+
- `Python` 3.10+

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

Translate an English `README.md` to `README.ko.md`:

```powershell
node ./src/cli.js sync --from en --source README.md
```

Translate a Korean `README.md` to `README.en.md`:

```powershell
node ./src/cli.js sync --from ko --source README.md
```

Specify the target filename manually:

```powershell
node ./src/cli.js sync --from ko --source README.md --target README.en.md
```

Automatically detect the translation direction:

```powershell
node ./src/cli.js sync
```

When `--from` is omitted, the CLI checks the latest Git commit and attempts to determine which configured README changed.

## npm usage

After the package is published to npm, it can be used without installing it globally.

Initialize bilingual README files:

```bash
npx readme-translate-kr-en init
```

Translate English → Korean:

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

If `--target` is omitted:

```text
README.md
→ README.ko.md
```

Translate Korean → English:

```bash
npx readme-translate-kr-en sync --from ko --source README.md
```

If `--target` is omitted:

```text
README.md
→ README.en.md
```

Specify a custom target file:

```bash
npx readme-translate-kr-en sync \
  --from ko \
  --source docs/README.md \
  --target docs/README.en.md
```

Automatically detect the translation direction:

```bash
npx readme-translate-kr-en sync
```

The `init` command creates or updates the language navigation at the top of the README files.

After initialization, README files contain navigation such as:

```text
English | 한국어
```

The links are generated from the configured English and Korean README paths.

## How it works

English → Korean:

```text
source file
   ↓
Markdown protection
   ↓
English → Korean model
   ↓
target file
```

Example:

```text
README.md
   ↓
README.ko.md
```

Korean → English:

```text
source file
   ↓
Markdown protection
   ↓
Korean → English model
   ↓
target file
```

Example:

```text
README.md
   ↓
README.en.md
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

The Action supports the following inputs:

| Input            | Description                                   | Default                  |
| ---------------- | --------------------------------------------- | ------------------------ |
| `from`           | Source language: `en` or `ko`                 | Auto-detect              |
| `source-file`    | README file used as the translation source    | Auto-detect or `README.md` |
| `target-file`    | Translated README path                        | Automatically determined |
| `python-version` | Python version used by the translation engine | `3.11`                   |

### English README as the main README

If your project uses:

```text
README.md
README.ko.md
```

use:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

Because `target-file` is omitted, the Action automatically uses:

```text
README.ko.md
```

### Korean README as the main README

If your project uses:

```text
README.md
README.en.md
```

use:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.md
```

Because `target-file` is omitted, the Action automatically uses:

```text
README.en.md
```

### Custom source and target files

You can explicitly define both files:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

This is useful when your repository uses a custom README naming convention.

### Example workflow

Create:

```text
.github/workflows/readme-translate.yml
```

For a project where English is the main README:

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
    if: github.actor != 'github-actions[bot]'
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
          source-file: README.md

      - name: Commit translation
        run: |
          if git diff --quiet -- README.md README.ko.md; then exit 0; fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add README.md README.ko.md
          git commit -m "docs: sync bilingual README"
          git push
```

For a project where Korean is the main README:

```yaml
name: Sync bilingual README

on:
  push:
    branches: [main]
    paths:
      - README.md
      - README.en.md

permissions:
  contents: write

jobs:
  sync:
    if: github.actor != 'github-actions[bot]'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Translate README
        uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
        with:
          from: ko
          source-file: README.md

      - name: Commit translation
        run: |
          if git diff --quiet -- README.md README.en.md; then exit 0; fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add README.md README.en.md
          git commit -m "docs: sync bilingual README"
          git push
```

Replace `YOUR_GITHUB_NAME` with the GitHub username or organization that owns the `readme-translate-kr-en` repository.

## Automatic direction detection

You can omit `from`:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
```

When both `from` and `source-file` are omitted, the CLI compares the latest commit with its parent. If exactly one standard README (`README.md`, `README.ko.md`, or `README.en.md`) changed, it uses that file as the source and detects its language from the content. The translated counterpart is then updated.

If Git history is unavailable, or no standard README changed, the CLI falls back to `README.md` and content-based language detection.

For automatic detection, use:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

so the Action can compare the latest commit with its parent.

When multiple standard README files are modified in the same commit, the CLI stops rather than guessing. Specify both `from` and `source-file` explicitly.

For example:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
```

## Language navigation

`readme-translate-kr-en` maintains a language navigation block at the top of bilingual README files.

For example:

```html

```

When custom filenames are used, the navigation links should reflect those filenames.

For example, if Korean is the main README:

```text
README.md
README.en.md
```

the navigation becomes:

```html
<p align="right">
  <sub>
    🌐 Language&nbsp;&nbsp;
    <a href="./README.en.md">English</a>
    &nbsp;|&nbsp;
    <a href="./README.md">한국어</a>
  </sub>
</p>
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
- More flexible bilingual file detection

The long-term goal is to make bilingual README maintenance automatic while keeping translation local, predictable, and free from paid translation APIs.

## License

`readme-translate-kr-en` is licensed under the MIT License.

Translation models are downloaded separately and are not distributed as part of `readme-translate-kr-en`.

Each translation model has its own license and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial deployment.

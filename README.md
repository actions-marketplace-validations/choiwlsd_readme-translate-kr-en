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

`readme-translate-kr-en` translates README files locally using open-source machine translation models. It can be used as a CLI or GitHub Action.

## Features

- English → Korean and Korean → English translation
- Automatic translated README filename detection
- Automatic translation direction detection
- Custom source and target filenames
- GitHub-friendly English / 한국어 navigation
- Preserves code blocks, inline code, URLs, links, badges, and HTML where possible
- Local translation without a paid API
- CLI and GitHub Action support

## Requirements

- Node.js 20+
- Python 3.10+

Translation models are downloaded from Hugging Face on first use and cached locally.

## CLI Usage

### 1. Install

After the package is published to npm, you can run it directly with `npx`:

```bash
npx readme-translate-kr-en <command>
```

For local development:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then run the CLI with:

```bash
node ./src/cli.js <command>
```

### 2. Initialize bilingual READMEs

```bash
npx readme-translate-kr-en init
```

For local development:

```bash
node ./src/cli.js init
```

`init` creates or updates the language navigation at the top of the README files.

```text
English | 한국어
```

### 3. Translate English → Korean

If `README.md` is written in English:

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

This creates or updates:

```text
README.ko.md
```

### 4. Translate Korean → English

If `README.md` is written in Korean:

```bash
npx readme-translate-kr-en sync --from ko --source README.md
```

This creates or updates:

```text
README.en.md
```

### 5. Use custom filenames

Specify both source and target files when necessary:

```bash
npx readme-translate-kr-en sync \
  --from ko \
  --source docs/README.md \
  --target docs/README.en.md
```

### 6. Automatic detection

You can also run:

```bash
npx readme-translate-kr-en sync
```

When `--from` is omitted, the CLI attempts to determine which README changed from the latest Git commit and detects the translation direction automatically.

If multiple README files changed in the same commit, specify the source explicitly instead of relying on automatic detection:

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

## CLI Options

| Option            | Description                                      |
| ----------------- | ------------------------------------------------ |
| `init`            | Initialize or update bilingual README navigation |
| `sync`            | Translate and synchronize a README               |
| `--from en`       | Translate English → Korean                       |
| `--from ko`       | Translate Korean → English                       |
| `--source <file>` | Source README path                               |
| `--target <file>` | Target README path                               |

When `--target` is omitted, the target filename is automatically determined.

```text
English source:
README.md → README.ko.md

Korean source:
README.md → README.en.md
```

The translated file is created in the same directory as the source file.

For example:

```text
docs/README.md → docs/README.ko.md
```

## Translation

Dedicated NLLB-based models are used for each direction:

| Direction        | Model                        |
| ---------------- | ---------------------------- |
| English → Korean | `NHNDQ/nllb-finetuned-en2ko` |
| Korean → English | `NHNDQ/nllb-finetuned-ko2en` |

Only the model required for the selected translation direction is loaded.

Before translation, Markdown elements such as code blocks, inline code, URLs, links, images, badges, and HTML are protected where possible. Human-readable text is then translated and the Markdown structure is restored.

Translation runs locally. README content is not sent to OpenAI, Anthropic, Gemini, DeepL, or another paid translation API.

> Translation models are distributed separately and have their own licenses and usage terms. Check the corresponding Hugging Face model card before redistribution or commercial use.

## GitHub Action

The project can also be used as a reusable GitHub Action.

English → Korean:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

Korean → English:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.md
```

`target-file` is optional and is automatically determined when omitted.

Custom filenames:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

### Automatic synchronization

Example for an English-first repository:

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

Replace `YOUR_GITHUB_NAME` with the GitHub username or organization that owns this repository.

For automatic source detection, use `fetch-depth: 2` so the CLI can compare the latest commit with its parent.

## Tests

```bash
npm test
```

The test suite does not download or load the translation models.

## Roadmap

- Incremental README translation
- Translate only changed Markdown blocks
- Preserve manually edited translations where possible
- Improved Markdown parsing and protection
- Translation model benchmarking
- GitHub Profile README support
- Additional local translation engines

## License

`readme-translate-kr-en` is licensed under the MIT License.

Translation models are downloaded separately and are not distributed as part of this project. Each model has its own license and usage terms.

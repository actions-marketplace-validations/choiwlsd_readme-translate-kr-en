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

GitHub를 위한 무료 로컬 퍼스트 영어  한국어 README 번역 및 동기화.

**API 키 없음. 유료 AI API** 없음.

`readme-translate-kr-en`는 오픈 소스 기계 번역 모델을 사용하여 README 파일을 로컬로 번역합니다. CLI 또는 GitHub Action으로 사용할 수 있습니다.

## 특징

- 영어 → 한국어 및 한국어 → 영어 번역
- 자동 번역된 README 파일명 검출
- 자동 번역 방향 검출
- 커스텀 소스 및 타겟 파일네임
- GitHub 친화적인 영어 / 한국어 네비게이션
- 가능한 경우 코드 블록, 인라인 코드, URL, 링크, 배지 및 HTML을 보존합니다.
- 유료 API가 없는 로컬 번역
- CLI 및 GitHub 액션 지원

## 요건

- 노드.js 20+
- 파이썬 3.10+

번역 모델은 첫 사용 시 Hugging Face에서 다운로드되어 로컬로 캐시됩니다.

## CLI 사용

### 1. 설치

패키지가 npm으로 게시된 후 `npx`로 직접 실행할 수 있습니다.

```bash
npx readme-translate-kr-en <command>
```

지역 개발을 위해:

```bash
python -m venv .venv
```

윈도우 파워 셸:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

그런 다음 다음과 같이 CLI를 실행하십시오.

```bash
node ./src/cli.js <command>
```

### 2. 이중 언어 리드미를 초기화

```bash
npx readme-translate-kr-en init
```

지역 개발을 위해:

```bash
node ./src/cli.js init
```

`init`는 README 파일의 상단에 언어 네비게이션을 생성하거나 업데이트한다.

```text
English | 한국어
```

### 3. 영어 → 한국어 번역

`README.md`를 영어로 표기하면 다음과 같다.

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

이를 통해 다음을 생성하거나 업데이트합니다.

```text
README.ko.md
```

### 4. 한국어 → 영어 번역

`README.md`를 한글로 표기하면 다음과 같다.

```bash
npx readme-translate-kr-en sync --from ko --source README.md
```

이를 통해 다음을 생성하거나 업데이트합니다.

```text
README.en.md
```

### 5. 맞춤형 파일명을 사용하세요

필요한 경우 소스 파일과 타겟 파일을 모두 지정합니다.

```bash
npx readme-translate-kr-en sync \
  --from ko \
  --source docs/README.md \
  --target docs/README.en.md
```

### 6. 자동 검출

또한 다음과 같이 실행할 수 있습니다.

```bash
npx readme-translate-kr-en sync
```

`--from`가 생략된 경우, CLI는 최신 Git commit에서 변경된 README를 결정하려고 시도하고 번역 방향을 자동으로 검출한다.

동일한 커밋에서 여러 개의 README 파일이 변경된 경우 자동 검출에 의존하는 대신 출처를 명시적으로 지정한다.

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

## CLI 옵션

| 옵션            | 디스크립션                                      |
| ----------------- | ------------------------------------------------ |
| `init`            | 이중 언어 README 네비게이션을 초기화 또는 업데이트 |
| `sync`            | README를 번역 및 동기화               |
| `--from en`       | 영어 → 한국어 번역                       |
| `--from ko`       | 한국어 → 영어 번역                       |
| `--source <file>` | 소스 리드미 경로                               |
| `--target <file>` | 타겟 리드미 경로                               |

`--target`가 생략된 경우, 타겟 파일 네임이 자동으로 결정된다.

```text
English source:
README.md → README.ko.md

Korean source:
README.md → README.en.md
```

번역된 파일은 소스 파일과 동일한 디렉토리에서 생성됩니다.

예를 들면.

```text
docs/README.md → docs/README.ko.md
```

## 번역

각 방향에 대해 전용 NLLB 기반 모델이 사용된다.

| 방향        | 모델                        |
| ---------------- | ---------------------------- |
| 영어 → 한국어 | `NHNDQ/nllb-finetuned-en2ko` |
| 한국어 → 영어 | `NHNDQ/nllb-finetuned-ko2en` |

선택한 번역 방향에 필요한 모델만 로드됩니다.

번역 전에 코드 블록, 인라인 코드, URL, 링크, 이미지, 배지 및 HTML과 같은 마크다운 요소가 가능한 경우 보호된다. 그런 다음 사람이 읽을 수 있는 텍스트가 번역되고 마크다운 구조가 복원된다.

번역은 로컬로 실행됩니다. README 콘텐츠는 OpenAI, Anthropic, Gemini, DeepL 또는 기타 유료 번역 API로 전송되지 않습니다.

> 번역모델은 별도로 배포되어 있으며 고유의 라이선스와 사용조건을 가지고 있다. 재배포 또는 상업적 사용 전에 해당 Hugging Face모델 카드를 확인한다.

## GitHub 액션

이 프로젝트는 재사용 가능한 GitHub Action으로도 사용할 수 있습니다.

영어 → 한국어:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

한국어 → 영어:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.md
```

`target-file`는 선택 사항이며 생략 시 자동으로 결정됩니다.

커스텀 파일 네임:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

### 자동 동기화

영어 우선 저장소에 대한 예시:

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

`YOUR_GITHUB_NAME`를 이 저장소를 소유한 GitHub 사용자 이름 또는 조직으로 교체하십시오.

자동 소스 검출을 위해 `fetch-depth: 2`를 사용하여 CLI가 최신 커밋을 모체와 비교할 수 있다.

## 테스트

```bash
npm test
```

테스트 제품군은 번역 모델을 다운로드하거나 로드하지 않습니다.

## 로드맵

- 인크레멘탈 리드미 번역
- 변경된 마크다운 블록만 번역
- 가능한 경우 수동으로 편집된 번역본을 보존합니다.
- 개선된 마크다운 파싱 및 보호
- 번역 모델 벤치마킹
- GitHub 프로파일 README 지원
- 추가 로컬 번역 엔진

## 라이선스

`readme-translate-kr-en`는 MIT 라이선스에 따라 라이선스됩니다.

번역 모델은 별도로 다운로드되며 이 프로젝트의 일부로 배포되지 않습니다. 각 모델에는 고유한 라이선스 및 사용 조건이 있습니다.

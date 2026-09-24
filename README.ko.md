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

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-readme--translate--kr--en-blue?logo=github)](https://github.com/marketplace/actions/readme-translate-kr-en))
[![GitHub release](https://img.shields.io/github/v/release/choiwlsd/readme-translate-kr-en)](https://github.com/choiwlsd/readme-translate-kr-en/releases/latest))
[![CI](https://github.com/choiwlsd/readme-translate-kr-en/actions/workflows/ci.yml/badge.svg)](https://github.com/choiwlsd/readme-translate-kr-en/actions/workflows/ci.yml))
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

영어와 한국어 README 파일을 번역하고 동기화하기 위한 무료 로컬 퍼스트 깃허브 액션입니다.

**npm 패키지 또는 유료 번역 API가 필요하지 않습니다.** 번역은 오픈 소스 기계 번역 모델이 있는 GitHub 액션 러너에서 실행됩니다.

##  스타트

번역하고자 하는 README를 포함하는 리포지토리에서 `.github/workflows/translate-readme.yml`을 생성한다.

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
        uses: actions/checkout@v7

      - name: Translate README
        uses: choiwlsd/readme-translate-kr-en@v0.2.1
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

### 첫 번째 번역을 생성합니다.

워크플로우 파일을 추가하는 것은 `README.md`가 변경되지 않은 경우 즉시 실행되지 않습니다. 워크플로우 파일을 디폴트 브랜치로 커밋하고 푸시한 후:

1. GitHub에서 리포지토리의 **Actions** 탭을 엽니다.
2. **Sync 이중 언어 README**을 선택한다.
3. **Run workfloww**을 선택하고, 디폴트 브랜치를 선택하여 실행합니다.
4. 워크플로우가 끝날 때까지 기다립니다. 그것은 `README.md`에서 지배적인 언어를 감지한 다음, 영어 소스 콘텐츠의 경우 `README.ko.md` 또는 한국어 소스 콘텐츠의 경우 `README.en.md`를 생성하고 커밋합니다.

작업 흐름은 **Run workfloww** 버튼이 사용 가능하기 전에 기본 브랜치에 존재해야 합니다. 커밋 단계가 거부되면 **Settings → Actions → General → Workflow permissions**를 열고 GitHub Actions가 저장소 콘텐츠를 작성할 수 있는지 확인하십시오. 조직 정책 또는 브랜치

첫 번째 번역 후, `README.md`을 변경하는 후속 푸시마다 워크플로우가 자동으로 실행됩니다. 또한 소스 README를 편집하지 않고 번역을 재생산하고 싶을 때마다 **Run workfloww**를 사용할 수 있습니다.

콘텐츠 기반 언어 검출을 원할 때 `from`를 설정하지 마십시오. `from: en` 또는 `from: ko`를 설정하면 의도적으로 검출을 무시하고 소스 언어를 강제합니다. 마크다운 코드 블록, URL, HTML 및 기타 비언어 콘텐츠는 한글 및 영어 문자를 계산하기 전에 최대한 제외됩니다.

첫 번째 실행은 번역 모델을 다운로드합니다. 이후 실행은 액션에서 관리하는 Hugging Face 모델 캐시를 재사용합니다.

> 브랜치 보호를 갖는 리포지토리들은 `GITHUB_TOKEN`으로부터의 직접 푸쉬들을 거부할 수 있다. GitHub 액션들이 타겟 브랜치로 푸쉬하도록 허용하거나 풀 요청을 열기 위해 최종 단계를 적응시킨다.

## 특징

- 영어 → 한국어 및 한국어 → 영어 번역
- GitHub 액션 러너에서 로컬로 실행
- API 키 또는 유료 AI 서비스가 없습니다
- 자동 번역된 README 파일명 선택
- 맞춤형 소스 및 타겟 경로
- 최신 커밋으로부터의 자동 번역 방향 검출
- 울타리 코드, 인라인 코드, 인라인 및 참조 링크, 이미지, 배지, HTML, 강조점, YAML 전면 사항 및 이모지를 보존합니다.
- 생성된 README 파일에 영어/ 한국어 네비게이션을 추가합니다
- 실행 사이에 껴안는 얼굴 모델을 다운로드한 캐시

## 용도

### 영어에서 한국어로

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.1
  with:
    from: en
    source-file: README.md
```

기본 대상은 `README.ko.md`입니다.

### 한국어에서 영어로

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.1
  with:
    from: ko
    source-file: README.ko.md
```

기본 대상은 `README.md`입니다.

### 커스텀 파일네임

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.1
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

### 자동 소스 검출

최신 커밋에서 단일 변경된 표준 README를 검출하려면 `from` 및 `source-file`을 생략한다.

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.1
```

자동 검출에 의존할 때 `fetch-depth: 2`을 사용하세요.

```yaml
- uses: actions/checkout@v7
  with:
    fetch-depth: 2
```

최신 커밋에서 하나 이상의 표준 README가 변경된 경우 `from` 및 `source-file`을 명시적으로 지정한다.

## 입력

| 입력            | 요구 사항 | 디폴트                    | 디스크립션                                   |
| ---------------- | -------- | -------------------------- | --------------------------------------------- |
| `from`           | 아니야.       | 자동 검출                | 소스 언어: `en` 또는 `ko`                 |
| `source-file`    | 아니야.       | 자동 검출 또는 `README.md` | 소스 리드미 경로                            |
| `target-file`    | 아니야.       | 자동으로 생성    | 번역된 README 경로                        |
| `python-version` | 아니야.       | `3.11`                     | 번역 엔진에 의해 사용되는 파이썬 버전 |

## 어떻게 작동하는지.

액션은 파이썬 번역 의존성을 설치하고, 캐싱된 Hugging Face 모델을 복원하고, Markdown 요소를 보호하며, 사람이 읽을 수 있는 텍스트를 번역하고, 번역된 README를 다시 확인된 저장소에 기록한다.

액션은 파일만 수정합니다. 결과를 수행하고 푸시하는 것은 호출자 워크플로우의 제어 하에 남아 있습니다.

각 방향에 대해 전용 NLLB 기반 모델이 사용된다.

| 방향        | 모델                        |
| ---------------- | ---------------------------- |
| 영어 → 한국어 | `NHNDQ/nllb-finetuned-en2ko` |
| 한국어 → 영어 | `NHNDQ/nllb-finetuned-ko2en` |

README 콘텐츠는 러너에서 처리되며 OpenAI, Anthropic, Gemini, DeepL 또는 다른 유료 번역 API로 전송되지 않습니다.

> 번역 모델은 별도로 배포되어 있으며 고유의 라이선스와 사용 조건을 가지고 있다. 재배포 또는 상업적 사용 전에 해당 Hugging Face 모델 카드를 검토한다.

## 지역 개발

저장소에는 개발 CLI도 포함되어 있지만 현재 npm으로 게시되지 않는다.

요건:

- 노드.js 20+
- 파이썬 3.10+

```bash
python -m venv .venv
python -m pip install -r requirements.txt
node ./src/cli.js sync --from en --source README.md
```

윈도우에서 다음과 같이 가상 환경을 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

테스트 스위트를 다음과 같이 실행하십시오.

```bash
npm test
```

단위 테스트는 번역 모델을 다운로드하거나 로드하지 않습니다.

## 방출

현재 마켓플레이스 릴리스는 [`v0.2.1`](https://github.com/choiwlsd/readme-translate-kr-en/releases/tag/v0.2.1)입니다. 전체 릴리스 태그를 고정하면 재현 가능한 동작이 제공됩니다.

```yaml
uses: choiwlsd/readme-translate-kr-en@v0.2.1
```

## 라이선스

이 프로젝트는 [MIT License](./LICENSE)에 따라 라이선스를 받았습니다.

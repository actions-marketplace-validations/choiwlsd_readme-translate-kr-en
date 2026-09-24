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

번역하고자 하는 README를 포함하는 저장소에 `.github/workflows/translate-readme.yml`를 생성한다.

```yaml
name: Sync Korean README

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
          from: en
          source-file: README.md

      - name: Commit translated README
        run: |
          if git diff --quiet -- README.md README.ko.md; then exit 0; fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add README.md README.ko.md
          git commit -m "docs: sync Korean README"
          git push
```

첫 번째 실행은 번역 모델을 다운로드합니다. 이후 실행은 액션에서 관리하는 Hugging Face 모델 캐시를 재사용합니다.

> 브랜치 보호를 갖는 리포지토리들은 `GITHUB_TOKEN`로부터의 직접 푸쉬들을 거부할 수 있다. GitHub 액션들이 타겟 브랜치로 푸쉬하도록 허용하거나 풀 요청을 열기 위해 최종 단계를 적응시킨다.

## 특징

- 영어 → 한국어 및 한국어 → 영어 번역
- GitHub 액션 러너에서 로컬로 실행
- API 키 또는 유료 AI 서비스가 없습니다
- 자동 번역된 README 파일명 선택
- 맞춤형 소스 및 타겟 경로
- 최신 커밋으로부터의 자동 번역 방향 검출
- 가능한 경우 울타리 코드, 인라인 코드, URL, 링크, 배지 및 HTML을 보존합니다.
- 생성된 README 파일에 영어/ 한국어 네비게이션을 추가합니다
- 실행 사이에 껴안는 얼굴 모델을 다운로드한 캐시

## 용도

### 영어에서 한국어로

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

기본 대상은 `README.ko.md`입니다.

### 한국어에서 영어로

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.ko.md
```

기본 대상은 `README.md`입니다.

### 커스텀 파일네임

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

### 자동 소스 검출

`from` 및 `source-file`를 생략하여 최신 커밋에서 단일 변경된 표준 README를 검출한다.

```yaml
- uses: choiwlsd/readme-translate-kr-en@v0.2.0
```

자동 검출에 의존할 때 `fetch-depth: 2`를 사용한다.

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

최신 커밋에서 하나 이상의 표준 README가 변경된 경우 `from` 및 `source-file`를 명시적으로 지정한다.

## 입력

| 입력 | 요구 사항 | 디폴트 | 디스크립션 |
| --- | --- | --- | --- |
| `from` | 아니야. | 자동 검출 | 소스 언어: `en` 또는 `ko` |
| `source-file` | 아니야. | 자동 검출 또는 `README.md` | 소스 리드미 경로 |
| `target-file` | 아니야. | 자동으로 생성 | 번역된 README 경로 |
| `python-version` | 아니야. | `3.11` | 번역 엔진에 의해 사용되는 파이썬 버전 |

## 어떻게 작동하는지.

액션은 파이썬 번역 의존성을 설치하고, 캐싱된 Hugging Face 모델을 복원하고, Markdown 요소를 보호하며, 사람이 읽을 수 있는 텍스트를 번역하고, 번역된 README를 다시 확인된 저장소에 기록한다.

액션은 파일만 수정합니다. 결과를 수행하고 푸시하는 것은 호출자 워크플로우의 제어 하에 남아 있습니다.

각 방향에 대해 전용 NLLB 기반 모델이 사용된다.

| 방향 | 모델 |
| --- | --- |
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

현재 마켓플레이스 릴리스는 [`v0.2.0`](https://github.com/choiwlsd/readme-translate-kr-en/releases/tag/v0.2.0)입니다. 전체 릴리스 태그를 고정하면 재현 가능한 동작이 제공됩니다.

```yaml
uses: choiwlsd/readme-translate-kr-en@v0.2.0
```

## 라이선스

이 프로젝트는 [MIT License](./LICENSE)에 따라 라이선스를 받았습니다.

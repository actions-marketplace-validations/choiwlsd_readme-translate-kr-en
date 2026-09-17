<!-- readme-bilingual:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-bilingual:end -->

# 읽기-중언어

무료, 현지 최초 영어  한국어 README 동기화 GitHub.

API 키가 없고 AI API도 없고

번역은 CLI 또는 GitHub 액션 런어를 실행하는 기기에서 오픈소스 기계 번역 모델을 사용하여 로컬로 실행됩니다.

## 그 역할은

- `README.md`와 `README.ko.md`를 동기화
- GitHub 친화적인 영어 / 한국어 탐색을 추가합니다
- 울타리 코드 블록, 인라인 코드, URL, 링크, 배지 및 HTML를 가능한 한 보존합니다
- 번역 API 없이 로컬로 실행됩니다
- CLI와 재사용 가능한 GitHub 액션으로 작동합니다
- `--from`가 생략되면 자동으로 README가 변경된 것을 감지합니다.

## 번역 모델

`readme-bilingual`는 현재 사용:

| 모델                              | 언어        |
| ---------------------------------- | ---------------- |
| _RB_TOKEN_0__ | 영어  한국어 |

NLLB 언어 코드:

| 언어 | 코드       |
| -------- | ---------- |
| 영어  | _RB_TOKEN_0__ |
| 한국어   | _RB_TOKEN_0__ |

단일 NLLB 모델은 양방향에서 번역을 처리합니다.

이 모델은 처음 사용 시 Hugging Face에서 다운로드 받아 다음 실행을 위해 로컬 캐시로 저장됩니다.

README 콘텐츠는 `readme-bilingual`를 실행하는 기계에서 처리되며 유료 번역이나 LLM API에 전송되지 않습니다.

> 번역 모델은 자체 라이선스 및 사용 조건이 있습니다. 재배포 또는 상업적 사용 전에 모델 카드를 확인하십시오.

## 지역 CLI

요구 사항:

- Node.js 20+
- 파이썬 3.10+

번역 의존성을 설치하기 전에 파이썬 가상 환경을 생성하고 활성화하십시오.

### 윈도우 파워셸

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

다음으로 README 파일을 초기화하고 동기화합니다.

```powershell
node ./src/cli.js init
node ./src/cli.js sync --from en
```

한국어 → 영어:

```powershell
node ./src/cli.js sync --from ko
```

### 의도된 npm 인터페이스

npm에 게시한 후, 의도된 인터페이스는:

```bash
npx readme-bilingual init
npx readme-bilingual sync --from en
npx readme-bilingual sync --from ko
```

## 어떻게 작동하는지

영어 → 한국어:

```text
README.md
   ↓
Markdown protection
   ↓
NLLB 600M
   ↓
README.ko.md
```

한국어 → 영어:

```text
README.ko.md
   ↓
Markdown protection
   ↓
NLLB 600M
   ↓
README.md
```

울타리 코드 블록, 인라인 코드, URL, 링크, 배지 및 HTML와 같은 마크다운 요소는 가능한 한 번역으로부터 보호됩니다.

## GitHub 액션

소비자 저장소는 번역 API 키 또는 API 비밀 없이 동작을 사용할 수 있습니다.

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

CLI가 가장 최근의 커밋에서 원천 README를 추론하기를 원한다면 `from: en`를 제거하십시오.

## 비용 모델

`readme-bilingual`는 OpenAI, Anthropic, Gemini, DeepL 또는 다른 유료 번역 API를 호출하지 않습니다.

** 번역 API 키가 필요하지 않으며 도구 자체는 번역 API 청구서를 생성하지 않습니다.**

번역 모델은 로컬 머신이나 러너에서 실행됩니다.

GitHub에서 호스팅된 액션의 사용은 저장소의 소유자의 GitHub 계획과 사용 제한에 의해 별도로 관리됩니다. 로컬 또는 자체 호스팅 된 러너에서 `readme-bilingual`를 실행하면 GitHub에서 호스팅된 컴퓨팅에 의존하는 것을 피합니다.

## 시험

아래와 같이 단위 테스트를 수행합니다.

```bash
npm test
```

단위 테스트는 번역 모델을 다운로드하지 않습니다.

## 라이센스

`readme-bilingual`는 MIT 라이선스에 따라 라이선스되어 있습니다.

번역 모델은 별도로 배포되며 자체 라이선스 및 사용 조건이 있습니다. 재 배포 또는 상업적 배포 전에 해당 Hugging Face 모델 카드를 확인하십시오.

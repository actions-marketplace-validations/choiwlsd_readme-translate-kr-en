<!-- readme-translate-kr-en:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-translate-kr-en:end -->

# 리드미-이중언어

GitHub를 위한 무료 로컬 퍼스트 영어 한국어 README 동기화입니다.

**API 키 없음. 유료 AI API** 없음.

`readme-bilingual`는 오픈 소스 기계 번역 모델을 사용하여 README 콘텐츠를 로컬로 번역합니다. 번역은 CLI 또는 GitHub 액션 러너를 실행하는 기계에서 전적으로 실행됩니다.

## 그게 하는 거.

- `README.md` 및 `README.ko.md`를 동기화한다
- 영어 → 한국어 및 한국어 → 영어 번역을 지원합니다.
- 각 방향에 대한 전용 번역 모델을 사용
- GitHub 친화적인 영어/ 한국어 네비게이션을 추가합니다
- 울타리 코드 블록, 인라인 코드, URL, 링크, 배지 및 HTML을 최대한 보존합니다.
- 번역 API 없이 로컬로 실행
- CLI 및 재사용 가능한 GitHub 액션으로 작동합니다.
- `--from`가 누락된 경우 어떤 README가 변경되었는지 자동으로 감지합니다.

## 번역 모델

`readme-bilingual`는 각 번역 방향에 대해 전용 NLLB 기반 모델을 사용한다.

| 방향          | 모델                         |
| ------------- | ---------------------------- |
| 영어 → 한국어 | `NHNDQ/nllb-finetuned-en2ko` |
| 한국어 → 영어 | `NHNDQ/nllb-finetuned-ko2en` |

NLLB 언어 코드:

| 언어    | 코드       |
| ------- | ---------- |
| 영어.   | `eng_Latn` |
| 한국어. | `kor_Hang` |

요청한 번역 방향에 필요한 모델만 로드됩니다.

예를 들면.

```bash
readme-bilingual sync --from en
```

영어 → 한국어 모델을 사용하는 반면:

```bash
readme-bilingual sync --from ko
```

한국어 → 영어 모델을 사용합니다.

모델은 첫 사용 시 Hugging Face에서 다운로드되고 후속 실행을 위해 로컬로 캐시됩니다.

README 콘텐츠는 `readme-bilingual`를 실행하는 기계에서 처리되며 유료 번역 또는 LLM API로 전송되지 않는다.

> 번역모델은 별도로 배포되어 있으며 고유의 라이선스와 사용조건을 가지고 있다. 재배포 또는 상업적 사용 전에 해당 Hugging Face모델 카드를 확인한다.

## 로컬 CLI

### 요건

- 노드.js 20+
- 파이썬 3.10+

번역 의존성을 설치하기 전에 파이썬 가상 환경을 생성하고 활성화합니다.

### 윈도우 파워

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

이중 언어 README 파일을 초기화합니다.

```powershell
node ./src/cli.js init
```

영어 → 한국어 번역:

```powershell
node ./src/cli.js sync --from en
```

한국어 → 영어 번역:

```powershell
node ./src/cli.js sync --from ko
```

## 의도된 NPM 인터페이스

npm으로 게시한 후 의도된 인터페이스는 다음과 같다.

```bash
npx readme-bilingual init

npx readme-bilingual sync --from en

npx readme-bilingual sync --from ko
```

`--from`가 생략된 경우, `readme-bilingual`는 어떤 README가 가장 최근에 변경되었는지를 결정하려고 시도한다.

```bash
npx readme-bilingual sync
```

## 어떻게 작동하는지.

영어 → 한국어:

```text
README.md
   ↓
Markdown protection
   ↓
English → Korean model
   ↓
README.ko.md
```

한국어 → 영어:

```text
README.ko.md
   ↓
Markdown protection
   ↓
Korean → English model
   ↓
README.md
```

번역 전에 `readme-bilingual`는 변경되지 않은 상태로 유지되어야 하는 마크다운 요소로부터 번역 가능한 텍스트를 분리한다.

그것은 보존하려고 시도합니다.

- 울타리 코드 블록
- 인라인 코드
- 코드 블록 내부의 명령
- URL
- 마크다운 링크
- 이미지
- 배지
- HTML
- 마크다운 구조
- 마크다운 신택스에 의해 보호될 때 파일 경로 및 패키지 이름

사람이 읽을 수 있는 텍스트만 가능한 경우 번역 모델을 통해 전송됩니다.

## GitHub 액션

리포지토리는 번역 API 키나 API 시크릿을 구성하지 않고도 `readme-bilingual`를 사용할 수 있다.

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

사용:

```yaml
with:
  from: en
```

영어 → 한국어 번역을 위한.

사용:

```yaml
with:
  from: ko
```

한국어 → 영어 번역용입니다.

`from`가 생략되면, CLI는 최신 커밋으로부터 소스 README를 추론하려고 시도한다.

## 모델 캐싱

번역 모델은 필요할 때만 다운로드하고 Hugging Face에서 캐싱합니다.

예를 들어, 달리기:

```bash
readme-bilingual sync --from en
```

첫 사용 시 영어 → 한국어 모델을 다운로드합니다.

후속 실행은 사용 가능한 경우 캐시된 모델을 재사용한다.

한국어 → 영어 모델은 그 번역 방향이 처음 사용될 때 별도로 다운로드된다.

이것은 한 방향만 필요할 때 두 번역 모델을 모두 로딩하는 런타임을 방지한다.

## 비용 모델

`readme-bilingual`는 OpenAI, Anthropic, Gemini, DeepL 또는 기타 유료 번역 API를 호출하지 않습니다.

**번역 API 키가 필요하지 않으며 `readme-bilingual` 자체가 번역 API 청구서를 생성하지 않습니다. **

번역은 대신 로컬 머신 또는 CI 러너에서 실행됩니다.

GitHub에서 호스팅하는 액션 사용은 저장소 소유자의 GitHub 계획과 사용 제한에 의해 별도로 관리된다.

`readme-bilingual`를 로컬로 또는 자체-호스팅된 러너 상에서 실행하는 것은 GitHub-호스팅된 컴퓨트에 의존하는 것을 회피한다.

## 테스트

다음과 같이 단위 테스트를 실행하십시오.

```bash
npm test
```

단위 테스트는 번역 모델을 다운로드하거나 로드하지 않습니다.

## 로드맵

계획된 개선 사항에는 다음이 포함됩니다.

- 인크레멘탈 리드미 번역
- 변경된 마크다운 블록만 번역
- 가능한 경우 수동으로 편집된 번역본을 보존합니다.
- 개선된 마크다운 파싱 및 보호
- 번역 모델 벤치마킹
- GitHub 프로파일 README 지원
- 추가 로컬 번역 엔진

번역을 로컬, 예측 가능하고 유료 번역 API로부터 자유로운 상태로 유지하면서 이중 언어 README 유지 관리를 자동화하는 것이 장기적 목표이다.

## 라이선스

`readme-bilingual`는 MIT 라이선스에 따라 라이선스됩니다.

번역 모델은 별도로 다운로드되며 `readme-bilingual`의 일부로 배포되지 않는다.

각 번역 모델에는 자체 라이선스 및 사용 조건이 있습니다. 재배포 또는 상업적 배포 전에 해당 Hugging Face 모델 카드를 확인하십시오.

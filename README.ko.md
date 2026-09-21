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

`readme-translate-kr-en`는 오픈 소스 기계 번역 모델을 사용하여 README 콘텐츠를 로컬로 번역합니다. 번역은 CLI 또는 GitHub 액션 러너를 실행하는 기계에서 전적으로 실행됩니다.

## 그게 하는 거.

- 영어 → 한국어 및 한국어 → 영어 번역을 지원합니다.
- 번역된 README를 자동으로 생성하거나 업데이트합니다.
- 맞춤형 소스 및 타겟 README 파일명을 지원합니다
- `target-file`가 누락된 경우 타겟 파일명을 자동으로 결정합니다.
- 각 방향에 대한 전용 번역 모델을 사용합니다.
- GitHub 친화적인 영어/ 한국어 네비게이션을 추가합니다
- 울타리 코드 블록, 인라인 코드, URL, 링크, 배지 및 HTML을 최대한 보존합니다.
- 번역 API 없이 로컬로 실행
- CLI 및 재사용 가능한 GitHub 액션으로 작동합니다.
- 가능한 경우 `--from`가 생략된 경우 어떤 README가 변경되었는지 자동으로 감지합니다.

## README 파일 네이밍

디폴트로, `readme-translate-kr-en`는 소스 언어로부터 번역된 README 파일명을 자동으로 결정할 수 있다.

예를 들면.

```text
from: en
source-file: README.md
target-file: empty

→ README.ko.md
```

그리고.

```text
from: ko
source-file: README.md
target-file: empty

→ README.en.md
```

이는 다음의 두 가지 프로젝트 구조가 모두 지원된다는 것을 의미한다.

메인 README로서의 영어:

```text
README.md
README.ko.md
```

메인 README로 한국어:

```text
README.md
README.en.md
```

소스 파일과 타겟 파일을 모두 명시적으로 지정하여 맞춤 파일명을 사용할 수도 있습니다.

예를 들면.

```text
docs/README.md
docs/README.en.md
```

아니면.

```text
README_EN.md
README_KR.md
```

`target-file`가 생략된 경우, 번역된 파일은 소스 파일과 동일한 디렉토리에 생성된다.

예시:

```text
README.md
→ README.ko.md

docs/README.md
→ docs/README.ko.md

guide.md
→ guide.ko.md
```

영어 → 한국어 번역을 위한.

한국어 → 영어 번역의 경우:

```text
README.md
→ README.en.md

docs/README.md
→ docs/README.en.md

guide.md
→ guide.en.md
```

## 번역 모델

`readme-translate-kr-en`는 각 번역 방향에 대해 전용 NLLB 기반 모델을 사용한다.

| 방향        | 모델                        |
| ---------------- | ---------------------------- |
| 영어 → 한국어 | `NHNDQ/nllb-finetuned-en2ko` |
| 한국어 → 영어 | `NHNDQ/nllb-finetuned-ko2en` |

NLLB 언어 코드:

| 언어 | 코드       |
| -------- | ---------- |
| 영어.  | `eng_Latn` |
| 한국어.   | `kor_Hang` |

요청한 번역 방향에 필요한 모델만 로드됩니다.

예를 들면.

```bash
readme-translate-kr-en sync --from en
```

영어 → 한국어 모델을 사용하는 반면:

```bash
readme-translate-kr-en sync --from ko
```

한국어 → 영어 모델을 사용합니다.

모델은 첫 사용 시 Hugging Face에서 다운로드되고 후속 실행을 위해 로컬로 캐시됩니다.

README 콘텐츠는 `readme-translate-kr-en`를 실행하는 기계에서 처리되며 유료 번역 또는 LLM API로 전송되지 않는다.

> 번역모델은 별도로 배포되어 있으며 고유의 라이선스와 사용조건을 가지고 있다. 재배포 또는 상업적 사용 전에 해당 Hugging Face모델 카드를 확인한다.

## 지역 개발

### 요건

- RB_TOKEN_0__ 20+
- RB_TOKEN_0__ 3.10+ __

번역 종속성을 설치하기 전에 리포지토리를 복제하고 파이썬 가상 환경을 생성한다.

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

영어 `README.md`를 `README.ko.md`로 번역합니다.

```powershell
node ./src/cli.js sync --from en --source README.md
```

한국어 `README.md`를 `README.en.md`로 번역합니다.

```powershell
node ./src/cli.js sync --from ko --source README.md
```

목표 파일명을 수동으로 지정합니다.

```powershell
node ./src/cli.js sync --from ko --source README.md --target README.en.md
```

번역 방향을 자동으로 감지합니다:

```powershell
node ./src/cli.js sync
```

`--from`가 생략된 경우, CLI는 최신 Git 커밋을 확인하고 어떤 구성 README가 변경되었는지를 결정하려고 시도한다.

## npm 사용량

패키지가 npm으로 공표된 후 글로벌 설치 없이 사용할 수 있습니다.

이중 언어 README 파일을 초기화합니다.

```bash
npx readme-translate-kr-en init
```

영어 → 한국어 번역:

```bash
npx readme-translate-kr-en sync --from en --source README.md
```

`--target`가 누락된 경우:

```text
README.md
→ README.ko.md
```

한국어 → 영어 번역:

```bash
npx readme-translate-kr-en sync --from ko --source README.md
```

`--target`가 누락된 경우:

```text
README.md
→ README.en.md
```

맞춤형 타겟 파일을 지정합니다.

```bash
npx readme-translate-kr-en sync \
  --from ko \
  --source docs/README.md \
  --target docs/README.en.md
```

번역 방향을 자동으로 감지합니다:

```bash
npx readme-translate-kr-en sync
```

`init` 명령은 README 파일의 상단에 언어 네비게이션을 생성하거나 업데이트한다.

초기화 후, README 파일들은 다음과 같은 네비게이션을 포함한다.

```text
English | 한국어
```

링크는 구성된 영어 및 한국어 README 경로로부터 생성된다.

## 어떻게 작동하는지.

영어 → 한국어:

```text
source file
   ↓
Markdown protection
   ↓
English → Korean model
   ↓
target file
```

예시:

```text
README.md
   ↓
README.ko.md
```

한국어 → 영어:

```text
source file
   ↓
Markdown protection
   ↓
Korean → English model
   ↓
target file
```

예시:

```text
README.md
   ↓
README.en.md
```

번역 전에 `readme-translate-kr-en`는 변경되지 않은 상태로 유지되어야 하는 마크다운 요소로부터 번역 가능한 텍스트를 분리한다.

그것은 보존하려고 시도합니다.

- 울타리 코드 블록
- 인라인 코드
- 코드 블록 내부의  명령
- URL
- 마크다운 링크
- 이미지
- 배지
- HTML
- 마크다운 구조
- 마크다운 신택스에 의해 보호될 때 파일 경로 및 패키지 이름

사람이 읽을 수 있는 텍스트만 가능한 경우 번역 모델을 통해 전송됩니다.

## GitHub 액션

`readme-translate-kr-en`는 재사용 가능한 GitHub Action으로도 사용될 수 있다.

번역 API 키나 API 비밀이 필요하지 않습니다.

액션은 다음과 같은 입력을 지원합니다.

| 입력            | 디스크립션                                   | 디폴트                  |
| ---------------- | --------------------------------------------- | ------------------------ |
| `from`           | 소스 언어: `en` 또는 `ko`                 | 자동 검출              |
| `source-file`    | 번역 소스로 사용되는 README 파일    | `README.md`              |
| `target-file`    | 번역된 README 경로                        | 자동 결정 |
| `python-version` | 번역 엔진에 의해 사용되는 파이썬 버전 | `3.11`                   |

### 메인 리드미로서의 영어 리드미

프로젝트에서 다음을 사용하는 경우:

```text
README.md
README.ko.md
```

사용:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: en
    source-file: README.md
```

`target-file`가 생략되기 때문에, 액션은 자동으로 다음을 사용한다.

```text
README.ko.md
```

### 메인 README로서의 한국어 README

프로젝트에서 다음을 사용하는 경우:

```text
README.md
README.en.md
```

사용:

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: README.md
```

`target-file`가 생략되기 때문에, 액션은 자동으로 다음을 사용한다.

```text
README.en.md
```

### 맞춤형 소스 및 타겟 파일

두 파일을 명시적으로 정의할 수 있습니다.

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
    source-file: docs/README.md
    target-file: docs/README.en.md
```

이것은 저장소가 맞춤형 README 네이밍 컨벤션을 사용할 때 유용합니다.

### 예시적인 워크플로우

Create:

```text
.github/workflows/readme-translate.yml
```

영어가 메인 README인 프로젝트의 경우 다음과 같습니다.

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

한국어가 주요 README인 프로젝트의 경우:

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

`YOUR_GITHUB_NAME`를 `readme-translate-kr-en` 저장소를 소유한 GitHub 사용자 이름 또는 조직으로 교체한다.

## 자동 방향 검출

`from`를 생략할 수 있습니다.

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
```

그런 다음 CLI는 최신 Git 커밋을 확인하고 어떤 README가 변경되었는지 결정하려고 시도한다.

자동 검출을 위해 다음과 같이 사용하세요.

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 2
```

따라서 액션은 최신 커밋을 모체와 비교할 수 있습니다.

두 README 파일이 동일한 커밋에서 수정되어 소스 언어를 안전하게 결정할 수 없는 경우 `from`를 명시적으로 지정한다.

예를 들면.

```yaml
- uses: YOUR_GITHUB_NAME/readme-translate-kr-en@v0.2.0
  with:
    from: ko
```

## 언어 네비게이션

`readme-translate-kr-en`는 이중언어 README 파일의 상단에 언어 내비게이션 블록을 유지한다.

예를 들면.

```html

```

맞춤형 파일명이 사용될 때, 네비게이션 링크는 그 파일명을 반영해야 한다.

예를 들어, 한국어가 메인 README인 경우:

```text
README.md
README.en.md
```

내비게이션은 다음과 같습니다.

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

네비게이션 블록은 번역 전에 제거되고 그 후에 다시 추가된다.

이는 언어 선택기 자체가 번역되는 것을 방지하고 반복 동기화에 대해 중복 네비게이션 블록을 추가하는 것을 방지한다.

## 모델 캐싱

번역 모델은 필요할 때만 다운로드됩니다.

예를 들면.

```bash
readme-translate-kr-en sync --from en
```

영어 → 한국어 모델을 로드합니다.

첫 번째 사용 시, 모델은 Hugging Face에서 다운로드된다. 후속 실행은 사용 가능한 경우 캐시된 모델을 재사용한다.

한국어 → 영어 모델은 다음과 같은 경우 별도로 다운로드됩니다.

```bash
readme-translate-kr-en sync --from ko
```

처음 사용하는 제품입니다.

GitHub 액션은 또한 호환 가능한 워크플로우 실행 사이에 Hugging Face 모델 디렉토리를 캐싱하여 불필요한 모델 다운로드를 줄인다.

선택한 번역 방향에 필요한 모델만 로드하면 됩니다.

## 비용 모델

`readme-translate-kr-en`는 OpenAI, Anthropic, Gemini, DeepL 또는 기타 유료 번역 API를 호출하지 않습니다.

**번역 API 키가 필요하지 않으며 `readme-translate-kr-en` 자체가 번역 API 청구서를 생성하지 않습니다. **

번역은 대신 로컬 머신 또는 CI 러너에서 실행됩니다.

GitHub에서 호스팅하는 액션 사용은 저장소 소유자의 GitHub 계획과 사용 제한에 의해 별도로 관리된다.

`readme-translate-kr-en`를 로컬로 또는 자체-호스팅된 러너 상에서 실행하는 것은 GitHub-호스팅된 컴퓨트에 의존하는 것을 회피한다.

## 테스트

테스트 스위트를 다음과 같이 실행하십시오.

```bash
npm test
```

테스트 제품군은 번역 모델을 다운로드하거나 로드하지 않습니다.

## 로드맵

계획된 개선 사항에는 다음이 포함됩니다.

- 인크레멘탈 리드미 번역
- 변경된 마크다운 블록만 번역
- 가능한 경우 수동으로 편집된 번역본을 보존합니다.
- 개선된 마크다운 파싱 및 보호
- 번역 모델 벤치마킹
- GitHub 프로파일 README 지원
- 추가 로컬 번역 엔진
- 보다 유연한 이중 언어 파일 검출

번역을 로컬, 예측 가능하고 유료 번역 API로부터 자유로운 상태로 유지하면서 이중 언어 README 유지 관리를 자동화하는 것이 장기적 목표이다.

## 라이선스

`readme-translate-kr-en`는 MIT 라이선스에 따라 라이선스됩니다.

번역 모델은 별도로 다운로드되며 `readme-translate-kr-en`의 일부로 배포되지 않는다.

각 번역 모델에는 자체 라이선스 및 사용 조건이 있습니다. 재배포 또는 상업적 배포 전에 해당 Hugging Face 모델 카드를 확인하십시오.

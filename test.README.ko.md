<!-- readme-bilingual:start -->
<p align="right">
  <a href="./README.md">English</a> · <a href="./README.ko.md">한국어</a>
</p>
<!-- readme-bilingual:end -->

# readme-bilingual

GitHub README를 영어 ↔ 한국어로 동기화하는 무료 로컬 우선 도구입니다.

**API 키가 필요 없고 유료 AI API도 사용하지 않습니다.** 번역은 CLI를 실행하는 컴퓨터나 GitHub Actions runner에서 오픈소스 기계번역 모델로 수행됩니다.

## 기능

- `README.md`와 `README.ko.md` 동기화
- GitHub에서 동작하는 English / 한국어 언어 이동 링크 자동 삽입
- 코드 블록, 인라인 코드, URL, 링크, 배지, HTML을 가능한 한 그대로 보존
- 오픈소스 번역 모델을 로컬에서 실행
- CLI와 재사용 가능한 GitHub Action 지원
- `--from`을 생략하면 최근 커밋에서 변경된 README를 감지

## 번역 모델

| 방향 | 모델 |
| --- | --- |
| 영어 → 한국어 | `Helsinki-NLP/opus-mt-tc-big-en-ko` |
| 한국어 → 영어 | `Helsinki-NLP/opus-mt-ko-en` |

첫 실행 시 Hugging Face에서 모델을 내려받고 이후 로컬 캐시를 사용합니다. README 번역 텍스트를 유료 AI API로 전송하지 않습니다.

## 로컬 CLI

필요 환경: Node.js 20+, Python 3.10+.

```bash
python3 -m pip install -r requirements.txt
node ./src/cli.js init
node ./src/cli.js sync --from en
```

한국어 → 영어:

```bash
node ./src/cli.js sync --from ko
```

npm 배포 후 목표 사용 방식은 다음과 같습니다.

```bash
npx readme-bilingual init
npx readme-bilingual sync --from en
```

## GitHub Action

사용자 저장소에서는 API Secret 없이 Action을 사용할 수 있습니다.

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

최근 커밋을 기준으로 원본 README를 자동 감지하려면 `from: en`을 제거하면 됩니다.

## 비용 구조

`readme-bilingual`은 OpenAI, Anthropic, Gemini, DeepL 또는 다른 유료 번역 API를 호출하지 않으므로 AI API 비용은 발생하지 않습니다.

GitHub-hosted Actions 사용량은 저장소 소유자의 GitHub 요금제 정책을 별도로 따릅니다. 과금 가능성까지 완전히 없애려면 로컬 CLI 또는 self-hosted runner를 사용하면 됩니다.

## 테스트

```bash
npm test
```

단위 테스트에서는 번역 모델을 다운로드하지 않습니다.

## 라이선스

프로젝트 코드는 MIT입니다. 번역 모델은 각자 별도의 라이선스를 가지므로 재배포 또는 상업적 사용 전 해당 모델 카드를 확인해야 합니다.

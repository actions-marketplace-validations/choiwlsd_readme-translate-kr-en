#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


LANGUAGES = {
    "en-to-ko": {
        "model": "NHNDQ/nllb-finetuned-en2ko",
        "source": "eng_Latn",
        "target": "kor_Hang",
    },
    "ko-to-en": {
        "model": "NHNDQ/nllb-finetuned-ko2en",
        "source": "kor_Hang",
        "target": "eng_Latn",
    },
}


FENCE_RE = re.compile(r"^\s*(```|~~~)")
HTML_ONLY_RE = re.compile(r"^\s*<[^>]+>\s*$")
SEPARATOR_RE = re.compile(r"^\s*[:\-| ]+\s*$")
REFERENCE_DEFINITION_RE = re.compile(
    r'^\s{0,3}\[[^\]\n]+\]:\s*\S+(?:\s+(?:["\'(].*["\')]|\S.*))?\s*$'
)

INLINE_TOKEN_RE = re.compile(
    r"(`[^`\n]+`|"
    r"!?\[[^\]\n]*\]\[[^\]\n]*\]|"
    r"!?\[[^\]\n]*\]\([^()\n]*(?:\([^()\n]*\)[^()\n]*)*\)|"
    r"https?://[^\s<>]+|"
    r"www\.\S+|"
    r"<(?:https?://|mailto:)[^>]+>|"
    r"<[^>\n]+>|"
    r"(?:\*\*|__|~~|(?<!\*)\*(?!\*)|(?<!_)_(?!_))|"
    r"(?:[\U0001F1E6-\U0001F1FF]{2}|"
    r"[\U0001F300-\U0001FAFF\u2600-\u27BF]"
    r"(?:\uFE0F|\uFE0E)?(?:\u200D[\U0001F300-\U0001FAFF\u2600-\u27BF]"
    r"(?:\uFE0F|\uFE0E)?)*))"
)

PREFIX_RE = re.compile(
    r"^(\s*(?:"
    r"#{1,6}\s+|"
    r"[-*+]\s+|"
    r"\d+[.)]\s+|"
    r">\s+|"
    r"\[[ xX]\]\s+"
    r")?)(.*)$"
)


def split_inline(text):
    """Split text from markup that must never reach the model."""
    pieces = []
    cursor = 0

    for match in INLINE_TOKEN_RE.finditer(text):
        if match.start() > cursor:
            append_text_piece(pieces, text[cursor:match.start()])

        pieces.append((False, match.group(0)))
        cursor = match.end()

    if cursor < len(text):
        append_text_piece(pieces, text[cursor:])

    return pieces


def append_text_piece(pieces, value):
    # Punctuation, spacing, and dates do not need translation.
    should_translate = bool(re.search(r"[A-Za-z가-힣]", value))
    pieces.append((should_translate, value))


def rebuild_inline(pieces, translated_iter):
    output = []

    for should_translate, value in pieces:
        output.append(
            next(translated_iter)
            if should_translate
            else value
        )

    return "".join(output)


def split_markdown(markdown):
    segments = []
    in_fence = False
    in_frontmatter = False
    in_html_comment = False

    for line_number, line in enumerate(
        markdown.splitlines(keepends=True)
    ):
        raw = line.rstrip("\r\n")
        newline = line[len(raw):]

        # Preserve complete HTML comments, including multiline examples.
        if in_html_comment or "<!--" in raw:
            segments.append((False, raw, newline, ""))

            if "<!--" in raw and "-->" not in raw:
                in_html_comment = True

            if in_html_comment and "-->" in raw:
                in_html_comment = False

            continue

        # Preserve YAML front matter at the start of a document.
        if line_number == 0 and raw.strip() == "---":
            in_frontmatter = True
            segments.append((False, raw, newline, ""))
            continue

        if in_frontmatter:
            segments.append((False, raw, newline, ""))

            if raw.strip() in {"---", "..."}:
                in_frontmatter = False

            continue

        # Fenced code blocks
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            segments.append((False, raw, newline, ""))
            continue

        # Preserve code blocks, blank lines, HTML-only lines,
        # and Markdown separators.
        if (
            in_fence
            or not raw.strip()
            or HTML_ONLY_RE.match(raw)
            or SEPARATOR_RE.match(raw)
            or REFERENCE_DEFINITION_RE.match(raw)
        ):
            segments.append((False, raw, newline, ""))
            continue

        # Markdown tables
        if "|" in raw and raw.count("|") >= 2:
            parts = raw.split("|")
            translated_parts = []

            for part in parts:
                if not part.strip() or SEPARATOR_RE.match(part):
                    translated_parts.append(
                        (False, part, "", "")
                    )
                    continue

                leading = part[: len(part) - len(part.lstrip())]
                trailing = part[len(part.rstrip()):]
                core = part.strip()

                pieces = split_inline(core)

                translated_parts.append(
                    (
                        True,
                        pieces,
                        "",
                        (
                            leading,
                            trailing,
                        ),
                    )
                )

            segments.append(
                (
                    "table",
                    translated_parts,
                    newline,
                    "",
                )
            )

            continue

        # Headings, lists, blockquotes, checkboxes, etc.
        match = PREFIX_RE.match(raw)
        prefix, body = match.groups()

        if not body.strip():
            segments.append((False, raw, newline, ""))
            continue

        leading = body[: len(body) - len(body.lstrip())]
        trailing = body[len(body.rstrip()):]
        core = body.strip()

        pieces = split_inline(core)

        segments.append(
            (
                True,
                pieces,
                newline,
                (
                    prefix + leading,
                    trailing,
                ),
            )
        )

    return segments


def translate_texts(texts, direction, batch_size=4):
    if not texts:
        return []

    try:
        import torch
        from transformers import (
            AutoModelForSeq2SeqLM,
            AutoTokenizer,
        )
    except ImportError as exc:
        raise SystemExit(
            "Local translation dependencies are missing. Run: "
            "python -m pip install -r requirements.txt"
        ) from exc

    language_config = LANGUAGES[direction]

    model_name = language_config["model"]
    source_lang = language_config["source"]
    target_lang = language_config["target"]

    print(
        f"Loading translation model: {model_name}",
        file=sys.stderr,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        src_lang=source_lang,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name
    )

    model.eval()

    target_token_id = tokenizer.convert_tokens_to_ids(
        target_lang
    )

    if target_token_id == tokenizer.unk_token_id:
        raise RuntimeError(
            f"Unknown NLLB target language token: {target_lang}"
        )

    output = []

    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]

            encoded = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            generated = model.generate(
                **encoded,
                forced_bos_token_id=target_token_id,
                max_new_tokens=512,
                num_beams=4,
            )

            translated_batch = tokenizer.batch_decode(
                generated,
                skip_special_tokens=True,
            )

            output.extend(translated_batch)

    return output


def translate_markdown(
    markdown,
    direction,
    translator=translate_texts,
):
    segments = split_markdown(markdown)

    texts = []

    for kind, value, _, _ in segments:
        if kind is True:
            texts.extend(
                piece
                for should_translate, piece in value
                if should_translate
            )

        elif kind == "table":
            for part_kind, part_value, _, _ in value:
                if part_kind:
                    texts.extend(
                        piece
                        for should_translate, piece in part_value
                        if should_translate
                    )

    translated_iter = iter(
        translator(
            texts,
            direction,
        )
    )

    output = []

    for kind, value, newline, meta in segments:
        if kind is False:
            output.append(
                value + newline
            )

        elif kind is True:
            prefix, trailing = meta
            translated = rebuild_inline(value, translated_iter)

            output.append(
                prefix
                + translated
                + trailing
                + newline
            )

        elif kind == "table":
            rebuilt = []

            for (
                part_kind,
                part_value,
                _,
                part_meta,
            ) in value:

                if not part_kind:
                    rebuilt.append(part_value)
                    continue

                leading, trailing = part_meta
                translated = rebuild_inline(
                    part_value,
                    translated_iter,
                )

                rebuilt.append(
                    leading
                    + translated
                    + trailing
                )

            output.append(
                "|".join(rebuilt)
                + newline
            )

    return "".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Translate README Markdown locally."
    )

    parser.add_argument(
        "--direction",
        required=True,
        choices=sorted(LANGUAGES),
    )

    parser.add_argument(
        "--input",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    source = Path(
        args.input
    ).read_text(
        encoding="utf-8"
    )

    translated = translate_markdown(
        source,
        args.direction,
    )

    Path(
        args.output
    ).write_text(
        translated,
        encoding="utf-8",
    )

    language_config = LANGUAGES[
        args.direction
    ]

    print(
        (
            f"Translated with {language_config['model']} "
            f"({language_config['source']} "
            f"-> {language_config['target']})"
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

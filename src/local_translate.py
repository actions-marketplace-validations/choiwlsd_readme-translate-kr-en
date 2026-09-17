#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path

MODEL_NAME = "facebook/nllb-200-distilled-600M"

LANGUAGES = {
    "en-to-ko": {
        "source": "eng_Latn",
        "target": "kor_Hang",
    },
    "ko-to-en": {
        "source": "kor_Hang",
        "target": "eng_Latn",
    },
}

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HTML_ONLY_RE = re.compile(r"^\s*<[^>]+>\s*$")
SEPARATOR_RE = re.compile(r"^\s*[:\-| ]+\s*$")

INLINE_TOKEN_RE = re.compile(
    r"(`[^`\n]+`|"
    r"!?\[[^\]]*\]\([^)]*\)|"
    r"https?://\S+|"
    r"www\.\S+|"
    r"<https?://[^>]+>|"
    r"<[^>\n]+>)"
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


def protect_inline(text):
    protected = []

    def replace(match):
        token = f"__RB_TOKEN_{len(protected)}__"
        protected.append(match.group(0))
        return token

    return INLINE_TOKEN_RE.sub(replace, text), protected


def restore_inline(text, protected):
    for index, value in enumerate(protected):
        token = f"__RB_TOKEN_{index}__"
        text = text.replace(token, value)

    return text


def split_markdown(markdown):
    segments = []
    in_fence = False

    for line in markdown.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        newline = line[len(raw):]

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

                protected_text, protected = protect_inline(core)

                translated_parts.append(
                    (
                        True,
                        protected_text,
                        "",
                        (
                            leading,
                            trailing,
                            protected,
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

        protected_text, protected = protect_inline(core)

        segments.append(
            (
                True,
                protected_text,
                newline,
                (
                    prefix + leading,
                    trailing,
                    protected,
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

    source_lang = language_config["source"]
    target_lang = language_config["target"]

    print(
        f"Loading translation model: {MODEL_NAME}",
        file=sys.stderr,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        src_lang=source_lang,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME
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
            texts.append(value)

        elif kind == "table":
            for part_kind, part_value, _, _ in value:
                if part_kind:
                    texts.append(part_value)

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
            prefix, trailing, protected = meta

            translated = restore_inline(
                next(translated_iter),
                protected,
            )

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

                leading, trailing, protected = part_meta

                translated = restore_inline(
                    next(translated_iter),
                    protected,
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
            f"Translated with {MODEL_NAME} "
            f"({language_config['source']} "
            f"-> {language_config['target']})"
        ),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
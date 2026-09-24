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


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
INDENTED_CODE_RE = re.compile(r"^(?: {4}|\t)\S")
HTML_ONLY_RE = re.compile(r"^\s*<[^>]+>\s*$")
SEPARATOR_RE = re.compile(r"^\s*[:\-| ]+\s*$")
REFERENCE_DEFINITION_RE = re.compile(
    r'^\s{0,3}\[[^\]\n]+\]:\s*\S+(?:\s+(?:["\'(].*["\')]|\S.*))?\s*$'
)

INLINE_TOKEN_RE = re.compile(
    r"((?P<code>`+)[^\n]*?(?P=code)|"
    r"\$\$[^\n$]+\$\$|(?<!\$)\$[^\n$]+\$(?!\$)|"
    r"\[[ xX]\]|\[![A-Z][A-Z0-9_-]*\]|"
    r"(?:\\\||(?<!\\)\|)|"
    r"&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);|"
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
    # Models commonly trim surrounding whitespace. Keep it outside the
    # translated fragment so markup boundaries do not collapse.
    leading = value[: len(value) - len(value.lstrip())]
    trailing = value[len(value.rstrip()):]
    core = value.strip()

    if not core:
        pieces.append((False, value))
        return

    if leading:
        pieces.append((False, leading))

    if core:
        # Punctuation and dates do not need translation.
        should_translate = bool(re.search(r"[A-Za-z가-힣]", core))
        pieces.append((should_translate, core))

    if trailing:
        pieces.append((False, trailing))


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
    fence_marker = None
    in_frontmatter = False
    in_html_comment = False
    in_html_tag = False

    for line_number, line in enumerate(
        markdown.splitlines(keepends=True)
    ):
        raw = line.rstrip("\r\n")
        newline = line[len(raw):]

        if in_html_tag:
            segments.append((False, raw, newline, ""))

            if ">" in raw:
                in_html_tag = False

            continue

        if re.match(r"^\s*<[A-Za-z][^>]*$", raw):
            in_html_tag = True
            segments.append((False, raw, newline, ""))
            continue

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

        # Fenced code blocks. Only the same marker type and an equal or
        # longer run can close a fence.
        fence_match = FENCE_RE.match(raw)

        if fence_marker is not None:
            segments.append((False, raw, newline, ""))

            if fence_match:
                marker, remainder = fence_match.groups()

                if (
                    marker[0] == fence_marker[0]
                    and len(marker) >= len(fence_marker)
                    and not remainder.strip()
                ):
                    fence_marker = None

            continue

        if fence_match:
            fence_marker = fence_match.group(1)
            segments.append((False, raw, newline, ""))
            continue

        # Preserve code blocks, blank lines, HTML-only lines,
        # and Markdown separators.
        if (
            INDENTED_CODE_RE.match(raw)
            or not raw.strip()
            or HTML_ONLY_RE.match(raw)
            or SEPARATOR_RE.match(raw)
            or REFERENCE_DEFINITION_RE.match(raw)
        ):
            segments.append((False, raw, newline, ""))
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

    expanded_texts = []
    owners = []

    for owner, text in enumerate(texts):
        for chunk in chunk_text(text, tokenizer):
            expanded_texts.append(chunk)
            owners.append(owner)

    translated_chunks = []

    with torch.inference_mode():
        for start in range(0, len(expanded_texts), batch_size):
            batch = expanded_texts[start : start + batch_size]

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

            translated_chunks.extend(translated_batch)

    grouped = [[] for _ in texts]

    for owner, translated in zip(owners, translated_chunks):
        grouped[owner].append(translated)

    return [" ".join(chunks) for chunks in grouped]


def chunk_text(text, tokenizer, max_tokens=480):
    """Split long model inputs without silently truncating content."""
    if len(tokenizer.encode(text, add_special_tokens=False)) <= max_tokens:
        return [text]

    words = text.split()
    chunks = []
    current = []

    for word in words:
        candidate = " ".join([*current, word])

        if (
            current
            and len(
                tokenizer.encode(
                    candidate,
                    add_special_tokens=False,
                )
            ) > max_tokens
        ):
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))

    if any(
        len(tokenizer.encode(chunk, add_special_tokens=False)) > max_tokens
        for chunk in chunks
    ):
        raise RuntimeError(
            "A single README token exceeds the translation model's "
            "input limit. Break the long token into smaller text."
        )

    return chunks


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

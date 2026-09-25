#!/usr/bin/env python3

import argparse
import difflib
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


def translate_markdown_incremental(
    markdown,
    current_target,
    previous_source,
    previous_generated,
    direction,
    translator=translate_texts,
):
    """Translate changed Markdown elements and preserve current translations."""
    source_lines = markdown.splitlines(keepends=True)
    previous_source_lines = previous_source.splitlines(keepends=True)
    previous_generated_lines = previous_generated.splitlines(keepends=True)
    current_target_lines = current_target.splitlines(keepends=True)
    segments = split_markdown(markdown)

    if (
        len(segments) != len(source_lines)
        or len(previous_source_lines) != len(previous_generated_lines)
    ):
        translated = translate_markdown(markdown, direction, translator)
        return translated, translated

    source_map = unchanged_line_map(
        previous_source_lines,
        source_lines,
    )
    current_chunks = map_edited_target(
        previous_generated_lines,
        current_target_lines,
    )

    texts = []

    for index, (kind, value, _, _) in enumerate(segments):
        if index in source_map or kind is not True:
            continue

        texts.extend(
            piece
            for should_translate, piece in value
            if should_translate
        )

    translated_iter = iter(
        translator(texts, direction) if texts else []
    )
    output = []
    generated = []

    for index, (kind, value, newline, meta) in enumerate(segments):
        previous_index = source_map.get(index)

        if previous_index is not None:
            output.append(current_chunks[previous_index])
            generated.append(previous_generated_lines[previous_index])
            continue

        if kind is False:
            translated_line = value + newline
        else:
            prefix, trailing = meta
            translated_line = (
                prefix
                + rebuild_inline(value, translated_iter)
                + trailing
                + newline
            )

        output.append(translated_line)
        generated.append(translated_line)

    return "".join(output), "".join(generated)


def unchanged_line_map(previous_lines, current_lines):
    """Map current line indexes to identical lines in the previous source."""
    matcher = difflib.SequenceMatcher(
        None,
        previous_lines,
        current_lines,
        autojunk=False,
    )
    mapping = {}

    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if tag != "equal":
            continue

        for offset in range(new_end - new_start):
            mapping[new_start + offset] = old_start + offset

    return mapping


def map_edited_target(previous_generated_lines, current_target_lines):
    """Attach current target edits to their previous generated elements."""
    chunks = [None] * len(previous_generated_lines)
    matcher = difflib.SequenceMatcher(
        None,
        previous_generated_lines,
        current_target_lines,
        autojunk=False,
    )

    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        old_count = old_end - old_start
        new_count = new_end - new_start

        if tag == "equal":
            for offset in range(old_count):
                chunks[old_start + offset] = current_target_lines[new_start + offset]
            continue

        if tag == "replace" and old_count == new_count:
            for offset in range(old_count):
                chunks[old_start + offset] = current_target_lines[new_start + offset]
            continue

        if tag in {"replace", "delete"} and old_count:
            chunks[old_start] = "".join(current_target_lines[new_start:new_end])

            for index in range(old_start + 1, old_end):
                chunks[index] = ""

            continue

        if tag == "insert" and new_count:
            inserted = "".join(current_target_lines[new_start:new_end])

            if old_start > 0:
                anchor = old_start - 1
                chunks[anchor] = (chunks[anchor] or previous_generated_lines[anchor]) + inserted
            elif chunks:
                chunks[0] = inserted + (chunks[0] or previous_generated_lines[0])

    return [
        previous_generated_lines[index] if chunk is None else chunk
        for index, chunk in enumerate(chunks)
    ]


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

    parser.add_argument("--current-target")
    parser.add_argument("--previous-source")
    parser.add_argument("--previous-generated")
    parser.add_argument("--generated-output")

    args = parser.parse_args()

    source = Path(
        args.input
    ).read_text(
        encoding="utf-8"
    )

    incremental_paths = [
        args.current_target,
        args.previous_source,
        args.previous_generated,
        args.generated_output,
    ]

    if any(incremental_paths) and not all(incremental_paths):
        parser.error(
            "incremental translation requires --current-target, "
            "--previous-source, --previous-generated, and "
            "--generated-output"
        )

    if all(incremental_paths):
        current_target = Path(args.current_target).read_text(encoding="utf-8")
        previous_source = Path(args.previous_source).read_text(encoding="utf-8")
        previous_generated = Path(args.previous_generated).read_text(encoding="utf-8")
        translated, generated = translate_markdown_incremental(
            source,
            current_target,
            previous_source,
            previous_generated,
            args.direction,
        )
        Path(args.generated_output).write_text(generated, encoding="utf-8")
    else:
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

import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "src" / "local_translate.py"
spec = importlib.util.spec_from_file_location("local_translate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fake_translate(texts, direction):
    return [f"KO:{text}" for text in texts]


class LocalTranslateTest(unittest.TestCase):
    def test_preserves_code_fences_and_links(self):
        src = "# Hello\n\nVisit [Docs](https://example.com).\n\n```js\nconsole.log('Hello')\n```\n"
        out = mod.translate_markdown(src, "en-to-ko", translator=fake_translate)
        self.assertIn("# KO:Hello", out)
        self.assertIn("[Docs](https://example.com)", out)
        self.assertIn("console.log('Hello')", out)

    def test_preserves_inline_code(self):
        out = mod.translate_markdown("Run `npm test` now.\n", "en-to-ko", translator=fake_translate)
        self.assertIn("`npm test`", out)

    def test_preserves_links_images_badges_and_emoji(self):
        src = (
            "## 🚀 Project **status**\n\n"
            "Visit [Docs](https://example.com/a_(b)) and "
            "[API][api]. ![Build](https://img.shields.io/badge/build-passing-green) ✅\n\n"
            "[api]: https://example.com/api \"API docs\"\n"
        )

        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertIn("🚀", out)
        self.assertIn("✅", out)
        self.assertIn("**KO:status**", out)
        self.assertIn("[Docs](https://example.com/a_(b))", out)
        self.assertIn("[API][api]", out)
        self.assertIn(
            "![Build](https://img.shields.io/badge/build-passing-green)",
            out,
        )
        self.assertIn(
            '[api]: https://example.com/api "API docs"',
            out,
        )

    def test_preserves_yaml_frontmatter(self):
        src = "---\ntitle: Project\ntags: [docs, readme]\n---\n# Hello\n"
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertTrue(out.startswith("---\ntitle: Project\ntags: [docs, readme]\n---\n"))
        self.assertIn("# KO:Hello", out)

    def test_preserves_complete_html_comments(self):
        src = (
            "<!-- Example text must not be translated.\n"
            '<a href="https://example.com">Icon example</a>\n'
            "-->\n"
            "# Hello\n"
        )
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertIn("Example text must not be translated.", out)
        self.assertIn(
            '<a href="https://example.com">Icon example</a>',
            out,
        )
        self.assertIn("# KO:Hello", out)

    def test_never_sends_protected_content_to_translator(self):
        received = []

        def recording_translator(texts, direction):
            received.extend(texts)
            return [f"KO:{text}" for text in texts]

        src = (
            '경희대학교 <a href="https://example.com">디닷컴</a> '
            '회장 <sub>2025. 01.</sub> 🚀\n'
        )
        out = mod.translate_markdown(
            src,
            "ko-to-en",
            translator=recording_translator,
        )

        model_input = "".join(received)
        self.assertNotIn("<a", model_input)
        self.assertNotIn("</a>", model_input)
        self.assertNotIn("<sub>", model_input)
        self.assertNotIn("🚀", model_input)
        self.assertIn('<a href="https://example.com">', out)
        self.assertIn("</a>", out)
        self.assertIn("<sub>2025. 01.</sub>", out)
        self.assertIn("🚀", out)

    def test_preserves_profile_readme_html_structure(self):
        src = (
            "### 🏆 Awards\n"
            '- 경희대학교 <a href="https://thon.khlug.org/" '
            'target="_blank">khuthon</a> '
            "<strong>최우수상</strong> <sub>2025. 05.</sub>\n"
            "### 💌 Contact\n"
            '<p align="center">\n'
            '  <a href="mailto:test@example.com">\n'
            '    <img src="https://example.com/icon.svg" title="Email" />\n'
            "  </a>\n"
            "</p>\n"
        )
        out = mod.translate_markdown(
            src,
            "ko-to-en",
            translator=fake_translate,
        )

        self.assertIn('href="https://thon.khlug.org/"', out)
        self.assertIn('target="_blank"', out)
        self.assertIn("<strong>", out)
        self.assertIn("</strong>", out)
        self.assertIn("<sub>2025. 05.</sub>", out)
        self.assertIn('href="mailto:test@example.com"', out)
        self.assertIn('src="https://example.com/icon.svg"', out)
        self.assertIn("🏆 KO:Awards", out)
        self.assertIn("KO:경희대학교 <a", out)
        self.assertIn("</a> ", out)
        self.assertIn("</strong> <sub>", out)

    def test_preserves_table_pipes_inline_code_and_entities(self):
        received = []

        def recording_translator(texts, direction):
            received.extend(texts)
            return [f"KO:{text}" for text in texts]

        src = (
            "| Name | Example |\n"
            "| --- | --- |\n"
            "| Parser | `left|right` and A\\|B &nbsp; |\n"
        )
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=recording_translator,
        )

        model_input = "".join(received)
        self.assertNotIn("|", model_input)
        self.assertNotIn("&nbsp;", model_input)
        self.assertNotIn("`left|right`", model_input)
        self.assertEqual(src.count("|"), out.count("|"))
        self.assertIn("`left|right`", out)
        self.assertEqual(src.count("\\|"), out.count("\\|"))
        self.assertIn("&nbsp;", out)

    def test_preserves_indented_code(self):
        src = "Example:\n\n    npm install package\n\nAfterward.\n"
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertIn("    npm install package", out)
        self.assertNotIn("KO:npm install package", out)

    def test_preserves_task_alert_math_and_double_backtick_code(self):
        received = []

        def recording_translator(texts, direction):
            received.extend(texts)
            return [f"KO:{text}" for text in texts]

        src = (
            "- [x] Completed task\n"
            "> [!NOTE]\n"
            "> Formula $E = mc^2$ uses ``code with ` tick``.\n"
        )
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=recording_translator,
        )

        model_input = "".join(received)
        self.assertNotIn("[x]", model_input)
        self.assertNotIn("[!NOTE]", model_input)
        self.assertNotIn("$E = mc^2$", model_input)
        self.assertNotIn("``code with ` tick``", model_input)
        self.assertIn("- [x] ", out)
        self.assertIn("> [!NOTE]", out)
        self.assertIn("$E = mc^2$", out)
        self.assertIn("``code with ` tick``", out)

    def test_does_not_close_backtick_fence_with_tildes(self):
        src = "```text\n~~~\nstill code\n```\n# Hello\n"
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertIn("~~~\nstill code\n```", out)
        self.assertNotIn("KO:still code", out)
        self.assertIn("# KO:Hello", out)

    def test_preserves_multiline_html_tag(self):
        src = (
            "<img\n"
            '  src="https://example.com/icon.svg"\n'
            '  alt="Project icon"\n'
            ">\n"
            "# Hello\n"
        )
        out = mod.translate_markdown(
            src,
            "en-to-ko",
            translator=fake_translate,
        )

        self.assertIn('alt="Project icon"', out)
        self.assertNotIn('alt="KO:Project icon"', out)
        self.assertIn("# KO:Hello", out)

    def test_chunks_long_text_without_truncation(self):
        class WordTokenizer:
            @staticmethod
            def encode(text, add_special_tokens=False):
                return text.split()

        text = " ".join(f"word{index}" for index in range(25))
        chunks = mod.chunk_text(text, WordTokenizer(), max_tokens=10)

        self.assertEqual(3, len(chunks))
        self.assertEqual(text.split(), " ".join(chunks).split())
        self.assertTrue(all(len(chunk.split()) <= 10 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()

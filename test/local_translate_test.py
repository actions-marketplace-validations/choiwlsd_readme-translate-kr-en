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
        self.assertIn("**status**", out)
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

    def test_fails_instead_of_dropping_protected_content(self):
        def destructive_translator(texts, direction):
            return ["translated without protected content" for _ in texts]

        with self.assertRaisesRegex(
            RuntimeError,
            "refusing to write a corrupted README",
        ):
            mod.translate_markdown(
                "Keep [Docs](https://example.com).\n",
                "en-to-ko",
                translator=destructive_translator,
            )


if __name__ == "__main__":
    unittest.main()

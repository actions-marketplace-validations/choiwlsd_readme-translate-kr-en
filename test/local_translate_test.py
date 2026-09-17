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


if __name__ == "__main__":
    unittest.main()

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from acto.cli import main, translated_argv


class ActoCliTests(unittest.TestCase):
    def test_commands_translate_to_legacy_compatible_commands(self):
        self.assertEqual(
            translated_argv(["studio", "draft.json", "--headless"]),
            ["author", "draft.json", "--headless"],
        )
        self.assertEqual(
            translated_argv(["review-results", "job", "--domain", "science"]),
            ["review", "job", "--domain", "science"],
        )
        self.assertEqual(
            translated_argv(["review-task", "task"]),
            ["review-task", "task"],
        )

    def test_main_delegates_after_translation(self):
        with patch("acto.cli.harbor_main", return_value=7) as delegated:
            result = main(["test-verifier", "draft.json"])

        self.assertEqual(result, 7)
        delegated.assert_called_once_with(["verifier", "draft.json"])

    def test_help_lists_acto_workflows(self):
        output = StringIO()
        with redirect_stdout(output):
            result = main(["--help"])

        self.assertEqual(result, 0)
        self.assertIn("acto <command>", output.getvalue())
        self.assertIn("review-results", output.getvalue())

    def test_unknown_command_returns_usage_error(self):
        error = StringIO()
        with redirect_stderr(error):
            result = main(["view"])

        self.assertEqual(result, 2)
        self.assertIn("Unknown Acto command", error.getvalue())


if __name__ == "__main__":
    unittest.main()

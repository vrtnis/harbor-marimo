import unittest

from harbor_marimo.tasks import REQUIRED_TASK_FILES, task_template_root


class TaskTemplateTests(unittest.TestCase):
    def test_terminal_bench_science_template_is_complete(self) -> None:
        root = task_template_root()

        self.assertTrue(root.is_dir())
        self.assertTrue(all((root / relative).is_file() for relative in REQUIRED_TASK_FILES))
        self.assertIn("environment_mode = \"separate\"", (root / "task.toml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

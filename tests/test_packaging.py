from pathlib import Path
from types import SimpleNamespace
import unittest

import harbor_marimo
from harbor_marimo.cli import marimo_command


class PackagedAppTests(unittest.TestCase):
    def test_analysis_and_expert_apps_are_inside_the_package(self):
        package = Path(harbor_marimo.__file__).resolve().parent

        self.assertTrue((package / "apps" / "analysis.py").is_file())
        self.assertTrue((package / "apps" / "expert_review.py").is_file())

    def test_view_command_launches_packaged_analysis_app(self):
        args = SimpleNamespace(
            command="view",
            paths=["job"],
            port=None,
            host="127.0.0.1",
            headless=False,
            token=None,
        )

        command = marimo_command(args)

        self.assertEqual(Path(command[-4]).name, "analysis.py")


if __name__ == "__main__":
    unittest.main()

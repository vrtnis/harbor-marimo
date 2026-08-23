from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OptionalDependencyTests(unittest.TestCase):
    def test_coreweave_support_is_opt_in(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        dependencies = project["project"]["dependencies"]
        extras = project["project"]["optional-dependencies"]

        self.assertFalse(any("cwsandbox" in item for item in dependencies))
        self.assertEqual(extras["coreweave"], ["harbor[cwsandbox]>=0.20,<0.21"])


if __name__ == "__main__":
    unittest.main()

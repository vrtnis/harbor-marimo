from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from harbor_marimo.tasks import (
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
    generate_verifier_script,
)


class VerifierGeneratorTests(unittest.TestCase):
    def test_generated_verifier_runs_without_harbor_marimo_imports(self) -> None:
        draft = TaskDraft.create(
            task_name="convergence-check",
            metadata=TaskMetadata(author_name="Expert"),
            brief=ScientificBrief(title="Task", instruction="Report convergence."),
            checks=(
                VerifierCheck(
                    id="chains-converged",
                    type="column_max",
                    artifact="posterior.csv",
                    parameters={"column": "r_hat", "value": 1.01},
                ),
            ),
        )
        source = generate_verifier_script(draft)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "test_verifier.py"
            script.write_text(source, encoding="utf-8")
            artifacts = root / "artifacts"
            artifacts.mkdir()
            (artifacts / "posterior.csv").write_text(
                "parameter,r_hat\nintercept,1.003\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, str(script), str(artifacts)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"passed": true', result.stdout)
        self.assertNotIn("harbor_marimo", source)


if __name__ == "__main__":
    unittest.main()

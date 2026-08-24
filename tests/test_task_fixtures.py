from pathlib import Path
import tempfile
import unittest

from harbor_marimo.tasks import (
    ArtifactContract,
    ArtifactField,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
    VerifierFixture,
    evaluate_fixtures,
    run_fixture_workbench,
)


class VerifierFixtureTests(unittest.TestCase):
    def test_valid_and_invalid_examples_match_expectations(self) -> None:
        draft = TaskDraft.create(
            task_name="posterior-check",
            metadata=TaskMetadata(author_name="Expert"),
            brief=ScientificBrief(title="Task", instruction="Report diagnostics."),
            artifacts=(
                ArtifactContract(
                    path="posterior.csv",
                    format="csv",
                    fields=(ArtifactField("r_hat", "number"),),
                ),
            ),
            checks=(
                VerifierCheck(
                    id="chains-converged",
                    type="column_max",
                    artifact="posterior.csv",
                    parameters={"column": "r_hat", "value": 1.01},
                ),
            ),
            fixtures=(
                VerifierFixture("Oracle", "valid", True),
                VerifierFixture("Non-converged", "invalid", False),
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "valid").mkdir()
            (root / "invalid").mkdir()
            (root / "valid" / "posterior.csv").write_text(
                "parameter,r_hat\na,1.001\n", encoding="utf-8"
            )
            (root / "invalid" / "posterior.csv").write_text(
                "parameter,r_hat\na,1.2\n", encoding="utf-8"
            )

            results = evaluate_fixtures(draft, root)

        self.assertEqual([item.matched for item in results], [True, True])
        self.assertEqual([item.actual_pass for item in results], [True, False])

    def test_workbench_requires_valid_invalid_and_machine_checks(self) -> None:
        draft = TaskDraft.create(
            task_name="incomplete-task",
            metadata=TaskMetadata(author_name="Expert"),
            brief=ScientificBrief(title="Task", instruction="Produce output."),
        )

        report = run_fixture_workbench(draft, Path.cwd())

        self.assertFalse(report.complete)
        self.assertEqual(len(report.requirements), 3)


if __name__ == "__main__":
    unittest.main()

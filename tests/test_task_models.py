import unittest

from harbor_marimo.tasks import (
    ArtifactContract,
    ArtifactField,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
)


class TaskDraftModelTests(unittest.TestCase):
    def test_round_trip_preserves_scientific_contract(self) -> None:
        draft = TaskDraft.create(
            task_name="bayesian-validation",
            metadata=TaskMetadata(
                author_name="Domain Expert",
                domain="mathematical-sciences",
                field="statistics",
                expert_time_estimate_hours=6,
            ),
            brief=ScientificBrief(
                title="Validate Bayesian sampling",
                instruction="Fit the supplied model and report posterior diagnostics.",
            ),
            artifacts=(
                ArtifactContract(
                    path="results/posterior.csv",
                    format="csv",
                    fields=(ArtifactField("r_hat", "number"),),
                ),
            ),
            checks=(
                VerifierCheck(
                    id="chains-converged",
                    type="column_max",
                    artifact="results/posterior.csv",
                    parameters={"column": "r_hat", "value": 1.01},
                ),
            ),
        )

        restored = TaskDraft.from_dict(draft.to_dict())

        self.assertEqual(restored, draft)
        self.assertEqual(restored.checks[0].parameters["value"], 1.01)

    def test_task_name_must_be_kebab_case(self) -> None:
        with self.assertRaisesRegex(ValueError, "kebab-case"):
            TaskDraft.create(
                task_name="Bad Task",
                metadata=TaskMetadata(author_name="Expert"),
                brief=ScientificBrief(title="Task", instruction="Do the work."),
            )


if __name__ == "__main__":
    unittest.main()

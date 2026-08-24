import unittest

from harbor_marimo.tasks import (
    ArtifactContract,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
)
from harbor_marimo.ui import artifact_rows, draft_readiness, task_summary_markdown


class TaskAuthoringUiTests(unittest.TestCase):
    def test_readiness_uses_expert_facing_language(self) -> None:
        draft = TaskDraft.create(
            task_name="protein-fold-check",
            metadata=TaskMetadata(author_name="Dr Expert", domain="biology"),
            brief=ScientificBrief(title="Check protein fold", instruction="Analyze the fold."),
        )

        issues = draft_readiness(draft)

        self.assertIn("Explain why the task matters scientifically.", issues)
        self.assertIn("Define at least one result artifact.", issues)
        self.assertNotIn("Python", " ".join(issues))

    def test_summary_and_artifacts_present_domain_content(self) -> None:
        draft = TaskDraft.create(
            task_name="posterior-check",
            metadata=TaskMetadata(author_name="Expert", domain="statistics"),
            brief=ScientificBrief(
                title="Validate posterior",
                instruction="Fit the model.",
                research_context="The estimate informs a scientific decision.",
            ),
            artifacts=(ArtifactContract(path="results/posterior.csv", format="csv"),),
            checks=(
                VerifierCheck(
                    id="result-exists",
                    type="file_exists",
                    artifact="results/posterior.csv",
                ),
            ),
        )

        self.assertIn("Validate posterior", task_summary_markdown(draft))
        self.assertEqual(artifact_rows(draft)[0]["Format"], "CSV")


if __name__ == "__main__":
    unittest.main()

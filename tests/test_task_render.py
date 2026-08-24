import unittest

from harbor_marimo.tasks import (
    ArtifactContract,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    render_instruction,
    render_task_toml,
)


class TaskRenderingTests(unittest.TestCase):
    def test_renders_outcome_focused_instruction_and_metadata(self) -> None:
        draft = TaskDraft.create(
            task_name="posterior-diagnostics",
            metadata=TaskMetadata(
                author_name="Expert",
                domain="mathematical-sciences",
                field="statistics",
                tags=("bayesian", "sampling"),
            ),
            brief=ScientificBrief(
                title="Posterior diagnostics",
                instruction="Fit the model and report diagnostics.",
                research_context="Reliable posterior inference requires convergence.",
            ),
            artifacts=(
                ArtifactContract(
                    path="results/posterior.csv",
                    format="csv",
                    description="Posterior parameter summary.",
                ),
            ),
        )

        instruction = render_instruction(draft)
        task_toml = render_task_toml(draft)

        self.assertIn("## Scientific context", instruction)
        self.assertIn("`results/posterior.csv`", instruction)
        self.assertNotIn("\ufffd", instruction)
        self.assertIn('artifacts = ["/app/results/posterior.csv"]', task_toml)
        self.assertIn('field = "statistics"', task_toml)
        self.assertIn('environment_mode = "separate"', task_toml)


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import tempfile
import tomllib
import unittest

from acto.profiles import load_review_profile
from acto.tasks import (
    ArtifactContract,
    ScientificBrief,
    TaskDraft,
    TaskMetadata,
    VerifierCheck,
    export_task_bundle,
)


class TaskBundleExportTests(unittest.TestCase):
    def test_exports_harbor_task_and_matching_review_profile(self) -> None:
        draft = TaskDraft.create(
            task_name="posterior-validation",
            metadata=TaskMetadata(
                author_name="Expert",
                domain="mathematical-sciences",
                field="statistics",
            ),
            brief=ScientificBrief(
                title="Posterior validation",
                instruction="Fit the model and report converged posterior estimates.",
            ),
            artifacts=(
                ArtifactContract(path="results/posterior.csv", format="csv"),
            ),
            checks=(
                VerifierCheck(
                    id="chains-converged",
                    type="column_max",
                    artifact="results/posterior.csv",
                    description="Sampling chains converged",
                    parameters={"column": "r_hat", "value": 1.01},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / draft.task_name

            result = export_task_bundle(draft, target)
            task_config = tomllib.loads((target / "task.toml").read_text(encoding="utf-8"))
            profile = load_review_profile(result.review_profile_path)

            self.assertEqual(task_config["verifier"]["environment_mode"], "separate")
            self.assertTrue((target / "tests" / "test_verifier.py").is_file())
            self.assertEqual(profile.acceptance_criteria[0].id, "chains-converged")
            with self.assertRaises(FileExistsError):
                export_task_bundle(draft, target)


if __name__ == "__main__":
    unittest.main()

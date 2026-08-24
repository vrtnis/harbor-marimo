from pathlib import Path
import tempfile
import unittest

from harbor_marimo.profiles import load_review_profile
from harbor_marimo.task_reviews import (
    RubricAssessment,
    RubricStatus,
    TaskReview,
    TaskReviewStore,
    load_task_bundle,
    result_review_command,
)


ROOT = Path(__file__).resolve().parents[1]
TASK = (
    ROOT
    / "examples"
    / "science-task-review"
    / "bayesian-posterior-convergence"
)


class ScienceTaskEndToEndTests(unittest.TestCase):
    def test_task_moves_from_independent_review_to_result_review(self) -> None:
        bundle = load_task_bundle(TASK)
        profile = load_review_profile(bundle.review_profile_path)
        review = TaskReview.create(
            task_name=bundle.task_name,
            task_author=bundle.task_author,
            reviewer="Independent statistician",
            reviewer_role="domain_reviewer",
            verdict="request_changes",
            conflict_declaration="No conflict",
            note="Clarify the supplied model and justify diagnostic thresholds.",
            assessments=(
                RubricAssessment(
                    criterion_id="instruction-clarity",
                    status=RubricStatus.DOES_NOT_MEET,
                    note="The model input is not identified.",
                    evidence_keys=("instruction",),
                ),
            ),
            evidence=bundle.evidence(),
        )

        with tempfile.TemporaryDirectory() as temp:
            review_path = TaskReviewStore(temp).save(review)
            command = result_review_command(bundle, Path(temp) / "harbor-job")

            self.assertTrue(review_path.is_file())
            self.assertEqual(profile.acceptance_criteria[0].id, "posterior-columns")
            self.assertIn(str(bundle.review_profile_path), command)


if __name__ == "__main__":
    unittest.main()

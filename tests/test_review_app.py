import tempfile
import unittest

from harbor_marimo.reviews import (
    CriterionAssessment,
    CriterionStatus,
    EvidenceReference,
    JsonReviewStore,
    record_review,
)


class ReviewApplicationServiceTests(unittest.TestCase):
    def test_record_review_updates_the_current_trial_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            store = JsonReviewStore(temp)
            reference = EvidenceReference(
                key="artifact:model.csv",
                kind="artifact",
                job_id="job-1",
                trial_id="trial-1",
            )

            first, _ = record_review(
                store,
                job_id="job-1",
                trial_id="trial-1",
                domain="science",
                verdict="needs_follow_up",
                evidence=[reference],
            )
            updated, destination = record_review(
                store,
                job_id="job-1",
                trial_id="trial-1",
                domain="science",
                verdict="approve",
                note="Diagnostics now converge.",
                confidence=0.95,
                evidence=[reference],
                criteria=[
                    CriterionAssessment(
                        criterion_id="convergence",
                        status=CriterionStatus.SATISFIED,
                    )
                ],
                follow_up="Archive the validated result.",
            )

            self.assertEqual(updated.review_id, first.review_id)
            self.assertEqual(updated.created_at, first.created_at)
            self.assertEqual(updated.verdict.value, "approve")
            self.assertEqual(updated.criteria[0].criterion_id, "convergence")
            self.assertIn("Archive", updated.follow_up or "")
            self.assertTrue(destination.endswith(".json"))


if __name__ == "__main__":
    unittest.main()

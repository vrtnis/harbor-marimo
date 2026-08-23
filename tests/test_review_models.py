import unittest

from harbor_marimo.reviews import EvidenceReference, ExpertReview, ReviewVerdict


class ExpertReviewModelTests(unittest.TestCase):
    def test_review_round_trip_preserves_evidence(self):
        evidence = EvidenceReference(
            key="artifact:forecast.xlsx",
            kind="artifact",
            job_id="job-1",
            trial_id="trial-1",
            label="Forecast workbook",
            path="artifacts/workspace/forecast.xlsx",
            locator="Forecast!F16",
        )
        review = ExpertReview.create(
            job_id="job-1",
            trial_id="trial-1",
            domain="financial",
            verdict=ReviewVerdict.NEEDS_FOLLOW_UP,
            note="Formula was replaced by a constant.",
            reviewer="expert@example.com",
            confidence=0.9,
            evidence=(evidence,),
        )

        restored = ExpertReview.from_dict(review.to_dict())

        self.assertEqual(restored, review)
        self.assertEqual(restored.evidence[0].locator, "Forecast!F16")

    def test_confidence_is_bounded(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            ExpertReview.create(
                job_id="job-1",
                trial_id="trial-1",
                domain="science",
                verdict="approve",
                confidence=1.1,
            )

    def test_evidence_cannot_point_at_another_trial(self):
        evidence = EvidenceReference(
            key="check-1",
            kind="verifier",
            job_id="job-1",
            trial_id="trial-2",
        )

        with self.assertRaisesRegex(ValueError, "same job and trial"):
            ExpertReview.create(
                job_id="job-1",
                trial_id="trial-1",
                domain="science",
                verdict="reject",
                evidence=(evidence,),
            )


if __name__ == "__main__":
    unittest.main()

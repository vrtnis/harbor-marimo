import unittest

from acto.task_reviews import (
    ReviewerRole,
    RubricAssessment,
    RubricStatus,
    TaskEvidenceReference,
    TaskReview,
    TaskReviewVerdict,
)


class TaskReviewModelTests(unittest.TestCase):
    def test_round_trips_evidence_linked_review(self) -> None:
        evidence = TaskEvidenceReference(
            key="instruction",
            kind="task_file",
            label="Task instruction",
            path="instruction.md",
        )
        review = TaskReview.create(
            task_name="posterior-check",
            task_author="Author",
            reviewer="Independent scientist",
            reviewer_role=ReviewerRole.DOMAIN_REVIEWER,
            verdict=TaskReviewVerdict.REQUEST_CHANGES,
            conflict_declaration="No conflict",
            evidence=(evidence,),
            assessments=(
                RubricAssessment(
                    criterion_id="scientific-validity",
                    status=RubricStatus.UNCERTAIN,
                    note="Threshold needs justification.",
                    evidence_keys=("instruction",),
                ),
            ),
        )

        restored = TaskReview.from_dict(review.to_dict())

        self.assertEqual(restored, review)

    def test_rejects_assessment_with_unknown_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown evidence"):
            TaskReview.create(
                task_name="posterior-check",
                task_author="Author",
                reviewer="Reviewer",
                reviewer_role="domain_reviewer",
                verdict="reject",
                conflict_declaration="No conflict",
                assessments=(
                    RubricAssessment(
                        criterion_id="validity",
                        status=RubricStatus.DOES_NOT_MEET,
                        evidence_keys=("missing",),
                    ),
                ),
            )


if __name__ == "__main__":
    unittest.main()

import unittest

from harbor_marimo.task_reviews import reviewer_assignment_issues


class TaskReviewConflictTests(unittest.TestCase):
    def test_author_cannot_independently_approve_own_task(self) -> None:
        issues = reviewer_assignment_issues(
            task_author="Dr. Ada Expert",
            reviewer="  DR. ADA   EXPERT ",
            reviewer_role="domain_reviewer",
            conflict_declaration="No conflict",
            verdict="approve",
        )

        self.assertTrue(any("task author" in item.lower() for item in issues))

    def test_author_validation_is_allowed_but_not_approval(self) -> None:
        issues = reviewer_assignment_issues(
            task_author="Author",
            reviewer="Author",
            reviewer_role="author_validation",
            conflict_declaration="N/A",
            verdict="approve",
        )

        self.assertEqual(len(issues), 1)
        self.assertIn("not independent approval", issues[0])

    def test_independent_reviewer_without_conflict_can_approve(self) -> None:
        issues = reviewer_assignment_issues(
            task_author="Author",
            reviewer="Reviewer",
            reviewer_role="final_approver",
            conflict_declaration="None",
            verdict="approve",
        )

        self.assertEqual(issues, ())


if __name__ == "__main__":
    unittest.main()

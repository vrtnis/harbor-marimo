import unittest

from harbor_marimo.task_reviews import TASK_REVIEW_RUBRIC, rubric_for_role


class TaskReviewRubricTests(unittest.TestCase):
    def test_rubric_covers_scientific_and_technical_quality(self) -> None:
        ids = {item.id for item in TASK_REVIEW_RUBRIC}

        self.assertIn("domain-correctness", ids)
        self.assertIn("verifier-validity", ids)
        self.assertIn("isolation-and-safety", ids)
        self.assertIn("benchmark-readiness", ids)

    def test_role_focuses_review_without_hiding_author_validation_coverage(self) -> None:
        technical = rubric_for_role("technical_reviewer")
        author = rubric_for_role("author_validation")

        self.assertTrue(all(item.id != "scientific-purpose" for item in technical))
        self.assertEqual(author, TASK_REVIEW_RUBRIC)


if __name__ == "__main__":
    unittest.main()
